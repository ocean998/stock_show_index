import numpy as np
from PyQt5.QtWidgets import   QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import macd_base as mb
import matplotlib
matplotlib.use("Qt5Agg")  # 声明使用QT5


class test_Figure(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        # 第一步：创建一个创建Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # 第二步：在父类中激活Figure窗口
        super(test_Figure, self).__init__(self.fig)  # 此句必不可少，否则不能显示图形

    # 第四步：就是画图，【可以在此类中画，也可以在其它类中画】

    def plotsin(self):
        self.axes0 = self.fig.add_subplot(111)
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2 * np.pi * t)
        self.axes0.plot(t, s)

    def plotcos(self):
        # 第三步：创建一个子图，用于绘制图形用，111表示子图编号，如matlab的subplot(1,1,1)
        self.axes = self.fig.add_subplot(1, 1, 1)
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2 * np.pi * t)
        self.axes.plot(t, s)


# 通过继承FigureCanvas类，使得该类既是一个PyQt5的Qwidget，
# 又是一个matplotlib的FigureCanvas，这是连接pyqt5与matplot
class MyFigure(FigureCanvas):
    def __init__(self,parent = None, width=14, height=4, dpi=200):
        # 创建一个Figure，注意：该Figure为matplotlib下的figure，
        # 不是matplotlib.pyplot下面的figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        # 第二步：在父类中激活Figure窗口 #此句必不可少，否则不能显示图形
        super(MyFigure, self).__init__(self.fig)
        # 第三步：创建一个子图，用于绘制图形用，111表示子图编号，如matlab的subplot(1,1,1)
        self.axes = self.fig.add_subplot(1, 1, 1)
        # 每次绘图都不保留上次的结果
        # self.axes.hold(False)
        FigureCanvas.__init__(self,self.fig)
        # self.setParent(parent)

        # 尺寸策略
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
    # 第四步：就是画图，【可以在此类中画，也可以在其它类中画】
    def plot_macd(self, code='sz000725', cycle='60'):
        self.fig.clear()
        self.axes = self.fig.add_subplot(1, 1, 1)
        mi = mb.MACD_INDEX(cycle)
        data = mi.get_index(code)
        self.macd = mi.get_macd(data)
        mi.disconnect()

        idx_macd = self.macd.loc[10:, ['time', 'dif', 'dea', 'macd']]
        idx_macd.set_index('time')
        idx_macd['zero'] = 0
        self.axes.plot(idx_macd.loc[:, 'time'],
                       idx_macd.loc[:, 'dif'], color='white')
        self.axes.plot(idx_macd.loc[:, 'time'],
                       idx_macd.loc[:, 'dea'], color='yellow')
        self.axes.plot(idx_macd.loc[:, 'time'],
                       idx_macd.loc[:, 'zero'], color='grey',alpha=0.3)

        self.axes.patch.set_color('black')
        for lab in self.axes.xaxis.get_ticklabels():
            lab.set_color('blue')
            lab.set_rotation(90)
            lab.set_fontsize(10)

    def plot_sin(self):
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2 * np.pi * t)
        self.axes.plot(t, s)


class MyPlot():
    def __init__(self):
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(1, 1, 1)

    def get_index(self, code=None, cycle='60'):
        mi = mb.MACD_INDEX(cycle)
        data = mi.get_index(code)
        self.macd = mi.get_macd(data)
        # self.macd.to_csv('C:/Users/Administrator/PycharmProjects/stock_show_index/macd.csv')
        mi.disconnect()

    def show(self):
        # plt.plot(self.macd)

        idx_macd = self.macd.loc[:, ['time', 'dif', 'dea', 'macd']]
        idx_macd.set_index('time')
        idx_macd['zero'] = 0

        idx_macd.set_index('time')
        # idx_macd.plot()  df1.index = range(len(df1))
        # idx_macd.index = range(len(idx_macd))
        idx_macd['idx'] = range(1,len(idx_macd)+1)

        print(idx_macd)
        # plt.plot(idx_macd.loc[:, 'idx'], idx_macd.loc[:, 'dif'], idx_macd.loc[:, 'idx'], idx_macd.loc[:, 'dea'])

        x = idx_macd.loc[:, 'idx']
        y = idx_macd.loc[:, 'dif']
        plt.plot(x, y,x,idx_macd.loc[:, 'dea'])
        plt.show()




if __name__ == '__main__':
    mp = MyPlot()
    mp.get_index('sz000725', '60')
    mp.show()
