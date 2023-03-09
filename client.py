from PyQt5.QtCore import QIODevice, QObject, pyqtSignal, QTimer
from PyQt5.QtNetwork import QTcpSocket, QAbstractSocket

class Client(QObject):
    host_disconnected_sig = pyqtSignal(tuple)
    connection_error_sig = pyqtSignal(tuple)
    connected_sig = pyqtSignal(tuple)
    timeout_sig = pyqtSignal(tuple)
    client_in_out_sig = pyqtSignal(tuple)
    server_replay_sig = pyqtSignal(tuple)

    def __init__(self, parent):
        super().__init__(parent)

        self.tcpSocket = QTcpSocket()
        self.ip = "000.000.000.000"
        self.port = "0000"
        self.client_name = "Client"

        self.conn_timer = QTimer()
        self.conn_timer.timeout.connect(self.checkConnection)
        self.conn_timer_count = 0

    def setClientName(self, name):
        self.client_name = name.rstrip().title()

    def setHostIP(self, ip):
        self.ip = ip # wireless lan

    def setHostPort(self, port):
        self.port = port

    def startUpMsgToServer(self):
        self.tcpSocket.write(bytes(self.client_name, encoding='ascii'))
        self.tcpSocket.readyRead.connect(self.recivedMsg)

    def startClient(self):
        self.conn_timer.start(1200)

    def checkConnection(self):
        self.tcpSocket.connectToHost(self.ip, self.port, QIODevice.OpenModeFlag.ReadWrite)
        if self.tcpSocket.waitForConnected(200):
            self.hostFounded()
        elif self.conn_timer_count == 15:
            self.conn_timer_count = 0
            self.timeout_sig.emit(('host_timeout',))
        self.conn_timer_count+=1

    def hostFounded(self):
        self.conn_timer.stop()
        self.startUpMsgToServer()
        self.connected_sig.emit(('connected',))

    def recivedMsg(self):
        # read incomming data
        server_replay = str(self.tcpSocket.readAll(), encoding='ascii')
        for msg_chunk in server_replay.rstrip("**e").split("**e"):
            if msg_chunk.rstrip():
                msg = eval(msg_chunk)
                if msg[0] == '*clientIO*': # for client in out 
                    self.client_in_out_sig.emit(msg[1])
                else:
                    if msg[0] == 'Server' and msg[1].startswith("Connection status: Connected"):
                        self.tcpSocket.error.connect(self.displayError)
                    self.server_replay_sig.emit(msg)

    def displayError(self, socketError):
        if socketError == QAbstractSocket.SocketError.RemoteHostClosedError:
            self.host_disconnected_sig.emit(("host_disconnected",))
        else:
            self.connection_error_sig.emit(('error', self.tcpSocket.errorString()))
            #print(self, "The following error occurred: %s." % self.tcpSocket.errorString())

    def sentMsg(self, msg):
        self.tcpSocket.write(bytes(msg, encoding='ascii'))