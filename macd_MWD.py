import macd_base as mb


if __name__ == '__main__':
    # macd_m = mb.MACD_INDEX('m')
    # macd_m.save_golden('all')
    #
    # macd_w = mb.MACD_INDEX('w')
    # macd_w.save_golden('D:\\0_stock_macd\\_月K线金叉.csv')
    #
    # macd_d = mb.MACD_INDEX('d')
    # macd_d.save_golden('D:\\0_stock_macd\\_周K线金叉.csv')

    macd_d = mb.MACD_INDEX('60')
    macd_d.save_bing_golden('D:\\0_stock_macd\\_周K线金叉.csv')
    macd_d.save_bottom('D:\\0_stock_macd\\_周K线金叉.csv')