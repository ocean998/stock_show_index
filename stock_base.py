import pandas as pd
import datetime as dt
import tushare as ts


class stkBaseError(Exception):
    """"各函数返回异常结果时抛出的异常"""

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg


def get_start_time(period='d'):
    '''
        根据周期获取开始、结束时间段
        preiod 为周期 取值为
        d=日k线、w=周、m=月、5=5分钟、15=15分钟、30=30分钟、60=60分钟k线数据
    '''
    begend = []
    if period == 'd':
        begin = dt.datetime.now() + dt.timedelta(days=-90)
        begend.append(begin.strftime('%Y-%m-%d'))
        # begend.append('2019-02-12')
        begend.append(dt.datetime.now().strftime('%Y-%m-%d'))

    elif period == 'w':
        begin = dt.datetime.now() + dt.timedelta(days=-400)
        begend.append(begin.strftime('%Y-%m-%d'))
        begend.append(dt.datetime.now().strftime('%Y-%m-%d'))

    elif period == 'm':
        begin = dt.datetime.now() + dt.timedelta(days=-1700)
        begend.append(begin.strftime('%Y-%m-%d'))
        begend.append(dt.datetime.now().strftime('%Y-%m-%d'))

    elif period == '15':
        begin = dt.datetime.now() + dt.timedelta(days=-10)
        begend.append(begin.strftime('%Y-%m-%d'))
        begend.append(dt.datetime.now().strftime('%Y-%m-%d'))

    elif period == '60':
        begin = dt.datetime.now() + dt.timedelta(days=-40)
        begend.append(begin.strftime('%Y-%m-%d'))
        end = dt.datetime.now()
        begend.append(end.strftime('%Y-%m-%d'))

    else:
        begin = dt.datetime.now() + dt.timedelta(days=-30)
        begend.append(begin.strftime('%Y-%m-%d'))
        begend.append(dt.datetime.now().strftime('%Y-%m-%d'))
    return begend


def get_rst_code(path=None):
    if path is None:
        return None
    df = pd.read_csv(path)

    code = []
    name = []

    for line in range(df.shape[0]):
        code.append(df.iloc[line]['大陆代码'])
        name.append(df.iloc[line]['日期'])
    try:
        data = {'stock_code': code, 'stock_name': name}
        return pd.DataFrame(data, columns=['stock_code', 'stock_name'])
    except BaseException:
        raise stkBaseError('get_rst_code error')


def set_market_code():
    pro = ts.pro_api(
        '3a225717090aa813ddf5d75c51b9d97349c8f0a38f8cea52e1a8fcff')
    # 查询当前所有正常上市交易的股票列表
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
    code = []
    codes = pd.DataFrame(columns=('stock_code', 'stock_name'))
    for i in range(1, data.shape[0]):
        code.append(data.iloc[i]['ts_code'][7:10].lower() +
                    '.' + data.iloc[i]['ts_code'][0:6])
        code.append(data.iloc[i]['name'])
        codes.loc[i] = code
        code.clear()
    codes.to_csv('股票代码.csv', index=False, header=True,encoding='utf_8')


def get_market_code(market):
    '''
            根据磁盘上的文件获得上海、深圳股票市场全部代码
            market='sz' 表示深圳股市代码，market='sh' 代表 上海
            返回pandas.DataFrame类型的代码和名称列表
        '''
    if market != 'all':
        return None

    try:
        df = pd.read_csv('股票代码.csv',encoding='utf_8')
        return df
    except BaseException:
        raise stkBaseError('get_rst_code error')


def get_stock_code(market=None):
    try:
        if market == 'all':
            # 	在本地原始文件中取股票代码代码
            rst = get_market_code(market)
        else:
            rst = get_rst_code(market)
    except stkBaseError:
        print(stkBaseError)
    else:
        return rst


if __name__ == "__main__":
    # df = stock_base.get_stock_code( 'D:\\0_stock_macd\\_月K线金叉.csv' )
    # # print( df )
    set_market_code()
    rst = get_market_code('all')
    print(rst)
    #
    # xx = get_stock_code('D:\\0_stock_macd\\_月K线金叉.csv')
    # print(xx)