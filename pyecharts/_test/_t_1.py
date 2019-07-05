# coding:utf-8
import baostock as bs
import pandas as pd

import stock_base
import analyze_base as ab
import macd_base as mb

from pyecharts import options as opts
from pyecharts.charts import Kline, Bar
# 内置主题类型可查看 pyecharts.globals.ThemeType
from pyecharts.globals import ThemeType

macd_d = mb.MACD_INDEX('60')

df = macd_d.get_index('sz.000725')
print(df)
# 成交量
z = []

def volume_percent(data: pd.DataFrame = None):
    low_min = float( data['low'].min() )
    vol_max = float(data['volume'].max())
    v = []
    for x in data['volume']:
        print(x)
        v.append(float(x) /100)
    return v
vol = volume_percent(df)
print(vol)
print(len(vol))


# 成交量相对值计算，用于显示成交量将对高低变化，
# 其最高值等于k线列表中的最小值


# 时间轴
y = []
for x in df['time']:
    str(x)[0:10]+'\n'+str(x)[10:]
    y.append(str(x)[10:]+'\n'+str(x)[5:10])

print(len(y))
df = df[['open', 'high', 'low', 'close']]

xx = df.values.tolist()

# ,yaxis_index=1, is_add_yaxis=True
def Kline_bar() -> Bar:
    bar = (
        Bar(init_opts=opts.InitOpts(width="1600px",height="400px"))
        .add_xaxis(y)
        .add_yaxis( "商家A", vol )
        .extend_axis(
            yaxis=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(formatter="{value} °C"),
            )
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
                        title_opts=opts.TitleOpts(title="Bar-DataZoom（slider-水平）"),
                        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-90)),
                        datazoom_opts=[opts.DataZoomOpts()],) )


    # kk = Kline().add_xaxis(y).add_yaxis('Kline', xx,yaxis_index=1)
    c = (Kline()
         .add_xaxis(y)
         .add_yaxis("kline", xx, yaxis_index=1)
         .set_global_opts(title_opts=opts.TitleOpts(title="Overlap-bar+line（双 Y 轴）"),
                          datazoom_opts=[opts.DataZoomOpts()], ))
    c.render("ccccc.html")
    bar.overlap(c)
    return bar


def kline_datazoom_slider() -> Kline:
    c = (Kline()
        .add_xaxis(y)
        .add_yaxis("kline", xx)
        .set_global_opts(title_opts=opts.TitleOpts(title="Overlap-bar+line（双 Y 轴）"),
                            datazoom_opts=[opts.DataZoomOpts()],width = 900))

    return c

bb = Kline_bar()
bb.render("bbb.html")
# yy = kline_datazoom_slider()
# yy.render("kkk.html")
# #
# line = Bar().add_xaxis(y).add_yaxis("商家A", vol, yaxis_index=1)
# # line.render("bbb.html")
# yy.overlap(bb)
# yy.render("abc.html")
