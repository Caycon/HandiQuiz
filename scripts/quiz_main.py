from PySide6.QtWidgets import QRadioButton, QCheckBox, QButtonGroup, QFormLayout, QLabel, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

import json
import random

from scripts import main, utils

class ClickableLabel(QLabel):
	def __init__(self, text, btn):
		self.btn = btn
		self.enable = True
		super().__init__(text, None)

	def mousePressEvent(self, event):
		if self.enable and event.button() == Qt.LeftButton:
			self.btn.setChecked(not self.btn.isChecked())

	def setEnabled(self, enable):
		self.enable = enable

class QUIZ_MAIN:
	def __init__(self, window):
		self.window = window
		self.current_question = 0
		self.number_of_question = 0
		self.questions = None
		self.show_answer_mode = False
		self.show_answer = False
		self.image_label = None
		self.btnGrpAnswer = None

	def startQuiz(self, is_mode_practice, is_show_answer, is_random_order):
		self.window.lstQuestions.clear()
		self.clearData()

		questions = json.loads(open(f'{main.TMPQUIZPATH}/data', 'r').read())
		self.number_of_question = int(self.window.lnNOQues.text())
		if is_mode_practice:
			part = int(self.window.cbbPartNumber.currentText().split(' ')[1]) - 1
			tmp = questions[part*self.number_of_question:part*self.number_of_question+self.number_of_question]
			if is_random_order:
				random.shuffle(tmp)
		else:
			tmp = []
			for _ in range(self.number_of_question):
				if len(questions) == 0:
					break
				question = random.choice(questions)
				tmp.append(question)
				questions.remove(question)
			random.shuffle(tmp)
		if len(tmp)!=self.number_of_question:
			self.number_of_question = len(tmp)
		for ques in tmp: ques['select'] = []
		self.questions = tmp
		self.show_answer_mode = is_show_answer

		# Add questions to list widget
		for obj in self.questions:
			if len(obj['question'].split('\n')[0]) < 28:
				self.window.lstQuestions.addItems([obj['question'].split('\n')[0]])
			else:
				self.window.lstQuestions.addItems([obj['question'].split('\n')[0][:28] + '...'])
		self.showQuestion()

	def jumpToQuestion(self, item):
		self.saveAnswer(0)
		self.current_question = self.window.lstQuestions.row(item)
		self.showQuestion()

	def nextQuestion(self):
		self.saveAnswer(0)
		if self.current_question < self.number_of_question-1:
			self.current_question += 1
			self.showQuestion()

	def prevQuestion(self):
		self.saveAnswer(0)
		if self.current_question > 0:
			self.current_question -= 1
			self.showQuestion()

	def showQuestion(self):
		# Change question
		self.window.lblQuestion.setText('        ' + self.questions[self.current_question]['question'])

		# Add image of question
		if self.image_label:
			layout = self.window.widget.layout()
			layout.removeWidget(self.image_label)  # Remove widget from layout
			self.image_label.deleteLater()  # Delete the widget to free memory
			self.image_label = None  # Clear the reference to the widget
		if self.questions[self.current_question]['image']:
			layout = self.window.widget.layout()
			self.image_label = main.ImageLabel()
			pixmap = QPixmap(f'{main.TMPQUIZPATH}/{self.questions[self.current_question]["image"]}')
			self.image_label.setPixmap(pixmap)
			layout.insertWidget(1, self.image_label)

		# Add answers for questions
		layout = self.window.lstAnswers.layout()
		while layout.count():	# Remove all widgets from the layout
			item = layout.takeAt(0)	# Take the first item in the layout
			widget = item.widget()
			if widget:
				widget.deleteLater()	# Schedule the widget for deletion
			else:
				layout.removeItem(item)

		self.btnGrpAnswer = QButtonGroup(self.window)
		for idx,answer in enumerate(self.questions[self.current_question]["answers"]):
			# Create button and label
			if len(self.questions[self.current_question]["correct"])==1:
				btn = QRadioButton('')
				self.btnGrpAnswer.addButton(btn)
			else:
				btn = QCheckBox('')
			lblAnswer = ClickableLabel(answer + '', btn)
			lblAnswer.setWordWrap(True)

			# Add shortcut to label
			btn.setShortcut(str(idx+1))

			# Set selected answer and show answer
			if self.show_answer_mode:
				if len(self.questions[self.current_question]['select'])!=0:
					btn.setEnabled(False)
					lblAnswer.setEnabled(False)
					if idx+1 in self.questions[self.current_question]['select']:
						lblAnswer.setText(lblAnswer.text() + ' ❌')
					if idx+1 in self.questions[self.current_question]['correct']:
						lblAnswer.setText(lblAnswer.text().replace(' ❌', '') + ' ✅')
			elif self.show_answer:
				btn.setEnabled(False)
				lblAnswer.setEnabled(False)
				if idx+1 in self.questions[self.current_question]['select']:
					lblAnswer.setText(lblAnswer.text() + ' ❌')
				if idx+1 in self.questions[self.current_question]['correct']:
					lblAnswer.setText(lblAnswer.text().replace(' ❌', '') + ' ✅')
			if idx+1 in self.questions[self.current_question]['select']:
				btn.setChecked(True)

			# Add to layout
			form_layout = QFormLayout()
			form_layout.addRow(btn, lblAnswer)
			form_layout.setHorizontalSpacing(10)
			form_layout.setContentsMargins(0, 0, 0, 10)

			# Add widget to screen
			wdgAnswer = QWidget()
			wdgAnswer.setLayout(form_layout)
			layout.addWidget(wdgAnswer)

	def submit(self):
		self.saveAnswer(1)
		if self.show_answer_mode:		# If show answer mode then change background color of list question
			question = self.questions[self.current_question]
			if len(question['select'])!=0:
				if all(elem in question['select'] for elem in question['correct']) and all(elem in question['correct'] for elem in question['select']):
					self.window.lstQuestions.item(self.current_question).setBackground(Qt.green)
				else:
					self.window.lstQuestions.item(self.current_question).setBackground(Qt.red)
		else:							# If not show answer mode then get score of all questions
			# Check if all questions are answered
			score = 0
			not_selected = 0
			selected = 0
			for question in self.questions:
				if len(question['select'])==0:
					not_selected+=1
				else:
					selected+=1
			if not_selected:
				if not utils.showPopupInfoYesNo('Submit', f"There are {not_selected} questions left!\n\nDo you still want to submit?"):
					return

			# If user still want to submit, then switch to show answer mode and calculate score
			self.show_answer = True
			for idx, question in enumerate(self.questions):
				if len(question['select'])==0:
					# self.window.lstQuestions.item(idx).setBackground(Qt.red)
					continue
				if all(elem in question['select'] for elem in question['correct']) and all(elem in question['correct'] for elem in question['select']):
					score += 1
					self.window.lstQuestions.item(idx).setBackground(Qt.green)
				else:
					self.window.lstQuestions.item(idx).setBackground(Qt.red)
			utils.showPopupInfo("Score", f'''          Total: {self.number_of_question}                    

          Correct: {score}
          Wrong: {selected - score}
          Left: {not_selected}''')
			# utils.showPopupInfo("Score", f'{score}/{self.number_of_question}')
		self.showQuestion()

	def saveAnswer(self, by_submit):
		# If show answer then answer will be saved just by clicking submit
		if self.show_answer_mode and not by_submit or self.show_answer:
			return

		# Iterate all answers and find which answer is checked then save that
		layout = self.window.lstAnswers.layout()
		selected_questions = []
		for i in range(layout.count()):
			widget = layout.itemAt(i).widget()
			if widget.layout().itemAt(0, QFormLayout.LabelRole).widget().isChecked():
				selected_questions.append(i+1)
		self.questions[self.current_question]['select'] = selected_questions

		# If no answer is selected, then change background of question in list to white
		if len(selected_questions)!=0:
			self.window.lstQuestions.item(self.current_question).setBackground(Qt.cyan)
		else:
			self.window.lstQuestions.item(self.current_question).setBackground(Qt.white)

	def clearData(self):
		self.current_question = 0
		self.number_of_question = 0
		self.questions = None
		self.show_answer_mode = False
		self.show_answer = False
		self.btnGrpAnswer = None
		if self.image_label:
			layout = self.window.widget.layout()
			layout.removeWidget(self.image_label)  # Remove widget from layout
			self.image_label.deleteLater()  # Delete the widget to free memory
			self.image_label = None  # Clear the reference to the widget
