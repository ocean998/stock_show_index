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
        # self.axes = self.fig.add_subplot(111)
    #第四步：就是画图，【可以在此类中画，也可以在其它类中画】
    def plot_macd(self, macd = None):
        self.fig.clear()
        self.axes0 = self.fig.add_subplot(1,1,1)
        # self.axes0.show()

class MyPlot():
    def __init__(self):
        self.fig =  plt.figure( )
        self.ax = self.fig.add_subplot( 1, 1, 1 )

    def get_index( self, code = None, cycle = '60' ):
    def show( self ):
        plt.show()

if __name__ == '__main__':
    mp = MyPlot()
    plt.show()