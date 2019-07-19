# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_WebEngineView.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
import sys


class UiMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(UiMainWindow, self).__init__(parent)
        self.setObjectName("MainWindow")
        self.resize(1197, 645)
        self.centralwidget = QtWidgets.QWidget()
        self.centralwidget.setObjectName("centralwidget")
        self.formLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 40, 1181, 541))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(70, 10, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1197, 23))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.status_bar = QtWidgets.QStatusBar()
        self.status_bar.setObjectName("status_bar")
        self.setStatusBar(self.status_bar)

        self.retranslate_ui()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.pushButton.clicked.connect(self.show_html)
        self.html = QWebEngineView()

    def retranslate_ui(self):
        self.setWindowTitle(QtCore.QCoreApplication.translate("MainWindow", "MainWindow"))
        self.pushButton.setText(QtCore.QCoreApplication.translate("MainWindow", "PushButton"))

    def show_html(self):
        url = "file:///C:/Users/Administrator/PycharmProjects/stock_show_index/macd.html"
        print(url)
        self.html.load(QUrl(url))
        self.formLayout.addWidget(self.html)
        self.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mp = UiMainWindow()
    mp.show()
    sys.exit(app.exec_())
