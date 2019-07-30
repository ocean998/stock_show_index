import UI_stock_show as UI
import macd_base as mb
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, QUrl
import stock_base as stb
from PyQt5.QtWebEngineWidgets import QWebEngineView
import get_echart_html as geh
import os, sys


# 多线程 取数据计算macd 避免界面无响应
class MacdCalc(QThread):

    def __init__(self):
        super().__init__()
        self.set_init()

    def set_init(self):
        self.macd_m = None
        self.para_m = ''

        self.macd_w = None
        self.para_w = ''

        self.macd_d = None
        self.para_d = ''

    # 初始化月 周 日 macd
    def set_macd_m(self, what_macd, what_para):
        self.macd_m = what_macd
        self.para_m = what_para

    def set_macd_w(self, what_macd, what_para):
        self.macd_w = what_macd
        self.para_w = what_para

    def set_macd_d(self, what_macd, what_para):
        self.macd_d = what_macd
        self.para_d = what_para

    def __del__(self):
        self.wait()

    def run(self):
        if self.macd_m is not None:
            print('month   :', self.para_m)
            self.macd_m.save_golden(self.para_m)
            self.macd_m.disconnect()

        if self.macd_w is not None:
            print('week   :', self.para_w)
            self.macd_w.save_golden(self.para_w)
            self.macd_w.disconnect()

        if self.macd_d is not None:
            print("day   :", self.macd_d)
            self.macd_d.save_golden(self.para_d)
            self.macd_d.disconnect()
        self.set_init()

