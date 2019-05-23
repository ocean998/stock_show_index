
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ListWidget(QListWidget):
	def clicked(self,item):
		QMessageBox.information(self, "ListWidget", "你选择了: "+item.text() )

if __name__ == '__main__':
	app = QApplication(sys.argv)
	listWidget  = ListWidget()
	listWidget.resize(300,120)
	listWidget.addItem("Item 1");
	listWidget.addItem("Item 2");
	listWidget.addItem("Item 3");
	listWidget.addItem("Item 4");
	listWidget.setWindowTitle('QListwidget 例子')
	listWidget.itemClicked.connect(listWidget.clicked)
	listWidget.show()
	sys.exit(app.exec_())


# -*- coding: utf-8 -*-

# import tushare as ts
# import matplotlib.pyplot as plt
# from datetime import datetime
#
# data = ts.get_hist_data('600848',start='2018-03-01',end='2018-03-31')
# # 对时间进行降序排列
# data = data.sort_index()
# print(data)
# xs = [datetime.strptime(d, '%Y-%m-%d').toordinal() for d in data.index ]
# print(xs)
# plt.plot_date( xs , data['open'] , 'b-')
# plt.gcf().autofmt_xdate()  # 自动旋转日期标记
# plt.show()
