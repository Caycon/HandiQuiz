import sys
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QFile

from scripts import main

if __name__ == "__main__":
	QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
	app = QApplication(sys.argv)
	app.setStyle("Fusion")

	ui_file = QFile("mainwindow.ui")
	loader = QUiLoader()
	ui = loader.load(ui_file)
	ui_file.close()
	ui.show()					# auto fork()

	main.Application(ui)
	sys.exit(app.exec())