from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont

def increaseAppSize(window):
	font = QFont()
	font.setPointSize(QApplication.font().pointSize()+1)
	QApplication.setFont(font)
	
def decreaseAppSize(window):
	font = QFont()
	font.setPointSize(QApplication.font().pointSize()-1)
	QApplication.setFont(font)

def showPopupInfo(title, msg):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)  # Options: Information, Warning, Critical, or Question
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()

def showPopupInfoYesNo(title, msg):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)  # Options: Information, Warning, Critical, or Question
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    return msg_box.exec() == QMessageBox.Yes

def showPopupCritical(title, msg):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)  # Options: Information, Warning, Critical, or Question
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()
