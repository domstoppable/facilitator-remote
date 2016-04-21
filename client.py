from PySide import QtGui, QtCore, QtNetwork
from functools import partial

from ui import *

class RemoteWindow(QtGui.QWidget):
	def __init__(self):
		super().__init__()
		
		self.setWindowTitle('Facilitator Remote')
		self.setLayout(QtGui.QVBoxLayout())
		
		self.hostBox = QtGui.QLineEdit('localhost')
		self.portBox = QtGui.QLineEdit('1234')
		self.connectButton = ToggleButton()
		self.connectButton.enabled.connect(self.connectToHost)
		self.connectButton.disabled.connect(self.disconnect)
		
		form = QtGui.QFormLayout()
		form.addRow('Host', self.hostBox)
		form.addRow('Port', self.portBox)
		form.addRow('Connection', self.connectButton)
		self.layout().addLayout(form)
		
		self.commandContainer = QtGui.QVBoxLayout()
		self.layout().addLayout(self.commandContainer)
		
		self.keyboardControlButton = QtGui.QPushButton('Keyboard control')
		self.keyboardControlButton.setCheckable(True)
		self.commandContainer.addWidget(self.keyboardControlButton)
		
		self.client = None
		self.installEventFilter(self)
		
	def eventFilter(self, widget, event):
#		if not self.keyboardControlButton.isChecked():
#			if event.type()
#			return True
		return super().eventFilter(widget, event)
		
	def connectToHost(self):
		self.client = RemoteClient(self.hostBox.text(), int(self.portBox.text()))
		self.client.receivedCommandList.connect(self.addCommands)
		self.client.connectToHost()
		
	def disconnect(self):
		self.client.socket.close()
		
	def addCommands(self, commands):
		while self.commandContainer.count() > 0:
			item = self.commandContainer.takeAt(0)
			widget = item.widget()
			self.commandContainer.removeWidget(widget)
			widget.setParent(None)
			del widget
			del item
		
		for c in commands:
			b = QtGui.QPushButton(c['key'])
			b.setToolTip(c['command'])
			b.clicked.connect(partial(self.client.sendCommand, c['key']))
			self.commandContainer.addWidget(b)
			
		self.adjustSize()

class RemoteClient(QtCore.QObject):
	receivedCommandList = QtCore.Signal(object)
	
	def __init__(self, host, port):
		super().__init__()
		self.host = host
		self.port = port
		self.socket = None
		
	def connectToHost(self):
		self.socket = QtNetwork.QTcpSocket()
		self.socket.connected.connect(self.connected)
		self.socket.disconnected.connect(self.disconnected)
		self.socket.readyRead.connect(self.readyRead)
		self.socket.connectToHost(self.host, self.port)
		
	def connected(self):
		self.socket.write('command-list')
		
	def disconnected(self):
		print('Disconnected!')
		
	def sendCommand(self, key):
		self.socket.write('cmd\t%s' % key)

	def readyRead(self):
		data = str(self.socket.readAll()).split('\t')

		cmd = data.pop(0)
		if cmd == 'command-list':
			commandList = []
			for c in data:
				c = c.split(',')
				commandList.append({
					'key': c[0],
					'command': c[1],
				})
			self.receivedCommandList.emit(commandList)
		else:
			print('Unknown message: %s - %s)' % (cmd, data))
	

if __name__ == '__main__':
	import sys

	app = QtGui.QApplication(sys.argv)
	appWindow = RemoteWindow()
	appWindow.show()
	sys.exit(app.exec_())
