from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtNetwork import QHostAddress, QTcpServer, QTcpSocket


class Server(QObject):
    port_in_use_sig = pyqtSignal(bool)
    client_in_out_sig = pyqtSignal(tuple)
    client_replay_sig = pyqtSignal(tuple)

    def __init__(self, parent):
        super().__init__(parent)

        self.tcpServer = None
        self.client_dict = {}
        self.host_name = "Server"
        self.server_ip = "000.000.000.000"
        self.server_port = "0000"
        self.client_replay_sig.connect(self.forwardRecivedMsgToAll)

    def setServerName(self, name):
        self.host_name = name.rstrip().title()

    def setServerIP(self, ip):
        self.server_ip = ip

    def setServerPort(self, port):
        self.server_port = port

    def startServer(self):
        self.tcpServer = QTcpServer()
        address = QHostAddress(self.server_ip) # wireless lan
        PORT = self.server_port
        if not self.tcpServer.listen(address, PORT):
            self.tcpServer.deleteLater()
            self.port_in_use_sig.emit(True)
            return
        self.port_in_use_sig.emit(False)
        self.tcpServer.newConnection.connect(self.client_connection)

    def client_connection(self):
        # connecting individual client to tcp server
        client = self.tcpServer.nextPendingConnection()
        self.clint_communication = _ClientCommunication(self, self.tcpServer, self.host_name, client, self.client_dict)
        self.clint_communication.valid_client_name_sig.connect(self.validClientResult)
        self.clint_communication.client_disconnected_sig.connect(self.client_disconnected)
        self.clint_communication.client_replay_sig.connect(self.clientReplay)

    def validClientResult(self, result):
        if result[0]:
            self.client_dict[result[2]] = result[1]

            self.clientInOutNotify(('in', result[2]))
            self.updateJoinedClientsToNewClient(result[2])

    def client_disconnected(self, disconnected_client):
        self.client_dict.pop(disconnected_client)
        self.clientInOutNotify(('out', disconnected_client))

    def getClientsList(self):
        return self.client_dict

    def sentMsgToAll(self, msg):
        for client in self.client_dict.values():
            client.write(bytes(str(msg).rstrip()+"**e", encoding='ascii'))

    def clientReplay(self, client_msg):
        self.client_replay_sig.emit(client_msg)

    def forwardRecivedMsgToAll(self, client_msg):
        for client in self.client_dict:
            if client != client_msg[0]:
                self.client_dict[client].write(bytes(str(client_msg).rstrip()+"**e", encoding='ascii'))

    def clientInOutNotify(self, client_in_or_out):
        self.client_in_out_sig.emit(client_in_or_out) # to host, to add new client to list

        # to old clients, to add new client to list
        for client in self.client_dict:
            if client != client_in_or_out[1]:
                self.client_dict[client].write(bytes(str(("*clientIO*", client_in_or_out)).rstrip()+"**e", encoding='ascii'))
            
    def updateJoinedClientsToNewClient(self, client_name):
        # to new client, to update old client list
        self.client_dict[client_name].write(bytes(str(("*clientIO*", ('in', f"{self.host_name} (HOST)"))).rstrip()+"**e", encoding='ascii')) # add host
        for client in self.client_dict:
            if client != client_name:
                self.client_dict[client_name].write(bytes(str(("*clientIO*", ('in', client))).rstrip()+"**e", encoding='ascii'))


class _ClientCommunication(QObject):
    valid_client_name_sig = pyqtSignal(tuple)
    client_disconnected_sig = pyqtSignal(str)
    client_replay_sig = pyqtSignal(tuple)

    def __init__(self, parent, server, host_name, client: QTcpSocket, client_dict):
        super().__init__(parent)

        self.tcpServer = server
        self.host_name = host_name
        self.client = client
        self.client_dict = client_dict
        self.client_name = None
        self.dealCommunication()

    def validateClientName(self, client_replay):
        client_replay = client_replay.rstrip().title()
        invalid_name = False
        if client_replay.lower() == self.host_name.lower():
            invalid_name = True
            self.client.write(bytes(str(("Server", f"Connection status: Failed\n\t'{client_replay}' is host name, please join using another name\nNOTE:\n\tThis message is from server not from host")).rstrip()+"**e", encoding='ascii'))
        elif client_replay.lower() == 'server':
            invalid_name = True
            self.client.write(bytes(str(("Server", f"Connection status: Failed\n\tDo not set your name as 'server', please join using another name\nNOTE:\n\tThis message is from server not from host")).rstrip()+"**e", encoding='ascii'))
        elif client_replay.lower().endswith('host') or client_replay.lower().endswith('(host)'):
            invalid_name = True
            self.client.write(bytes(str(("Server", f"Connection status: Failed\n\tDo not end your name with 'host', please join using another name\nNOTE:\n\tThis message is from server not from host")).rstrip()+"**e", encoding='ascii'))
        elif self.client_dict.get(client_replay, 0):
            invalid_name = True
            self.client.write(bytes(str(("Server", f"Connection status: Failed\n\t'{client_replay}' name already exits, please join using another name\nNOTE:\n\tThis message is from server not from host")).rstrip()+"**e", encoding='ascii'))

        if invalid_name:
            self.client.waitForBytesWritten(200)
            self.client.disconnectFromHost()
            self.client.deleteLater()
            self.valid_client_name_sig.emit((False,))
        else: # valid
            self.client_name = client_replay
            self.client.write(bytes(str(("Server", f"Connection status: Connected\nWelcome {self.client_name}, \n\tYou successfully made connection to {self.host_name}(Host)\nNOTE:\n\tThis message is from server not from host")).rstrip()+"**e", encoding='ascii'))

            # client disconnection signal
            self.client.disconnected.connect(self.dealDisconnection)
            self.valid_client_name_sig.emit((True, self.client, self.client_name))

    def dealCommunication(self):
        # ready to read connection
        self.client.readyRead.connect(self.getClientReplay)

    def dealDisconnection(self):
        # get the connection ready for clean up
        self.client_disconnected_sig.emit(self.client_name)
        self.client.deleteLater()

    def getClientReplay(self):
        # read incomming data
        client_replay = str(self.client.readAll(), encoding='ascii')
        if self.client_name != None:
            self.client_replay_sig.emit((self.client_name, client_replay))
        else: self.validateClientName(client_replay)