class StockUi(QtWidgets.QMainWindow, UI.Ui_MainWindow):
    """根据界面、逻辑分离原则 初始化界面部分"""

    def __init__(self, parent=None):
        super(StockUi, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.init_mwd)
        self.pushButton_2.clicked.connect(self.init_d)
        self.pushButton_3.clicked.connect(self.init_wd)
        self.pushButton_4.clicked.connect(self.conditions)
        self.pushButton_5.clicked.connect(self.plot_index)
        self.listWidget.itemClicked.connect(self.list_clicked)
        self.thread = MacdCalc()
        self.html_kline = QWebEngineView()
        self.html_volume = QWebEngineView()
        self.html_macd = QWebEngineView()
        self.html_base = QWebEngineView()
        self.csv_path = os.getcwd() + '\\param_macd_csv\\'
        self.jb = '60'
        self.set_init_conditions()

    def list_clicked(self, item):
        self.lineEdit.clear()
        code = item.text()
        self.lineEdit.setText(code)

        """
            显示指标图形
        """
    def plot_index(self):
        if len(self.lineEdit.text().strip()) < 10:
            print('错误提示框')
        code = self.lineEdit.text().split(' ')[0]
        code = code[code.find('s'):]

        if self.radioButton_6.isChecked():
            # print('radioButton_6 60 分钟级别')
            self.jb = '60'

        if self.radioButton_7.isChecked():
            # print('radioButton_7 15 分钟级别')
            self.jb = '15'

        if self.radioButton_12.isChecked():
            # print('radioButton_12 日线级别')
            self.jb = 'd'

        charts = geh.StockData(code, self.jb)
        charts.kline()
        charts.volume_bar()
        charts.macd_line()
        charts.base_macd_line()

        self.html_kline.load(QUrl(charts.kline_path))
        print(charts.kline_path)
        self.html_volume.load(QUrl(charts.volume_path))
        self.html_macd.load(QUrl(charts.macd_path))
        self.html_base.load(QUrl(charts.base_macd_path))

        self.formLayout.addWidget(self.html_kline)
        self.formLayout_2.addWidget(self.html_volume)
        self.formLayout_3.addWidget(self.html_macd)
        self.formLayout_4.addWidget(self.html_base)
        self.show()

    def init_mwd(self):
        """ 全部股票代码选出月线金叉，在此基础上选周线金叉，在此基础上再选日线金叉"""
        self.statusbar.showMessage('金叉初始化(月周日)')
        macd_m = mb.MACD_INDEX('m')
        macd_m.signal.send.connect(self.macd_progress)

        macd_w = mb.MACD_INDEX('w')
        macd_w.signal.send.connect(self.macd_progress)

        macd_d = mb.MACD_INDEX('d')
        macd_d.signal.send.connect(self.macd_progress)

        self.thread.set_macd_m(macd_m, 'all')
        self.thread.set_macd_w(macd_w, self.csv_path+'_月K线金叉.csv')
        self.thread.set_macd_d(macd_d, self.csv_path+'_周K线金叉.csv')
        self.thread.start()

    def init_wd(self):
        """ 全部股票代码选出周线金叉，在此基础上再选日线金叉"""
        print('全部股票代码选出周线金叉，在此基础上再选日线金叉')
        self.statusbar.showMessage('金叉初始化(周日)')
        macd_w = mb.MACD_INDEX('w')
        macd_w.signal.send.connect(self.macd_progress)

        macd_d = mb.MACD_INDEX('d')
        macd_d.signal.send.connect(self.macd_progress)

        self.thread.set_macd_w(macd_w, 'all')
        self.thread.set_macd_d(macd_d, self.csv_path+'_周K线金叉.csv')
        self.thread.start()

    def init_d(self):
        """全部股票代码选出日线金叉"""
        self.statusbar.showMessage('金叉初始化(日)')
        macd_d = mb.MACD_INDEX('d')
        macd_d.signal.send.connect(self.macd_progress)

        self.thread.set_macd_d(macd_d, 'all')
        self.thread.start()

    def set_init_conditions(self):
        self.radioButton_2.setChecked(True)
        self.radioButton_6.setChecked(True)
        self.radioButton_9.setChecked(True)

    """开始选股"""
    def conditions(self):
        # noinspection PyGlobalUndefined
        global path
        self.statusbar.showMessage('正在计算...')
        self.listWidget.clear()
        if self.radioButton.isChecked():
            # print('radioButton 月线')
            path = self.csv_path+'_月K线金叉.csv'

        if self.radioButton_2.isChecked():
            # print('radioButton_2 周线')
            path = self.csv_path+'_周K线金叉.csv'

        if self.radioButton_3.isChecked():
            # print('radioButton_3 日线')
            path = self.csv_path+'_日K线金叉.csv'

        if self.radioButton_6.isChecked():
            # print('radioButton_6 60 分钟级别')
            self.jb = '60'

        if self.radioButton_7.isChecked():
            # print('radioButton_7 15 分钟级别')
            self.jb = '15'

        if self.radioButton_12.isChecked():
            # print('radioButton_12 日线级别')
            self.jb = 'd'

        macd_jb = mb.MACD_INDEX(self.jb)
        macd_jb.signal.send.connect(self.macd_progress)

        if self.radioButton_8.isChecked():
            # print('radioButton_8 已金叉')
            macd_jb.save_golden(path)

        if self.radioButton_9.isChecked():
            # print('radioButton_9 即将金叉 ')
            macd_jb.save_bing_golden(path)

        if self.radioButton_10.isChecked():
            # print('radioButton_10 底背离')
            macd_jb.save_bottom(path)

        if self.radioButton_11.isChecked():
            print('radioButton_11 刚刚金叉')
            macd_jb.save_golden_now(path)

        macd_jb.disconnect()

        self.label.setText('  ')
        stock_code = stb.get_stock_code(macd_jb.save_name)
        cnt = stock_code.shape[0]
        self.statusbar.showMessage('计算完成, 共选出 ' + str(cnt) + ' 只')

        all_stock = stb.get_market_code('all')

        for x in range(cnt):
            code = stock_code.iloc[x]['stock_code']
            for i in range(1, all_stock.shape[0]):
                if all_stock.iloc[i]['stock_code'].find(code[3:]) > 0:
                    rst = code + ' ' + all_stock.iloc[i]['stock_name']
                    self.listWidget.addItem(rst)

    def macd_progress(self, curr):
        self.label.setText(curr)
        QtWidgets.QApplication.processEvents()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MP = StockUi()

    MP.setWindowTitle(' ~^_^~ MACD指标选股')
    MP.show()
    sys.exit(app.exec_())
