import sys
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QWidget
from view import View
from model import Model
import pandas as pd

class Controller():
    def __init__(self):
        self.csv_name = ''
        self.stopwords = []
        self.columns = []
        self.view = View(self)
        self.model = Model(self)
        self.existingWordMsg = QMessageBox()
        self.existingWordMsg.setIcon(QMessageBox.Information)
        self.existingWordMsg.setWindowTitle('Invalid Stopword')
        self.existingWordMsg.setText('The word is already in the list of stopwords.')
        self.WCErrorMsg = QMessageBox()
        self.WCErrorMsg.setIcon(QMessageBox.Warning)
        self.WCErrorMsg.setWindowTitle('Invalid Data')
        self.WCErrorMsg.setText('Wordcloud cannot be generated. Please check data and column selected.')

    def main(self):
        self.view.main()

    def csvClick(self):
        self.csv_name, _ = QFileDialog.getOpenFileName(None, 'Select a CSV file', QDir.currentPath(), 'CSV File (*.csv)')
        print(self.csv_name,)
        if self.csv_name == '':
            pass
        else:
            self.model.load_csv(self.csv_name)
            self.view.csvSelected()

    
    def addToListWidget(self):
        text = self.view.frame2.inputbox.text().strip().lower()
        if text == '':
            pass
        if text not in self.stopwords:
            self.stopwords.append(text)
            self.view.frame2.list.addItem(text)
            self.view.frame2.inputbox.setText('')
        else:
            self.existingWordMsg.exec_()
            self.view.frame2.inputbox.setText('')

    def delFromListWidget(self):
        itemList = self.view.frame2.list.selectedItems()
        if not itemList: return
        for item in itemList:
            self.stopwords.remove(item.text())
            self.view.frame2.list.takeItem(self.view.frame2.list.row(item))

    def clearListWidget(self):
        self.view.frame2.list.clear()
        self.stopwords = []

    def changecsv(self):
        self.view.frame1.raise_()
        self.csv_name = ''

    def dropdownSelectionChanged(self, i):
        self.model.currentCol = self.view.frame2.dropdown.itemText(i)

    def generateWordCloud(self, i):
        self.model.addedStopWords = [self.view.frame2.list.item(i).text() for i in range(self.view.frame2.list.count())]
        self.model.createWCObject(self.model.addedStopWords)
        if self.model.wcObject == None:
            self.WCErrorMsg.exec_()
        else: 
            self.view.generateWC(self.model.wcObject, self.model.freq, self.model.freq_df, self.model.df[[self.model.currentCol]])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('QtCurve')
    controller = Controller()
    controller.main()
    sys.exit(app.exec_())