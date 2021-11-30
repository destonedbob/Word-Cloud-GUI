import sys
from PyQt5.QtWidgets import (QApplication, QComboBox, QGridLayout, QGroupBox, QHeaderView, QLabel, QListWidget, QPushButton, QTableView, QTableWidget, QWidget, QFileDialog, QFrame, 
                            QSpacerItem, QVBoxLayout, QHBoxLayout, QSizePolicy, QTabWidget, QLineEdit, QMainWindow, QTableWidgetItem, QAbstractItemView)
from PyQt5.QtCore import Qt, QAbstractTableModel, QRect, QRectF
from PyQt5.QtGui import QFont, QWindow, QPalette, QColor, QFontMetrics
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas
import wordcloud

HEIGHT = 720
WIDTH = 1280

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=9, height=6, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = fig.add_subplot(111)
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)
        super(MplCanvas, self).__init__(fig)

class MplCanvas_normal_plot(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=9, height=6, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.axes = fig.add_subplot(111)
        super(MplCanvas_normal_plot, self).__init__(fig)

class View(QWidget):
    def __init__(self, Controller):
        super().__init__()
        self.controller = Controller
        self.setGeometry(380, 200, WIDTH, HEIGHT)
        self.setWindowTitle('WordCloud Generator')
        self.setStyleSheet(''' 
                QFrame {
                    background-color: #f0f0f0;
                    font-size:36pt;
                }
                QLabel#TitleLabel {
                    font-weight: bold;
                }
                QListWidget {
                    font-size:20px;
                    background-color: #f0f0f0;
                }
                QLabel#csvNameLabel {
                    font-size:20px;
                }
                QTableWidget {
                    font-size: 12pt;
                    background-color: white;
                    border: 1px solid black;
                }
                QHeaderView {
                    font-size: 12pt;
                    background-color: white;
                }
                QTabWidget {
                    background-color: #f0f0f0
                    border: 1px solid grey
                }
                QWidget#left {
                    border: 1px solid grey
                }
                QWidget#right {
                    border: 1px solid grey
                }
        ''')

        self.frame2 = secondFrame(self, self.controller)
        self.frame1 = firstFrame(self, self.controller)   

    def main(self):
        self.show()

    def change_filename(self):
        self.frame2.csvNameLabel.setText('Current File: {}'.format(self.controller.csv_name))

    def csvSelected(self):
        self.change_filename()
        self.frame2.raise_()
        self.frame2.createDropDown()

    def generateWC(self, wcObject, freq, freq_df, col_df):
        #Enable tabs
        [self.frame2.tabs.setTabEnabled(i, True) for i in range(1, self.frame2.tabs.count())]
        #WC
        self.frame2.wcCanvas.axes = None
        self.frame2.displayframe.takeCentralWidget()
        self.frame2.wcCanvas = MplCanvas(self.frame2.displayframe)
        self.frame2.wcCanvas.axes.imshow(wcObject)
        self.frame2.displayframe.setCentralWidget(self.frame2.wcCanvas)
        self.frame2.displayframe.show()
        #WF Plot
        self.frame2.wfCanvas.axes = None
        self.frame2.displayframe2.takeCentralWidget()
        self.frame2.wfCanvas = MplCanvas_normal_plot(self.frame2.displayframe2)
        zipped = sorted(zip(list(freq.keys()), list(freq.values())), key=lambda x: x[1], reverse=True)
        x = [each for each, _ in zipped]
        y = [each for _, each in zipped]
        self.frame2.wfCanvas.axes.plot(x[:50], y[:50])
        self.frame2.wfCanvas.axes.set_xticklabels(labels=x, rotation=90)
        self.frame2.displayframe2.setCentralWidget(self.frame2.wfCanvas)
        self.frame2.displayframe2.show()
        #WF Data Table
        self.frame2.datatable.setRowCount(freq_df.shape[0])
        self.frame2.datatable.setColumnCount(freq_df.shape[1])
        self.frame2.datatable.setHorizontalHeaderLabels(freq_df.columns)
        for row in freq_df.iterrows():
            for col_idx, value in enumerate(row[1]):
                if isinstance(value, int):
                    tableItem = QTableWidgetItem(str(value))
                else:
                    tableItem = QTableWidgetItem(value)
                self.frame2.datatable.setItem(row[0], col_idx, tableItem)
        self.frame2.datatable.resizeColumnsToContents()
        self.frame2.datatable.resizeRowsToContents()
        self.frame2.datatable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #Raw Data Table
        self.frame2.rawdatatable.setRowCount(col_df.shape[0])
        self.frame2.rawdatatable.setColumnCount(col_df.shape[1])
        self.frame2.rawdatatable.setHorizontalHeaderLabels(['Raw Data'])
        for row in col_df.iterrows():
            for col_idx, value in enumerate(row[1]):
                if isinstance(value, int):
                    tableItem = QTableWidgetItem(str(value))
                else:
                    tableItem = QTableWidgetItem(value)
                self.frame2.rawdatatable.setItem(row[0], col_idx, tableItem)
        # self.frame2.rawdatatable.resizeColumnsToContents()
        self.frame2.rawdatatable.resizeRowsToContents()
        self.frame2.rawdatatable.setEditTriggers(QAbstractItemView.NoEditTriggers)

class firstFrame(QFrame):
    def __init__(self, parent, controller):
        super().__init__(parent=parent)
        self.controller = parent.controller
        self.setGeometry(0, 0, WIDTH, HEIGHT)

        #Label
        self.TitleLabel = QLabel()
        self.TitleLabel.setText("WordCloud Generator")
        self.TitleLabel.setObjectName('TitleLabel')
        self.TitleLabel.move((WIDTH-self.TitleLabel.width())/2, (HEIGHT-self.TitleLabel.height())/2)
        self.TitleLabel.setAlignment(Qt.AlignCenter)
        self.TitleLabel.setMargin(20)

        #CSV button with filedialog
        self.csvButton = QPushButton()
        self.csvButton.setText('Upload CSV File')
        self.csvButton.move((WIDTH-self.csvButton.width())/2, HEIGHT*3/4-self.csvButton.height()/2)
        self.csvButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.csvButton.clicked.connect(self.controller.csvClick)

        #Spacers (create space at top and bottom)
        spacerItem = QSpacerItem(0, HEIGHT, QSizePolicy.Minimum, QSizePolicy.Expanding)
        spacerItem2 = QSpacerItem(0, HEIGHT, QSizePolicy.Minimum, QSizePolicy.Expanding)

        #Layout
        self.layout = QVBoxLayout()
        self.layout.addItem(spacerItem)
        self.layout.addWidget(self.TitleLabel)
        self.layout.addWidget(self.csvButton, alignment=Qt.AlignCenter)
        self.layout.addItem(spacerItem2)
        self.setLayout(self.layout)

class secondFrame(QFrame):
    def __init__(self, parent, Controller): #add controller
        super().__init__(parent=parent)
        self.controller = Controller
        self.setGeometry(0,0, WIDTH, HEIGHT)
        self.grid = QGridLayout(self)

        #Left
        self.left = QWidget()
        self.left.setObjectName('left')
        self.leftlayout = QVBoxLayout()
            #Group box for dropdown
        self.ddgroupbox = QGroupBox('Select column to analyze:')
        self.ddgroupbox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
                #Drop down with all columns
        self.dropdown = QComboBox()
        self.dropdown.currentIndexChanged.connect(self.controller.dropdownSelectionChanged)
        self.ddlayout = QVBoxLayout()
        self.ddlayout.addWidget(self.dropdown)
        self.ddgroupbox.setLayout(self.ddlayout)
            
            #Input box for user to enter stopwords
        self.inputbox = QLineEdit()
        self.inputbox.setPlaceholderText('Add a stopword (case insensitive)')
        self.inputbox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.inputbox.returnPressed.connect(self.controller.addToListWidget)
            #Show list of entered stopwords
        self.list = QListWidget()
        self.list.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            #Adding Buttons
        self.HButtonLayout = QHBoxLayout()
        self.addbutton = QPushButton()
        self.addbutton.setText('Add')
        self.addbutton.clicked.connect(self.controller.addToListWidget)
        self.delbutton = QPushButton()
        self.delbutton.setText('Delete')
        self.delbutton.clicked.connect(self.controller.delFromListWidget)
        self.clearbutton = QPushButton()
        self.clearbutton.setText('Clear')
        self.clearbutton.clicked.connect(self.controller.clearListWidget)

            #Adding All Widgets on Left
        self.HButtonLayout.addWidget(self.addbutton)
        self.HButtonLayout.addWidget(self.delbutton)
        self.HButtonLayout.addWidget(self.clearbutton)
        self.leftlayout.addWidget(self.ddgroupbox)
        self.leftlayout.addWidget(self.inputbox)
        self.leftlayout.addWidget(self.list)
        self.leftlayout.addLayout(self.HButtonLayout)
        self.left.setLayout(self.leftlayout)

        #Right
        self.tabs = QTabWidget()
        self.right = QWidget()
        self.right.setObjectName('right')
        self.right2 = QWidget()
        self.right3 = QWidget()
        self.right4 = QWidget()
        self.tabs.addTab(self.right, 'Word Cloud')
        self.tabs.addTab(self.right2, 'Top 50 Word/Phrase Plot')
        self.tabs.addTab(self.right3, 'Word Frequency Table')
        self.tabs.addTab(self.right4, 'Column\'s Raw Data')
        self.rightlayout = QVBoxLayout()
        self.rightlayout.setAlignment(Qt.AlignHCenter)
            #Frame (Tab 1 - WC)
        self.displayframe = QMainWindow()
        self.displayframe.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.generateButton = QPushButton()
        self.generateButton.setText('Generate WordCloud')
        self.generateButton.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.generateButton.clicked.connect(self.controller.generateWordCloud)
        self.rightlayout.addWidget(self.displayframe)
        self.rightlayout.addWidget(self.generateButton)
        self.right.setLayout(self.rightlayout)
            #try plot
        self.wcCanvas = MplCanvas(self.displayframe)
        self.displayframe.setCentralWidget(self.wcCanvas)
        self.displayframe.show()
            # Frame2, (Tab 2 - WF)
        self.rightlayout2 = QVBoxLayout()
        self.rightlayout2.setAlignment(Qt.AlignHCenter)
        self.displayframe2 = QMainWindow()
        self.displayframe2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.rightlayout2.addWidget(self.displayframe2)
        self.right2.setLayout(self.rightlayout2)
        self.wfCanvas = MplCanvas_normal_plot(self.displayframe2)
        self.displayframe2.setCentralWidget(self.wfCanvas)
        self.displayframe2.show()
            #Frame3, (Tab 3 - Table)
        self.rightlayout3 = QVBoxLayout()
        self.rightlayout3.setAlignment(Qt.AlignHCenter)
        self.displayframe3 = QWidget()
        self.displayframe3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.datatable = QTableWidget()
        self.datatable.horizontalHeader().setStretchLastSection(True)
        self.datatable.verticalHeader().setVisible(True)
        self.layoutforTable = QVBoxLayout(self.displayframe3)
        self.layoutforTable.addWidget(self.datatable)
        self.rightlayout3.addWidget(self.displayframe3)
        self.right3.setLayout(self.rightlayout3)
            #Frame4, (Tab 4 - Raw Data Tab)
        self.rightlayout4 = QVBoxLayout()
        self.rightlayout4.setAlignment(Qt.AlignHCenter)
        self.displayframe4 = QWidget()
        self.displayframe4.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.rawdatatable = QTableWidget()
        self.rawdatatable.horizontalHeader().setStretchLastSection(True)
        self.rawdatatable.verticalHeader().setVisible(True)
        self.layoutforrawTable = QVBoxLayout(self.displayframe4)
        self.layoutforrawTable.addWidget(self.rawdatatable)
        self.rightlayout4.addWidget(self.displayframe4)
        self.right4.setLayout(self.rightlayout4)
            #disable tab before Generate
        [self.tabs.setTabEnabled(i, False) for i in range(1,self.tabs.count())]


        # Top
        self.top = QWidget()
        self.top.setObjectName('top')
        self.top.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.toplayout = QHBoxLayout()
        self.csvNameLabel = QLabel()
        self.csvNameLabel.setObjectName('csvNameLabel')
        # self.csvNameLabel.setFont(QFont('Arial', 16))
        self.csvNameLabel.setText('')
        self.changecsvButton = QPushButton()
        self.changecsvButton.setText('Change CSV')
        self.changecsvButton.clicked.connect(self.controller.changecsv)
        self.changecsvButton.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.toplayout.addWidget(self.csvNameLabel)
        self.toplayout.addWidget(self.changecsvButton)
        self.top.setLayout(self.toplayout)

        self.grid.addWidget(self.top, 0, 0, 1, 4)
        self.grid.addWidget(self.left, 1, 0, 7, 1)
        self.grid.addWidget(self.tabs, 1, 1, 7, 3)
                        
        

        self.left.setAutoFillBackground(True)
        paletteleft = self.left.palette()
        self.left.setPalette(paletteleft)

        self.right.setAutoFillBackground(True)
        paletteright = self.right.palette()
        self.right.setPalette(paletteright)
        self.setLayout(self.grid)
        
    def createDropDown(self):
        self.dropdown.clear()
        for col in self.controller.columns:
            self.dropdown.addItem(col)
        listOfStrings = [self.dropdown.itemText(i) for i in range(self.dropdown.count())]
        w=self.dropdown.fontMetrics().boundingRect(max(listOfStrings, key=len)).width()
        self.dropdown.view().setFixedWidth(w+10)
    
        # frame to display image TODO


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = View()
#     window.main()
#     sys.exit(app.exec_())