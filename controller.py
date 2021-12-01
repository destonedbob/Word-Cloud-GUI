import sys
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox, QInputDialog, QLineEdit
from view import View
from model import Model
import pandas as pd
import os

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
        self.filesavedMsg = QMessageBox()
        self.filesavedMsg.setIcon(QMessageBox.Information)
        self.filesavedMsg.setWindowTitle('File Saved')
        self.filesavedMsg.setText('Your file has been saved in your selected Folder/Directory.')


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

    def saveFile(self):
        def uniquify(path):
            filename, extension = os.path.splitext(path)
            counter = 1

            while os.path.exists(path):
                path = filename + " (" + str(counter) + ")" + extension
                counter += 1

            return path

        print('Save button clicked')
        # folderpath, _ =QFileDialog.getSaveFileName(None, "Saving Outputs", "Output", "All Files (*)", options=QFileDialog.ShowDirsOnly)
        folderpath = QFileDialog.getExistingDirectory(None, 'Select Folder to Save Outputs', QDir.currentPath(), options=QFileDialog.ShowDirsOnly)
        if folderpath == '':
            return
        print(folderpath)

        filename, okPressed = QInputDialog.getText(None, "Please input your file name",
                                                    "Please type the output's file name:", QLineEdit.Normal, "")
        if okPressed and filename != '':
            #Save WC
            wcfilename = uniquify(folderpath + "/{} - Wordcloud.png".format(filename))
            self.model.wcObject.to_file(wcfilename)

            #Save FreqDist
            wffilename = uniquify(folderpath + "/{} - Top 50 Word Freq.png".format(filename))
            self.view.frame2.wfCanvas.axes.figure.savefig(wffilename)

            #Save Excel (WF + Raw Data)
            exfilename = uniquify(folderpath + "/{} - Word Frequencies.xlsx".format(filename))
            with pd.ExcelWriter(exfilename) as writer:
                self.model.freq_df.to_excel(writer, sheet_name="Word Frequencies", index=False)
                self.model.df[[self.model.currentCol]].to_excel(writer, sheet_name="Raw Data", index=False)
            
            self.filesavedMsg.exec_()
        else:
            return
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('QtCurve')
    controller = Controller()
    controller.main()
    sys.exit(app.exec_())