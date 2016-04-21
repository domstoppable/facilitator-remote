import subprocess, os
print(os.name)

from PySide import QtGui, QtCore, QtNetwork

from pymouse import PyMouse
from pykeyboard import PyKeyboard

from ui import *

commands = [
	{'key':'cmd', 'command': 'cmd'},
	{'key':'explorer', 'command': 'explorer'},
	{'key':'browser', 'command': '"C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"'},
	{'key':'gnome-calc', 'command': 'gnome-calculator'},
]

def getCommandByKey(key):
	for cmd in commands:
		if cmd['key'] == key:
			return cmd

class SettingsWindow(QtGui.QWidget):
	enabled = QtCore.Signal()
	disabled = QtCore.Signal()

	def __init__(self):
		super().__init__()
		
		self.setWindowTitle('Facilitator Remote Server')
		self.setLayout(QtGui.QFormLayout())
		
		self.mainToggle = ToggleButton()
		self.mainToggle.enabled.connect(self.enabled.emit)
		self.mainToggle.disabled.connect(self.disabled.emit)
		
		self.layout().addRow('Server status', self.mainToggle)
		self.layout().addRow(QtGui.QLabel('--------------'))
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
			
	def disable(self):
		self.close()
			
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
			data = str(self.socket.readAll()).split('\t')
			
			cmd = data.pop(0)
			if cmd == 'command-list':
				response = 'command-list'
				for cmd in commands:
					response = response + '\t%s,%s' % (cmd['key'], cmd['command'])
				self.socket.write(response)
			elif cmd == 'cmd':
				commandLine = getCommandByKey(data.pop(0))['command']
				if os.name == 'posix':
					commandLine = '%s &' % commandLine
				elif os.name == 'nt':
					commandLine = 'start %s' % commandLine
				
				print(commandLine)
				subprocess.call(commandLine, shell=True)
			else:
				print('Unknown command: %s' % data)
			
		def disconnected(self):
			print('Disconnected')
			self.socket.deleteLater()
				


if __name__ == '__main__':
	import sys

	QtGui.QApplication.setStyle('Cleanlooks')
	app = QtGui.QApplication(sys.argv)
	appWindow = SettingsWindow()
	appWindow.show()
	server = RemoteListener()
	appWindow.enabled.connect(server.enable)
	appWindow.disabled.connect(server.disable)
	server.enable()
	sys.exit(app.exec_())
