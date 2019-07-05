import pandas as pd

import stock_base
import analyze_base as ab
import macd_base as mb

from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar
from pyecharts.globals import ThemeType

# 获得指标展示的html结果
# 接受股票代码和级别

class Stock_Data():
    # code 股票代码 cycle 级别
    def __init__(self, code, cycle):
        self.code = code
        self.cycle = cycle
        # 时间点列表
        self.time_point = []

        self.get_data()

    def get_name(self):
        d_name = dict({'d':' 日k线', 'w':' 周k线', 'm':' 月k线', '15':' 15分钟k线', '60':' 60分钟k线'})
        return self.code + d_name[self.cycle]

    def get_data(self):
        macd = mb.MACD_INDEX(self.cycle)
        self.data = macd.get_index(self.code)
        self.macd = macd.get_MACD(self.data)
        # self.macd = macd.get_MACD(self.data)

        # 周期为60 15的 日期和时间之间添加换行
        if len(self.cycle) == 2:
            for x in self.data['time']:
                self.time_point.append(str(x)[10:] + '\n' + str(x)[5:10])
        else:
            for x in self.data['time']:
                self.time_point.append(str(x))

    def get_KLine(self):
        kl = self.data[['open', 'close', 'low', 'high']].values.tolist()
        ma5 = self.data['close'].rolling(window=5).mean()
        ma10 = self.data['close'].rolling(window=10).mean()
        maLine = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="1300px", height="300px" ))
                .add_xaxis(self.time_point)
                .add_yaxis("五周期均线", ma5, is_smooth=True,is_symbol_show=False)
                .add_yaxis("十周期均线", ma10, is_smooth=True,is_symbol_show=False)
                .set_global_opts(title_opts=opts.TitleOpts(title="收盘均线"))
        )

        # 另外写法 画带影线的交易k线，
        kline = Kline(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="1300px", height="300px") )
        kline.add_xaxis(self.time_point)
        kline.add_yaxis('交易K线图', kl,itemstyle_opts=opts.ItemStyleOpts(
                                            color="#ec0000",
                                            color0="#00da3c",
                                            border_color="#8A0000",
                                            border_color0="#008F28",
                                        )
                )
        kline.set_global_opts(
                    xaxis_opts=opts.AxisOpts(is_scale=True),
                    yaxis_opts=opts.AxisOpts(is_scale=True,
                                             splitarea_opts=opts.SplitAreaOpts(is_show=True,
                                                                               areastyle_opts=opts.AreaStyleOpts(opacity=1))),
                    title_opts=opts.TitleOpts(title=self.get_name()),
                    #  横坐标缩放
                    datazoom_opts=[opts.DataZoomOpts()], )

        kline.overlap(maLine)
        kline.render("K线.html")

    # 成交量
    def get_volume_bar(self):
        volume_data = []
        # 数据取整数
        for i in range(1,len(self.data['volume'])):
            volume_data.append(int( self.data['volume'][i]/100 ))
        bar = (
                # 设置页面风格，设置长宽像素
                Bar( init_opts=opts.InitOpts(theme=ThemeType.DARK, width="1300px", height="300px" ))
                    .add_xaxis(self.time_point)
                    .add_yaxis("成交量",volume_data)
                    .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                    .set_global_opts(title_opts=opts.TitleOpts(title=self.get_name()),
                                    #  横坐标顺时针旋转90
                                    xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                                    #  横坐标缩放
                                    datazoom_opts=[opts.DataZoomOpts()],
                                     )
                )

        bar.render("volume.html")

    # macd 线
    def get_MACD_line(self):
        macd_Line = (
            Line(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="1300px", height="300px" ))
                .add_xaxis(self.time_point)
                .add_yaxis("dea(慢线)", self.macd['dea'], is_smooth=True, is_symbol_show=False)
                .add_yaxis("dif(快线)", self.macd['dif'], is_smooth=True, is_symbol_show=False)
                .add_yaxis("MACD(变化趋势)", self.macd['macd'], is_smooth=True, is_symbol_show=False,
                                                areastyle_opts=opts.AreaStyleOpts(opacity=0.5) )
                .set_global_opts(title_opts=opts.TitleOpts(title="MACD  " + self.get_name()),
                                 xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                                 #  横坐标缩放
                                 datazoom_opts=[opts.DataZoomOpts()],
                                 )
        )
        macd_Line.render("macd.html")

if __name__ == '__main__':
    sd = Stock_Data('sz.002006', '15')
    sd.get_KLine()
    sd.get_volume_bar()
    sd.get_MACD_line()