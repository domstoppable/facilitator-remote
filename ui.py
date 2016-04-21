from PySide import QtGui, QtCore

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

