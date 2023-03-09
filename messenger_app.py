from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

from server import Server
from client import Client

# painter render hints
RENDER_HINTS = (
    QPainter.RenderHint.Antialiasing
    | QPainter.RenderHint.HighQualityAntialiasing
    | QPainter.RenderHint.SmoothPixmapTransform
    | QPainter.RenderHint.LosslessImageRendering
    | QPainter.RenderHint.Qt4CompatiblePainting
    | QPainter.RenderHint.NonCosmeticDefaultPen
    | QPainter.RenderHint.TextAntialiasing
)

# Basic empty window creating
class MainWindow(QMainWindow):
    client_in_out_sig = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Server")
        self.variables()
        self.setUpUI()

    def variables(self):
        self.ip = '000.000.000.000'
        self.port = '0000'
        self.name = 'null'
        self.send_msg = None

    def setUpUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_glayout = QGridLayout()
        self.main_left_vlayout = QVBoxLayout()
        self.main_glayout.addLayout(self.main_left_vlayout, 0, 0)
        self.main_right_vlayout = QVBoxLayout()
        self.main_glayout.addLayout(self.main_right_vlayout, 0, 1)
        main_widget.setLayout(self.main_glayout)

        self.font_ = QFont("Consolas", 0, 0, True)

        self.ServerOrClientFrame()
        self.connectionFrame()
        self.serverOrClientStatusFrame()
        self.connectedClintsListFrame()
        self.msgDisplayFrame()

    # to choose use as server or client
    def ServerOrClientFrame(self):
        self.font_.setPixelSize(15)

        frame = QFrame()
        frame.setFixedWidth(400)
        frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shape.Panel)
        self.main_left_vlayout.addWidget(frame, 0, Qt.AlignmentFlag.AlignCenter)

        glayout = QGridLayout()
        frame.setLayout(glayout)

        self.sr_btn = QRadioButton()
        self.sr_btn.setChecked(1)
        self.sr_btn.setFont(self.font_)
        self.sr_btn.setText("Use as server")
        self.sr_btn.toggled.connect(lambda: self.setServerOrClient(self.sr_btn))
        glayout.addWidget(self.sr_btn, 0, 0, Qt.AlignmentFlag.AlignLeft)

        self.cl_btn = QRadioButton()
        self.cl_btn.setFont(self.font_)
        self.cl_btn.setText("Use as client")
        self.cl_btn.toggled.connect(lambda: self.setServerOrClient(self.cl_btn))
        glayout.addWidget(self.cl_btn, 0, 1, Qt.AlignmentFlag.AlignRight)

        self.sr_or_cl_lbl = QLabel("Setted as: server")
        self.sr_or_cl_lbl.setFont(self.font_)
        glayout.addWidget(self.sr_or_cl_lbl, 1, 0, Qt.AlignmentFlag.AlignLeft)

        self.sr_or_cl_confrim_btn = QPushButton("Confrim setting")
        self.sr_or_cl_confrim_btn.setFont(self.font_)
        self.sr_or_cl_confrim_btn.clicked.connect(self.serverOrClientConfrim)
        glayout.addWidget(self.sr_or_cl_confrim_btn, 1, 1, Qt.AlignmentFlag.AlignRight)

    def setServerOrClient(self, btn: QRadioButton):
        if "server" in btn.text():
            if btn.isChecked():
                self.setWindowTitle("Server")
                self.sr_or_cl_lbl.setText("Setted as: server")
                self.cl_btn.setChecked(0)

        elif "client" in btn.text():
            if btn.isChecked():
                self.setWindowTitle("Client")
                self.sr_or_cl_lbl.setText("Setted as: client")
                self.sr_btn.setChecked(0)

        self.status_lbl.setText("Session opened in:" if self.sr_btn.isChecked()==1 else "Client listening to:")
        self.sr_or_cl_name_le.setPlaceholderText("Enter "+("server" if self.sr_btn.isChecked()==1 else "client")+" name")
        self.sr_or_cl_name.setText(("Server " if self.sr_btn.isChecked()==1 else "Client ")+"name: "+self.name)
        self.sr_or_cl_activate_btn.setText("Activate server" if self.sr_btn.isChecked()==1 else "Connect host")
        self.start_indicate_lbl.setText(("Server " if self.sr_btn.isChecked()==1 else "Client ")+"state: In-active")
        
    def serverOrClientConfrim(self):
        self.sr_btn.setDisabled(1)
        self.cl_btn.setDisabled(1)
        self.sr_or_cl_confrim_btn.setDisabled(1)
        self.connection_frame.setDisabled(0)

        if self.sr_btn.isChecked():
            self.server = Server(self)

        elif self.cl_btn.isChecked():
            self.client = Client(self)

    # connection setting frame
    def connectionFrame(self):
        self.font_.setPixelSize(15)

        self.connection_frame = QFrame()
        self.connection_frame.setDisabled(1)
        self.connection_frame.setFixedWidth(300)
        self.connection_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shape.Panel)
        self.main_right_vlayout.addWidget(self.connection_frame, 0, Qt.AlignmentFlag.AlignCenter)

        glayout = QGridLayout()
        self.connection_frame.setLayout(glayout)

        ip_lbl = QLabel("Enter WLAN IP: ")
        ip_lbl.setFont(self.font_)

        self.ip_le = QLineEdit()
        self.ip_le.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ip_le.setFont(self.font_)
        self.ip_le.setInputMask("000.000.000.000;-")

        ip_form = QFormLayout()
        ip_form.setContentsMargins(0, 0, 0, 0)
        ip_form.addRow(ip_lbl, self.ip_le)
        ip_wig = QWidget()
        ip_wig.setLayout(ip_form)
        glayout.addWidget(ip_wig, 0, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)

        port_lbl = QLabel("Enter port: ")
        port_lbl.setFont(self.font_)

        self.port_le = QLineEdit()
        self.port_le.setFixedWidth(QFontMetrics(self.font_).width('00000'))
        self.port_le.setFont(self.font_)
        self.port_le.setInputMask("0000;-")

        port_form = QFormLayout()
        port_form.setContentsMargins(0, 0, 0, 0)
        port_form.addRow(port_lbl, self.port_le)
        port_wig = QWidget()
        port_wig.setLayout(port_form)
        glayout.addWidget(port_wig, 1, 0, Qt.AlignmentFlag.AlignLeft)

        self.ip_port_ok_btn = QPushButton("Set IP and Port")
        self.ip_port_ok_btn.setFont(self.font_)
        self.ip_port_ok_btn.clicked.connect(self.setIPPort)
        glayout.addWidget(self.ip_port_ok_btn, 1, 1, Qt.AlignmentFlag.AlignLeft)

        self.sr_or_cl_name_le = QLineEdit()
        self.sr_or_cl_name_le.setFont(self.font_)
        self.sr_or_cl_name_le.setPlaceholderText("Enter "+("server" if self.sr_btn.isChecked()==1 else "client")+" name")

        sr_or_cl_name_btn = QPushButton("Set name")
        sr_or_cl_name_btn.setFont(self.font_)
        sr_or_cl_name_btn.clicked.connect(self.setName)

        sr_or_cl_name_form = QFormLayout()
        sr_or_cl_name_form.setContentsMargins(0, 0, 0, 0)
        sr_or_cl_name_form.addRow(self.sr_or_cl_name_le, sr_or_cl_name_btn)
        sr_or_cl_name_wig = QWidget()
        sr_or_cl_name_wig.setLayout(sr_or_cl_name_form)
        glayout.addWidget(sr_or_cl_name_wig, 2, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)

    def setIPPort(self):
        try:
            self.ip = '.'.join(map(str, map(int, self.ip_le.text().split('.'))))
            port = self.port_le.text()
            if port.isdigit():
                self.port = int(port)

            self.ip_port_lbl.setText("IP->"+self.ip+"\n"+"Port->"+str(self.port))
        except: pass

    def setName(self):
        self.name = self.sr_or_cl_name_le.text()
        self.sr_or_cl_name.setText(("Server " if self.sr_btn.isChecked()==1 else "Client ")+"name: "+self.name)
        if self.ip != "000.000.000.000" and self.port != "0000" and self.name:
            self.connection_frame.setDisabled(1)
            self.sr_or_cl_status_frame.setDisabled(0)

    # display server or client status
    def serverOrClientStatusFrame(self):
        self.font_.setPixelSize(15)

        self.sr_or_cl_status_frame = QFrame()
        self.sr_or_cl_status_frame.setDisabled(1)
        self.sr_or_cl_status_frame.setFixedWidth(300)
        self.sr_or_cl_status_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shape.Panel)
        self.main_right_vlayout.addWidget(self.sr_or_cl_status_frame, 0, Qt.AlignmentFlag.AlignCenter)

        glayout = QGridLayout()
        self.sr_or_cl_status_frame.setLayout(glayout)

        self.status_lbl = QLabel()
        self.status_lbl.setText("Session opened in:" if self.sr_btn.isChecked()==1 else "Client listening to:")
        self.status_lbl.setFont(self.font_)
        glayout.addWidget(self.status_lbl, 0, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)

        self.ip_port_lbl = QLabel("IP->"+self.ip+"\n"+"Port->"+str(self.port))
        self.ip_port_lbl.setFont(self.font_)
        glayout.addWidget(self.ip_port_lbl, 1, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)

        self.sr_or_cl_name = QLabel()
        self.sr_or_cl_name.setText(("Server " if self.sr_btn.isChecked()==1 else "Client ")+"name: "+self.name)
        self.sr_or_cl_name.setFont(self.font_)
        glayout.addWidget(self.sr_or_cl_name, 2, 0, Qt.AlignmentFlag.AlignLeft)

        self.sr_or_cl_activate_btn = QPushButton("Activate server" if self.sr_btn.isChecked()==1 else "Connect host")
        self.sr_or_cl_activate_btn.setFont(self.font_)
        self.sr_or_cl_activate_btn.clicked.connect(self.start)
        glayout.addWidget(self.sr_or_cl_activate_btn, 2, 1, Qt.AlignmentFlag.AlignCenter)

        self.start_indicate_lbl = QLabel()
        self.start_indicate_lbl.setText(("Server " if self.sr_btn.isChecked()==1 else "Client ")+"state: In-active")
        self.start_indicate_lbl.setFont(self.font_)
        glayout.addWidget(self.start_indicate_lbl, 3, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)

    # start server or client
    def start(self):
        self.sr_or_cl_status_frame.setDisabled(1)
        self.connection_frame.setDisabled(1)
        
        if self.sr_btn.isChecked():
            self.serverOperations()
        elif self.cl_btn.isChecked():
            self.clientOperations()

        self.start_indicate_lbl.setText(("Server " if self.sr_btn.isChecked()==1 else "Client ")+"state: Active")
        self.client_in_out_sig.connect(self.toast)

    # server operation
    def serverOperations(self):
        self.server.setServerName(self.name)
        self.server.setServerIP(self.ip)
        self.server.setServerPort(self.port)

        self.send_msg = self.server.sentMsgToAll

        self.server.port_in_use_sig.connect(self.portInUse)
        self.server.startServer()

        self.msg_send_btn.setDisabled(0)
        self.msg_te.setDisabled(0)
    
    # client operation
    def clientOperations(self):
        self.client.setClientName(self.name)
        self.client.setHostIP(self.ip)
        self.client.setHostPort(self.port)

        self.send_msg = self.client.sentMsg
        self.toast(('connecting',))

        self.client.host_disconnected_sig.connect(self.toast)
        self.client.connection_error_sig.connect(self.toast)
        self.client.connected_sig.connect(self.toast)
        self.client.timeout_sig.connect(self.toast)
        self.client.client_in_out_sig.connect(self.updateClientList)
        self.client.startClient()
        self.client.server_replay_sig.connect(self.recivedMsg)

    # to check if given port in use for server side only
    def portInUse(self, state):
        self.toast(('port_in_use', state))
        self.server.port_in_use_sig.disconnect()
        try: self.client_in_out_sig.disconnect()
        except: pass
        if state:
            self.connection_frame.setDisabled(0)
            self.sr_or_cl_status_frame.setDisabled(0)
        else:
            self.server.client_in_out_sig.connect(self.updateClientList)
            self.server.client_replay_sig.connect(self.recivedMsg)

    # display connected clients includeing host
    def connectedClintsListFrame(self):
        self.font_.setPixelSize(15)

        frame = QFrame()
        frame.setFixedWidth(300)
        frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shape.Panel)
        self.main_right_vlayout.addWidget(frame, 0, Qt.AlignmentFlag.AlignCenter)

        glayout = QGridLayout()
        frame.setLayout(glayout)

        hedding_lbl = QLabel("Conected clients")
        hedding_lbl.setFont(self.font_)
        glayout.addWidget(hedding_lbl)

        self.connected_clients = QListWidget()
        glayout.addWidget(self.connected_clients)

    # update list when client connected or disconnected
    def updateClientList(self, client):
        if client[1] != '(HOST)':
            self.client_in_out_sig.emit(client)

        if client[0] == 'in':
            item = QListWidgetItem()
            item.setText(client[1])
            item.setFlags(Qt.ItemFlag.ItemIsUserTristate)

            line_text = QLabel(client[1])
            line_text.setFont(self.font_)
            line_text.setStyleSheet("background: white; border-bottom: 1px solid black")
            item.setSizeHint(line_text.sizeHint())

            self.connected_clients.addItem(item)
            self.connected_clients.setItemWidget(item, line_text)
        
        elif client[0] == 'out':
            for idx in range(self.connected_clients.count()):
                if self.connected_clients.item(idx).text() == client[1] or self.connected_clients.item(idx).text().endswith(client[1]):
                    self.connected_clients.takeItem(idx)
                    break
    
    # display session all message
    def msgDisplayFrame(self):
        self.font_.setPixelSize(15)

        self.msg_display_frame = QFrame()
        self.msg_display_frame.setContentsMargins(0, 0, 0, 0)
        self.msg_display_frame.setFixedSize(self.size()-self.main_left_vlayout.sizeHint()+QSize(0, 30))
        self.msg_display_frame.setFixedWidth(400)
        self.msg_display_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shape.Panel)
        self.main_left_vlayout.addWidget(self.msg_display_frame, 0, Qt.AlignmentFlag.AlignCenter)

        glayout = QGridLayout()
        glayout.setContentsMargins(0, 0, 0, 0)
        self.msg_display_frame.setLayout(glayout)

        hedding_lbl = QLabel("Chat box")
        hedding_lbl.setContentsMargins(0, 6, 0, 0)
        hedding_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hedding_lbl.setFont(self.font_)
        glayout.addWidget(hedding_lbl, 0, 0)

        self.msg_display = QListWidget()
        glayout.addWidget(self.msg_display, 1, 0)

        self.msg_send_btn = QPushButton("Send")
        self.msg_send_btn.setFixedWidth(90)
        self.msg_send_btn.setFixedHeight(50)
        self.msg_send_btn.setFont(self.font_)
        self.msg_send_btn.clicked.connect(self.sendMsg)
        self.msg_send_btn.setDisabled(1)

        self.msg_te = QTextEdit()
        self.msg_te.setFixedWidth(self.msg_display_frame.width()-self.msg_send_btn.width()-8)
        self.msg_te.setFixedHeight(50)
        self.msg_te.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.msg_te.setFont(self.font_)
        self.msg_te.setDisabled(1)

        msg_form = QFormLayout()
        msg_form.setContentsMargins(0, 0, 0, 0)
        msg_form.setSpacing(0)
        msg_form.addRow(self.msg_te, self.msg_send_btn)
        msg_wig = QWidget()
        msg_wig.setContentsMargins(0, 0, 0, 0)
        msg_wig.setLayout(msg_form)
        glayout.addWidget(msg_wig, 2, 0, Qt.AlignmentFlag.AlignCenter)

    # to send message to session
    def sendMsg(self):
        msg = self.msg_te.toPlainText()
        self.send_msg((f"{self.name}(HOST)", msg) if self.sr_btn.isChecked() else msg)
        self.msg_te.clear()

        self.updateNewMsgToList(self.name, msg, 'send')

    # to recive message from session
    def recivedMsg(self, replay):
        if replay[0] == 'Server' and replay[1].startswith("Connection status: Failed"):
            try: 
                self.client.server_replay_sig.disconnect()
                self.client.host_disconnected_sig.disconnect()
                self.client.connection_error_sig.disconnect()
                self.client.connected_sig.disconnect()
                self.client.timeout_sig.disconnect()
                self.client.client_in_out_sig.disconnect()
                self.client_in_out_sig.disconnect()
            except: pass
            self.msg_send_btn.setDisabled(1)
            self.msg_te.setDisabled(1)
            self.connection_frame.setDisabled(0)
            self.sr_or_cl_status_frame.setDisabled(0)
        
        self.updateNewMsgToList(replay[0], replay[1], 'recive')

    # upadte message list when new message recived
    def updateNewMsgToList(self, messagner_name, msg, msg_type):
        item = QListWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsUserTristate)
        item_frame = QFrame()
        item_frame.setAutoFillBackground(1)
        line_text = MessageLabel(self.font_, messagner_name, self.msg_display_frame.width(), msg_type)
        line_text.setText(msg)
        item_layout = QHBoxLayout()
        item_layout.addWidget(line_text, 0, Qt.AlignmentFlag.AlignRight if msg_type=='send' else Qt.AlignmentFlag.AlignLeft)
        item_frame.setLayout(item_layout)
        item.setSizeHint(item_frame.sizeHint())

        self.msg_display.addItem(item)
        self.msg_display.setItemWidget(item, item_frame)

        self.msg_display.scrollToBottom()

    # send toast
    def toast(self, info):
        self.font_.setPixelSize(15)

        toast_lbl = QLabel()
        toast_lbl.setMaximumWidth(int(self.msg_display.width()*0.9))
        toast_lbl.setFixedHeight(30)
        toast_lbl.setStyleSheet(f"background: rgba(127, 153, 134, 50); border-radius: {toast_lbl.height()//2}px;")
        toast_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toast_lbl.setFont(self.font_)

        if info[0] == 'port_in_use':
            if info[1]:
                toast_lbl.setStyleSheet(f"background: rgba(255, 235, 59, 100); border-radius: {toast_lbl.height()//2}px;")
                toast_lbl.setText(f"Port '{self.port}' in use, Try other port")
            else: toast_lbl.setText(f"Server started in {self.ip}:{self.port}")
        elif info[0] == 'in':
            if info[1].endswith('(HOST)'):
                toast_lbl.setText(f"'{info[1].rstrip(' (HOST)')}' is the host of this session")
            else:
                toast_lbl.setText(f"'{info[1]}' client joined the session")
        elif info[0] == 'out':
            toast_lbl.setText(f"'{info[1]}' client leaved the session")
        elif info[0] == 'host_disconnected':
            toast_lbl.setStyleSheet(f"background: rgba(216, 67, 21, 100); border-radius: {toast_lbl.height()//2}px;")
            toast_lbl.setText("Host stoped the session")
            self.updateClientList(('out', '(HOST)'))
        elif info[0] == 'error':
            toast_lbl.setStyleSheet(f"background: rgba(216, 67, 21, 100); border-radius: {toast_lbl.height()//2}px;")
            toast_lbl.setFixedHeight(60)
            toast_lbl.setText(f"Error occcured: {info[1]}\nClose and restart the application")
            toast_lbl.setWordWrap(1)
        elif info[0] == 'connecting':
            toast_lbl.setText("Trying to connect host")
        elif info[0] == 'connected':
            self.msg_send_btn.setDisabled(0)
            self.msg_te.setDisabled(0)
            toast_lbl.setText(f"Connected to host")
        elif info[0] == 'host_timeout':
            toast_lbl.setStyleSheet(f"background: rgba(255, 235, 59, 100); border-radius: {toast_lbl.height()//2}px;")
            toast_lbl.setFixedHeight(45)
            toast_lbl.setText("Error occcured: Unable to connect host\nTrying to reconnect...")

        item = QListWidgetItem()
        item.setFlags(Qt.ItemFlag.ItemIsUserTristate)
        item_frame = QFrame()
        item_frame.setAutoFillBackground(1)
        item_layout = QHBoxLayout()
        item_layout.addWidget(toast_lbl)
        item_frame.setLayout(item_layout)
        item.setSizeHint(item_frame.sizeHint())

        self.msg_display.addItem(item)
        self.msg_display.setItemWidget(item, item_frame)

        self.msg_display.scrollToBottom()


