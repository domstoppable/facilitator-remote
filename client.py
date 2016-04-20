from PySide import QtGui, QtCore, QtNetwork

class RemoteWindow(QtGui.QWidget):
	def __init__(self):
		super().__init__()
		
		self.setWindowTitle('Facilitator Remote')
		self.setLayout(QtGui.QVBoxLayout())

class RemoteClient(QtCore.QObject):
	def __init__(self, host, port):
		super().__init__()
		self.host = host
		self.port = port
		self.socket = None
		
	def connect(self):
		self.socket = QtNetwork.QTcpSocket()
		self.socket.connected.connect(self.connected)
		self.socket.disconnected.connect(self.disconnected)
		self.socket.readyRead.connect(self.readyRead)
		self.socket.connectToHost(self.host, self.port)
		
	def connected(self):
		print('We totally connected... sending some data now')
		self.socket.write('command-list')
		print('Data sent, hopefully')
		
	def disconnected(self):
		print('Disconnected!')
		exit(1)

	def readyRead(self):
		data = self.socket.readAll()
		print(data)
	

if __name__ == '__main__':
	import sys

	app = QtGui.QApplication(sys.argv)
	client = RemoteClient('localhost', 1234)
	client.connect()
	sys.exit(app.exec_())
