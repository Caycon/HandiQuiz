import re
import os
import xlrd
import json
import shutil
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

from PySide6.QtWidgets import QFileDialog
from scripts import main, utils

NUMBER_OF_QUESTION = 30

class QUIZ_SETUP:
	def __init__(self, window):
		self.window = window

	def fileImport(self, questions):
		file_path = QFileDialog.getOpenFileName(self.window, "Import", "", "Excel Workbook (*.xlsx)")
		if not file_path[0]:
			return
		path = '/'.join(file_path[0].split('/')[:-1]) + '/'
		filename = '.'.join(file_path[0].split('/')[-1].split('.')[:-1])

		if os.path.exists(f'{main.DATAPATH}/{filename}'):
			shutil.rmtree(f'{main.DATAPATH}/{filename}')
		os.mkdir(f'{main.DATAPATH}/{filename}')
		os.mkdir(f'{main.DATAPATH}/{filename}/images')

		workbook = xlrd.open_workbook(file_path[0])
		worksheet = workbook.sheet_by_index(0)
		data = []
		for col in range(worksheet.ncols):
			ques = worksheet.cell_value(rowx=0, colx=col)
			img = worksheet.cell_value(rowx=1, colx=col)
			correct = worksheet.cell_value(rowx=2, colx=col)
			ans = []
			for i in range(3, worksheet.nrows):
				if not worksheet.cell_value(rowx=i, colx=col):
					break
				ans.append(worksheet.cell_value(rowx=i, colx=col))

			# Check question
			if not ques:
				utils.showPopupCritical("Question error", 'Missing question')
				return

			# Check image
			img_path = ''
			if img:
				if os.path.exists(img):
					img_path = img
				elif os.path.exists(path + img):
					img_path = path + img
				if not img_path:
					utils.showPopupCritical("Image error", f'{ques}\n\nInvalid image path: {img}')
					# print(f"Question: \n")
					return
			img_path = img_path.replace('\\', '/')

			# Check correct answer number
			if not correct:
				utils.showPopupCritical("Answer error", f'{ques}\n\nNo answer provided')
				return
			if type(correct)==float or type(correct)==int:
				correct = str(int(correct))
			if re.search('[^0-9, ]', correct):
				utils.showPopupCritical("Answer error", f'{ques}\n\nInvalid answer number: {correct}')
				return
			correct = [int(i) for i in correct.replace(' ', '').split(',')]
			for val in correct:
				if val < 1 or len(ans) < val:
					utils.showPopupCritical("Answer error", f'{ques}\n\nInvalid answer number: {val}')
					return

			# Save data
			if img_path:
				shutil.copy(img_path, os.path.abspath(f'{main.DATAPATH}/{filename}/images'))
				img_path = 'images/' + img_path.split('/')[-1]
			data.append({
				'question': ques,
				'image': img_path,
				'correct': correct,
				'answers': ans
			})

		# Save all question
		open(f'{main.DATAPATH}/{filename}/data', 'w').write(json.dumps(data, indent=4))
		open(f'{main.DATAPATH}/{filename}/info', 'w').write(json.dumps({"number": len(data)}, indent=4))
		# Zip folder and rename to .hqz
		shutil.make_archive(f'{main.DATAPATH}/{filename}', 'zip', f'{main.DATAPATH}/{filename}')
		shutil.move(os.path.abspath(f'{main.DATAPATH}/{filename}.zip'), os.path.abspath(f'{main.DATAPATH}/{filename}.hqz'))
		shutil.rmtree(f'{main.DATAPATH}/{filename}')

		self.extractQuiz(os.path.abspath(f'{main.DATAPATH}/{filename}.hqz').replace('\\', '/'))
		self.setNumberOfQuestion()

	def fileOpen(self, filename=''):
		file_path = QFileDialog.getOpenFileName(self.window, "Open", main.DATAPATH, "HandiQuiz (*.hqz)")
		if not file_path[0]:
			return

		self.extractQuiz(file_path[0])
		self.setNumberOfQuestion()

	def fileExport(self):
		if not main.QUIZNAME or not main.TMPQUIZPATH:
			utils.showPopupInfo("Missing HandiQuiz file", f'Please open a HandiQuiz file before exporting the quiz')
			return
		file_path = QFileDialog.getSaveFileName(self.window, "Export to PDF", "", "PDF (*.pdf)")
		print(file_path)
		if not file_path[0]:
			return
		pdfmetrics.registerFont(TTFont('TimesNewRoman', 'C:/Windows/Fonts/times.ttf'))
		pdfmetrics.registerFont(TTFont('TimesNewRomanBold', 'C:/Windows/Fonts/timesbd.ttf'))
		doc = SimpleDocTemplate(file_path[0], pagesize=A4)
		question_style = ParagraphStyle(
		    name="Vietnamese",
		    fontName="TimesNewRoman",
		    fontSize=12,
		    leading=15  # Line spacing
		)
		answer_style = ParagraphStyle(
		    name="Vietnamese",
		    fontName="TimesNewRoman",
		    fontSize=12,
		    leading=15,  # Line spacing
		    firstLineIndent=10
		)
		answer_correct_style = ParagraphStyle(
		    name="VietnameseBold",
		    fontName="TimesNewRomanBold",
		    fontSize=12,
		    leading=15,  # Line spacing
		    firstLineIndent=10
		)
		content = []

		questions = json.loads(open(f'{main.TMPQUIZPATH}/data', 'r').read())
		for question in questions:
			content.append(Paragraph(question['question'].replace('\n', '<br/>') + '<br/>', question_style))
			if question['image']:
				image = ImageReader(f"{main.TMPQUIZPATH}/{question['image']}")
				img_width, img_height = image.getSize()
				scale_width = 400
				scale_height = (scale_width / img_width) * img_height  # Maintain aspect ratio
				img = Image(f"{main.TMPQUIZPATH}/{question['image']}", width=scale_width, height=scale_height)
				content.append(img)
			for i,answer in enumerate(question['answers']):
				if i+1 in question['correct']:
					content.append(Paragraph(f'  <b>{answer}</b><br/>', answer_correct_style))
				else:
					content.append(Paragraph(f'  {answer}<br/>', answer_style))
			content.append(Spacer(1, 24))
		try:
			doc.build(content)
		except Exception as e:
			utils.showPopupCritical('Error exporting...', str(e))


	def extractQuiz(self, file_path):
		# Remove existed temp folder
		if os.path.exists(main.TMPQUIZPATH):
			shutil.rmtree(main.TMPQUIZPATH)
		
		# Remove existed temp folder
		main.QUIZNAME = '.'.join(file_path.split('/')[-1].split('.')[:-1])
		main.TMPQUIZPATH = tempfile.gettempdir().replace('\\', '/') + '/' + main.QUIZNAME
		if os.path.exists(main.TMPQUIZPATH):
			shutil.rmtree(main.TMPQUIZPATH)
		os.mkdir(main.TMPQUIZPATH)
		shutil.unpack_archive(file_path, main.TMPQUIZPATH, "zip")
		self.window.lnName.setText(file_path)

	def setNumberOfQuestion(self):
		if not self.window.lnName.text():
			return

		if not self.window.lnNOQues.text():
			self.window.lnNOQues.setText(str(NUMBER_OF_QUESTION))
			number_of_question = NUMBER_OF_QUESTION
		else:
			try:
				number_of_question = int(self.window.lnNOQues.text())
			except:
				self.window.lnNOQues.setText(str(NUMBER_OF_QUESTION))
				number_of_question = NUMBER_OF_QUESTION

		info = json.loads(open(f'{main.TMPQUIZPATH}/info', 'r').read())
		self.window.cbbPartNumber.clear()
		if self.window.cbbPartNumber.isEnabled():
			self.window.cbbPartNumber.addItems([f'Part {i}' for i in range(1, (info['number']//number_of_question) + 1)])
			if info['number'] % number_of_question != 0:
				self.window.cbbPartNumber.addItem(f'Part ' + str((info['number']//number_of_question) + 1))

	def disablePartSelection(self, val):
		if val:
			self.window.lblPartNumber.setEnabled(False)
			self.window.cbbPartNumber.setEnabled(False)
			self.window.lblRandomOrder.setEnabled(False)
			self.window.rbtnRandomOrderNo.setEnabled(False)
			self.window.rbtnRandomOrderYes.setEnabled(False)
			self.window.cbbPartNumber.clear()
		else:
			self.window.lblPartNumber.setEnabled(True)
			self.window.cbbPartNumber.setEnabled(True)
			self.window.lblRandomOrder.setEnabled(True)
			self.window.rbtnRandomOrderNo.setEnabled(True)
			self.window.rbtnRandomOrderYes.setEnabled(True)
			self.setNumberOfQuestion()

	def clearTemp(self):
		if os.path.exists(main.TMPQUIZPATH):
			shutil.rmtree(main.TMPQUIZPATH)
			main.TMPQUIZPATH = ''

