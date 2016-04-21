import subprocess, os

from PySide import QtGui, QtCore, QtNetwork

from pymouse import PyMouse
from pykeyboard import PyKeyboard

from ui import *

settings = QtCore.QSettings('Green Light Go', 'Facilitator Remote')

def getCommands():
	commands = []
	size = settings.beginReadArray('commands')
	for i in range(size):
		settings.setArrayIndex(i)
		commands.append({
			'key': settings.value('key'),
			'command': settings.value('command'),
		})
	settings.endArray()
		
	return commands

def saveCommands(commands):
	settings.beginWriteArray('commands')
	count = 0
	for details in commands:
		key = details['key'].strip()
		command = details['command'].strip()
		
		if key != '' or command != '':
			settings.setArrayIndex(count)
			settings.setValue('key', key)
			settings.setValue('command', command)
			count = count + 1
	settings.endArray()

def getCommandByKey(key):
	commands = getCommands()
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
		
		self.commandLayout = QtGui.QFormLayout()
		self.layout().addRow(self.commandLayout)

		addButton = QtGui.QPushButton('+')
		addButton.clicked.connect(self.addCommand)
		self.layout().addRow('', addButton)
		
		resetButton = QtGui.QPushButton('Reset')
		resetButton.clicked.connect(self.reset)
		
		saveButton = QtGui.QPushButton('Save')
		saveButton.clicked.connect(self.save)
		
		self.layout().addRow(resetButton, saveButton)
		
		self.reset()
		
	def addCommand(self, key='', cmd=''):
		self.commandListWidgets.append({
			'key': QtGui.QLineEdit(key),
			'command': QtGui.QLineEdit(cmd),
		})
		self.commandLayout.addRow(
			self.commandListWidgets[-1]['key'],
			self.commandListWidgets[-1]['command'],
		)
		
	def reset(self):
		self.commandListWidgets = []
		commands = getCommands()
		
		if len(commands) == 0:
			self.addCommand()
		else:
			for cmd in commands:
				self.addCommand(cmd['key'], cmd['command'])
			
	def save(self):
		commands = []
		for commandWidgets in self.commandListWidgets:
			commands.append({
				'key': commandWidgets['key'].text(),
				'command': commandWidgets['command'].text(),
			})
		saveCommands(commands)

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
				for cmd in getCommands():
					response = response + '\t%s,%s' % (cmd['key'], cmd['command'])
				self.socket.write(response)
			elif cmd == 'cmd':
				commandLine = getCommandByKey(data.pop(0))['command']
				if os.name == 'posix':
					commandLine = '%s &' % commandLine
				
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
