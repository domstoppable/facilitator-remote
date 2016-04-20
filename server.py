from PySide import QtGui, QtCore, QtNetwork

from pymouse import PyMouse
from pykeyboard import PyKeyboard

commands = [
	{'key':'cmd', 'command': 'cmd'},
	{'key':'explorer', 'command': 'explorer'},
	{'key':'browser', 'command': 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'},
]

class ToggleButton(QtGui.QWidget):
	enabled = QtCore.Signal()
	disabled = QtCore.Signal()
	
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setLayout(QtGui.QHBoxLayout())
		self.layout().setSpacing(0)
		
		self.offButton = QtGui.QPushButton('Off')
		self.offButton.clicked.connect(self.disable)
		self.layout().addWidget(self.offButton)

		self.onButton = QtGui.QPushButton('On')
		self.onButton.clicked.connect(self.enable)
		self.layout().addWidget(self.onButton)
		
		pal = self.onButton.palette()
		self.defaultColor = pal.color(pal.Button)
		
	def disable(self):
		self._setColor(self.onButton, self.defaultColor)
		self._setColor(self.offButton, QtCore.Qt.red)
		self.disabled.emit()
		
	def enable(self):
		self._setColor(self.onButton, QtCore.Qt.green)
		self._setColor(self.offButton, self.defaultColor)
		self.enabled.emit()
		
	def _setColor(self, button, bgColor):
		pal = button.palette()
		pal.setColor(pal.Button, bgColor)
		button.setAutoFillBackground(True)
		button.setPalette(pal)
		button.update()

class SettingsWindow(QtGui.QWidget):
	def __init__(self):
		super().__init__()
		
		self.setWindowTitle('Facilitator Remote Server')
		self.setLayout(QtGui.QFormLayout())
		self.layout().addRow('Allow mouse countrol', ToggleButton())
		self.layout().addRow('Allow keyboard countrol', ToggleButton())
		self.layout().addRow(QtGui.QLabel('Command list'))
		self.layout().addRow(QtGui.QLabel('Key'), QtGui.QLabel('Command'))
		for cmd in commands:
			self.layout().addRow(QtGui.QLineEdit(cmd['key']), QtGui.QLineEdit(cmd['command']))

class RemoteListener(QtNetwork.QTcpServer):
	def __init__(self):
		super().__init__()
		self.mouse = PyMouse()
		self.keyboard = PyKeyboard()
		self.connections = []
		
	def enable(self):
		if not self.listen(port=1234):
			raise 'Unable to start server :('
		print('Listening!')
			
	def incomingConnection(self, socketDescriptor):
		print('Incoming connection - that is neat!')
		self.connections.append(self.ClientConnection(socketDescriptor, self))

	class ClientConnection():
		error = QtCore.Signal(object)
		
		def __init__(self, socketDescriptor, parent):
			super().__init__()
			self.parent = parent
			self.socketDescriptor = socketDescriptor

			self.socket = QtNetwork.QTcpSocket()
			if not self.socket.setSocketDescriptor(self.socketDescriptor):
				self.error.emit(self.socket.error())
				return
				
			self.socket.readyRead.connect(self.readyRead) # may need Qt::DirectConnection 
			self.socket.disconnected.connect(self.disconnected)
			
		def readyRead(self):
			data = self.socket.readAll()
			print('Received: %s' % data)
			if data == 'command-list':
				self.socket.write('command-list\tnasa-tlx')
			else:
				print('Unknown command: %s' % data)
			
		def disconnected(self):
			print('Disconnected')
			self.socket.deleteLater()
			exit(0)
				


if __name__ == '__main__':
	import sys

	QtGui.QApplication.setStyle('Cleanlooks')
	app = QtGui.QApplication(sys.argv)
	appWindow = SettingsWindow()
	appWindow.show()
#	server = RemoteListener()
#	server.enable()
	sys.exit(app.exec_())
