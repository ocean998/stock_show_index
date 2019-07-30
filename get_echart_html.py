from typing import Dict
import macd_base as mb
from pyecharts import options as opts
from pyecharts.charts import Kline, Line, Bar
from pyecharts.globals import ThemeType
import os
"""
    获得指标展示的html结果
    接受股票代码和级别
"""


class StockData:
    # code 股票代码 cycle 级别
    def __init__(self, code: object, cycle: object) -> object:
        # code为带点的股票代码如 sz.000725,提取为没有点的 sz000725
        if cycle in ["15", "60"]:
            self.code = code[:2] + code[3:]
        else:
            self.code = code
        self.base_code = code
        self.cycle = cycle

        self.kline_path = str(os.getcwd() + '/param_html/kline.html').replace('\\','/')
        self.volume_path = str(os.getcwd() + '/param_html/volume.html').replace('\\','/')
        self.macd_path = str(os.getcwd() + '/param_html/macd.html').replace('\\','/')
        self.base_macd_path = str(os.getcwd() + '/param_html/base_macd.html').replace('\\','/')
        
        # 时间点列表
        self.time_point = []
        self.time_point_base = []
        self.data = None
        self.macd = None
        self.get_data()

    def get_name(self):
        d_name: Dict[str, str] = dict({'d': ' 日k线', 'w': ' 周k线', 'm': ' 月k线', '15': ' 15分钟k线', '60': ' 60分钟k线'})
        return "%s%s" % (self.code, d_name[self.cycle])

    def get_name_base(self):
        d_name: Dict[str, str] = dict({'15': ' 日k线', '60': ' 周k线', 'd': ' 月k线'})
        return "%s%s" % (self.code, d_name[self.cycle])

    def get_data(self):
        # 当前周期数据
        __macd = mb.MACD_INDEX(self.cycle)

        # 基础周期数据
        if self.cycle == '15':
            __base_macd = mb.MACD_INDEX('d')
        elif  self.cycle == '60':
            __base_macd = mb.MACD_INDEX('w')
        else:
            __base_macd = mb.MACD_INDEX('m')

        self.data = __macd.get_index(self.code)
        self.macd = __macd.get_macd(self.data)

        self.base_data = __base_macd.get_index(self.base_code)
        self.base_macd = __base_macd.get_macd(self.base_data)

        # 周期为60 15的 日期和时间之间添加换行
        if len(str(self.cycle)) == 2:
            for x in self.data['time']:
                self.time_point.append(str(x)[10:] + '\n' + str(x)[5:10])
        else:
            for x in self.data['time']:
                self.time_point.append(str(x))

        for x in self.base_data['time']:
            self.time_point_base.append(str(x)[2:])
        __macd.disconnect()
        __base_macd.disconnect()

    def kline(self):
        kl = self.data[['open', 'close', 'low', 'high']].values.tolist()
        ma5 = self.data['close'].rolling(window=5).mean()
        ma10 = self.data['close'].rolling(window=10).mean()
        ma_line: Line = (Line(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="1340px", height="200px"))
                         .add_xaxis(self.time_point)
                         .add_yaxis("五周期均线", ma5, is_smooth=True, is_symbol_show=False)
                         .add_yaxis("十周期均线", ma10, is_smooth=True, is_symbol_show=False)
                         .set_global_opts(title_opts=opts.TitleOpts(title="收盘均线"))
                         )

        # 另外写法 画带影线的交易k线，
        kline = Kline(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="1340px", height="200px"))
        kline.add_xaxis(self.time_point)
        kline.add_yaxis('交易K线图', kl, itemstyle_opts=opts.ItemStyleOpts(
            color="#ec0000",
            color0="#00da3c",
            border_color="#8A0000",
            border_color0="#008F28",
        )
                        )
        kline.set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(is_scale=True),
            title_opts=opts.TitleOpts(title=self.get_name()),
            #  横坐标缩放
            datazoom_opts=[opts.DataZoomOpts(range_start=60, range_end=100)], )
        # 设置缩放 datazoom_opts= [opts.DataZoomOpts(range_start=10, range_end=80,is_zoom_lock=False)],
        kline.overlap(ma_line)
        kline.render(self.kline_path)

    # 成交量
    def volume_bar(self):
        volume_data = []
        # 数据取整数
        if self.cycle in ['15', '60']:
            for i in range(1, len(self.data['volume'])):
                volume_data.append(int(self.data['volume'][i] / 100))
        else:
            for i in range(1, len(self.data['volume'])):
                volume_data.append(self.data['volume'][i])
        # 设置页面风格，设置长宽像素
        bar = (Bar(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="1300px", height="200px"))
               .add_xaxis(self.time_point)
               .add_yaxis("成交量", volume_data)
               .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
               .set_global_opts(title_opts=opts.TitleOpts(title=self.get_name()),
                                #  横坐标顺时针旋转90
                                xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                                #  横坐标缩放
                                datazoom_opts=[opts.DataZoomOpts(range_start=60, range_end=100)],
                                )
               )

        bar.render(self.volume_path)

    def macd_line(self):
        macd_line = (Line(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="1300px", height="200px"))
                     .add_xaxis(self.time_point)
                     .add_yaxis("dea(慢线)", self.macd['dea'], is_smooth=True, is_symbol_show=False)
                     .add_yaxis("dif(快线)", self.macd['dif'], is_smooth=True, is_symbol_show=False)
                     .add_yaxis("MACD(变化趋势)", self.macd['macd'], is_smooth=True, is_symbol_show=False,
                                areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
                     .set_global_opts(title_opts=opts.TitleOpts(title="MACD  " + self.get_name()),
                                      xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                                      #  横坐标缩放
                                      datazoom_opts=[opts.DataZoomOpts(range_start=60, range_end=100)],
                                      )
                     )
        macd_line.render(self.macd_path)

    def base_macd_line(self):
        macd_line = (Line(init_opts=opts.InitOpts(theme=ThemeType.DARK, width="660px", height="200px"))
                     .add_xaxis(self.time_point_base)
                     .add_yaxis("dea(慢线)", self.base_macd['dea'], is_smooth=True, is_symbol_show=False)
                     .add_yaxis("dif(快线)", self.base_macd['dif'], is_smooth=True, is_symbol_show=False)
                     .add_yaxis("MACD(变化趋势)", self.base_macd['macd'], is_smooth=True, is_symbol_show=False,
                                areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
                     .set_global_opts(title_opts=opts.TitleOpts(title="MACD  " + self.get_name_base()),
                                      xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                                      #  横坐标缩放
                                      datazoom_opts=[opts.DataZoomOpts(range_start=60, range_end=100)],
                                      )
                     )
        macd_line.render(self.base_macd_path)

if __name__ == '__main__':
    sd = StockData('sh.603726', 'm')
    sd.get_data()
    sd.kline()
    sd.volume_bar()
    sd.macd_line()