# message label design
class MessageLabel(QWidget):
    def __init__(self, font: QFont, messagener_name, max_width, msg_recive_or_send):
        super().__init__()

        self.font_ = font
        self.messagener_name = messagener_name
        self.max_width = max_width
        self.msg_recive_or_send = msg_recive_or_send
        self.setFixedSize(200, 50)

        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(0)
        self.setLayout(vlayout)

        self.msg_messagener_name_lbl = QLabel()
        self.msg_messagener_name_lbl.setText(messagener_name)
        self.msg_messagener_name_lbl.setMaximumWidth(round(self.max_width*0.7))
        self.msg_messagener_name_lbl.setContentsMargins(10, 5, 0, 0)
        self.msg_messagener_name_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.msg_messagener_name_lbl.setStyleSheet("color: yellow")
        self.msg_messagener_name_lbl.setFont(font)
        vlayout.addWidget(self.msg_messagener_name_lbl, 0, Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignLeft)

        self.msg_lbl = QLabel()
        self.msg_lbl.setFixedWidth(round(self.max_width*0.8))
        self.msg_lbl.setStyleSheet("color: white")
        self.msg_lbl.setContentsMargins(0, 5, 0, 5)
        self.msg_lbl.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        self.msg_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.msg_lbl.setFont(font)
        self.msg_lbl.setWordWrap(1)
        vlayout.addWidget(self.msg_lbl, 0, Qt.AlignmentFlag.AlignTop|Qt.AlignmentFlag.AlignHCenter)

    def setText(self, text):
        self.msg_lbl.setText(text)
        self.setFixedSize(QSizeF(self.msg_lbl.sizeHint().width()+20, self.msg_messagener_name_lbl.sizeHint().height()+self.msg_lbl.sizeHint().height()).toSize())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(RENDER_HINTS, True)

        self.main_crect = QRectF(0, 0, self.width()-15, self.height())
        self.main_crect.moveCenter(self.rect().center())

        painter.setPen(QPen(QColorConstants.Svg.red, 2))

        path = QPainterPath()
        path.moveTo(self.main_crect.topLeft()+QPointF(0, 3))
        path.lineTo(self.main_crect.bottomLeft())
        path.lineTo(self.main_crect.bottomRight())
        path.lineTo(self.main_crect.topRight()+QPointF(0, 15))
        path.lineTo(QPointF(self.rect().topRight().x(), self.main_crect.topRight().y()+3))
        path.lineTo(self.main_crect.topLeft()+QPointF(0, 3))

        painter.setBrush(QColorConstants.Svg.darkgreen)

        if self.msg_recive_or_send == "recive":
            t = QTransform()
            t.rotate(180, Qt.Axis.YAxis)
            path.boundingRect().x()
            path = t.map(path)
            path.translate(-path.boundingRect().x(), -path.boundingRect().y())
            painter.setBrush(QColorConstants.Svg.green)

        painter.drawPath(path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
