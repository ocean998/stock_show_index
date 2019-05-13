from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import macd_base as mb

import pandas as pd

import matplotlib as mpl

#创建一个matplotlib图形绘制类
class MyFigure(FigureCanvas):
    def __init__(self,width=5, height=4, dpi=100):
        #第一步：创建一个创建Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #第二步：在父类中激活Figure窗口
        super(MyFigure,self).__init__(self.fig) #此句必不可少，否则不能显示图形
        #第三步：创建一个子图，用于绘制图形用，111表示子图编号，如matlab的subplot(1,1,1)
        self.axes = self.fig.add_subplot(1,1,1)
    #第四步：就是画图，【可以在此类中画，也可以在其它类中画】
    def plot_macd(self, code = 'sz000725', cycle = '60'):
        self.fig.clear()
        self.axes0 = self.fig.add_subplot(1,1,1)
        mi = mb.MACD_INDEX(cycle)
        data = mi.get_index(code)
        self.macd = mi.get_MACD(data)
        # self.macd.to_csv(r'C:\Users\Administrator\PycharmProjects\stock_show_index\000725MACD.scv' ,\
        #                       index=False, header=True, encoding='utf-8')
        mi.disconnect()

        idx_macd = self.macd.loc[:, ['time', 'dif', 'dea']]
        idx_macd.set_index('time')
        plt.plot(idx_macd.loc[:, 'time'], idx_macd.loc[:, 'dif'], idx_macd.loc[:, 'time'], idx_macd.loc[:, 'dea'])
        plt.show()


class MyPlot():
    def __init__(self):
        self.fig =  plt.figure( )
        self.ax = self.fig.add_subplot( 1, 1, 1 )

    def get_index( self, code = None, cycle = '60' ):
        mi = mb.MACD_INDEX(cycle)
        data = mi.get_index(code)
        self.macd = mi.get_MACD(data)
        mi.disconnect()


    def show( self ):
        # plt.plot(self.macd)
        idx_macd = self.macd.loc[:, ['time', 'dif', 'dea'] ]
        idx_macd.set_index('time')
        # idx_macd.plot()

        plt.plot(idx_macd.loc[:,'time'], idx_macd.loc[:,'dif'], idx_macd.loc[:,'time'], idx_macd.loc[:,'dea'] )
        plt.show()

if __name__ == '__main__':
    mp = MyPlot()
    mp.get_index('sz000725', '60')
    mp.show()