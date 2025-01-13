from PySide6.QtWidgets import QApplication, QLabel, QSizePolicy, QButtonGroup
from PySide6.QtGui import QKeySequence, QShortcut, QFont
from PySide6.QtCore import Qt

import re
import os
import time
import json
import threading

from scripts import utils, quiz_setup, quiz_main
# from scripts.quiz_main import QUIZ_MAIN

DATAPATH = 'data'
QUIZNAME = ''
QUIZPATH = ''
TMPQUIZPATH = ''


class ImageLabel(QLabel):
	def __init__(self):
		super().__init__()
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.setMinimumSize(1, 1)
		self.setAlignment(Qt.AlignCenter)
		
	def setPixmap(self, pixmap):
		self.original_pixmap = pixmap
		self._update_pixmap()
		
	def resizeEvent(self, event):
		super().resizeEvent(event)
		self._update_pixmap()
		
	def _update_pixmap(self):
		if hasattr(self, 'original_pixmap') and not self.original_pixmap.isNull():
			scaled_pixmap = self.original_pixmap.scaled(
				self.size(),
				Qt.KeepAspectRatio,
			)
			super().setPixmap(scaled_pixmap)

class Application():
	def __init__(self, ui):
		self.window = ui
		self.questions = []
		self.QUIZ_MAIN = quiz_main.QUIZ_MAIN(self.window)
		self.QUIZ_SETUP = quiz_setup.QUIZ_SETUP(self.window)

		# Check folders
		if not os.path.exists(DATAPATH):
			os.mkdir(DATAPATH)

		# Default size
		font = QFont()
		font.setPointSize(11)
		QApplication.setFont(font)

		# Config radio button
		self.window.rbtnModePractice.setChecked(True)
		self.btnGrpMode = QButtonGroup(self.window)
		self.btnGrpMode.addButton(self.window.rbtnModePractice)
		self.btnGrpMode.addButton(self.window.rbtnModeQuiz)

		self.window.rbtnShowAnswerNo.setChecked(True)
		self.btnGrpShowAns = QButtonGroup(self.window)
		self.btnGrpShowAns.addButton(self.window.rbtnShowAnswerNo)
		self.btnGrpShowAns.addButton(self.window.rbtnShowAnswerYes)

		self.window.rbtnRandomOrderNo.setChecked(True)
		self.btnGrpRandOrder = QButtonGroup(self.window)
		self.btnGrpRandOrder.addButton(self.window.rbtnRandomOrderNo)
		self.btnGrpRandOrder.addButton(self.window.rbtnRandomOrderYes)

		# Add shortcut "Ctrl + ]"
		shortcut = QKeySequence(Qt.CTRL | Qt.Key_BracketRight)
		QShortcut(shortcut, self.window).activated.connect(lambda: utils.increaseAppSize(self.window))
		# Add shortcut "Ctrl + ["
		shortcut = QKeySequence(Qt.CTRL | Qt.Key_BracketLeft)
		QShortcut(shortcut, self.window).activated.connect(lambda: utils.decreaseAppSize(self.window))
		# Add shortcut "Enter" in frame Quiz
		shortcut = QKeySequence("Enter")
		QShortcut(shortcut, self.window).activated.connect(self.QUIZ_MAIN.submit)
		# Add shortcut "Esc" in frame Quiz to return back frame Home
		shortcut = QKeySequence("Esc")
		QShortcut(shortcut, self.window).activated.connect(self.processEscape)

		# Setup menu action
		self.window.actionImport.triggered.connect(lambda: self.QUIZ_SETUP.fileImport(self.questions))
		self.window.actionOpen.triggered.connect(lambda: self.QUIZ_SETUP.fileOpen(self.questions))
		self.window.actionExit.triggered.connect(self.processExit)
		self.window.actionAbout.triggered.connect(self.processAbout)

		# Setup button
		self.window.rbtnModePractice.clicked.connect(lambda: self.QUIZ_SETUP.disablePartSelection(False))
		self.window.rbtnModeQuiz.clicked.connect(lambda: self.QUIZ_SETUP.disablePartSelection(True))
		self.window.btnSet.clicked.connect(self.QUIZ_SETUP.setNumberOfQuestion)
		self.window.btnStart.clicked.connect(lambda: self.switchFrame(1))
		self.window.btnSubmit.clicked.connect(self.QUIZ_MAIN.submit)
		self.window.btnNextQues.clicked.connect(self.QUIZ_MAIN.nextQuestion)
		self.window.btnPrevQues.clicked.connect(self.QUIZ_MAIN.prevQuestion)

		# Config lstQuestions
		self.window.lstQuestions.itemDoubleClicked.connect(lambda item: self.QUIZ_MAIN.jumpToQuestion(item))

	def switchFrame(self, frame_num):
		if frame_num==1:
			if not self.window.lnName.text() or not self.window.lnNOQues.text():
				utils.showPopupInfo("No find found", 'you did not open anyfile')
				return
			self.QUIZ_MAIN.startQuiz(self.btnGrpMode.checkedButton() == self.window.rbtnModePractice,
				self.btnGrpShowAns.checkedButton() == self.window.rbtnShowAnswerYes,
				self.btnGrpRandOrder.checkedButton() == self.window.rbtnRandomOrderYes
			)
		self.window.stackedWidget.setCurrentIndex(frame_num)

	def triggerFunction(self, in_frame, func):
		if in_frame!=self.window.stackedWidget.currentIndex():
			return
		func()

	def processEscape(self):
		if self.window.stackedWidget.currentIndex()==0:
			if utils.showPopupInfoYesNo("Exit", "Are you sure you want to exit?"):
				self.processExit()
		elif self.window.stackedWidget.currentIndex()==1:
			if utils.showPopupInfoYesNo("Return to Quiz Setup", "Go back to the Quiz Setup?"):
				self.window.stackedWidget.setCurrentIndex(0)

	def processExit(self):
		self.QUIZ_SETUP.clearTemp()
		exit(0)

	def processAbout(self):
		utils.showPopupInfo("About", "Powered by JohnathanHuuTri")

