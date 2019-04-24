import analyze_base as ab
import pandas as pd
import os
import macd_base as mb


if __name__ == '__main__':
    macd_60 = mb.MACD_INDEX('60')
    # macd_60.set_time('2018-06-01','2018-12-11')

    df = macd_60.get_index('sz.000897')
    print("df"*9)
    print(df)
    df2 = macd_60.get_MACD(df)
    # 取完macd下面判断各种选股条件
    # 底背离
    # dbl_rst = ab.analyze_bottom(df2, True)

    # 即将0轴下金叉，
    gold = ab.analyze_bing_golden(df2,True)

    # os.system('pause')
    # python C:\Users\Administrator\PycharmProjects\STOCK\macd_bottom_deviate.py