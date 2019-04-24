import baostock as bs
import pandas as pd
import stock_base
import analyze_base as ab
import requests
from PyQt5.QtCore import pyqtSignal,QObject

class MACD_Error(Exception):
    """"各函数返回异常结果时抛出的异常"""

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

class QTypeSignal(QObject):
    # 定义一个信号
    send = pyqtSignal(str)

    def __init__(self):
        super(QTypeSignal, self).__init__()

    def sendmsg(self,msg):
        # 发射信号
        self.send.emit(msg)

class MACD_INDEX:
    '''
            计算macd指标，需要初始化周期级别
    '''
    signal = None
    def __init__(self, jb='d'):
        '''
                根据周期初始化 开始时间，结束时间，股票列表
        '''
        # 定义信号量，用于发送计算过程的百分比,str为函数说明和分母，int为分子
        self.signal = QTypeSignal()
        #### 登陆系统 ####
        lg = bs.login()
        # 显示登陆返回信息
        if int(lg.error_code) == 0:
            self.status = '远程登录成功'
        else:
            self.status = '远程登录失败'
            print('baostock 远程登录失败:', lg.error_msg)
            return
        # df = stock_base.get_stock_code('sz')
        self.jb = jb
        date = stock_base.get_start_time(jb)
        self.begin = date[0]
        self.end = date[1]

        print('k线级别:', self.jb, '\t开始时间:', self.begin, '\t结束时间:', self.end)

    def disconnect( self ):
        lg = bs.logout()
        if int(lg.error_code) == 0:
            self.status = '退出成功'
        else:
            self.status = '退出失败'

    def set_time(self, begin='2019', end='2019'):
        '''重新设置开始时间和结束时间'''
        if begin != '2019':
            self.begin = begin
        if end != '2019':
            self.end = end
        print('k线级别:', self.jb, '\t新设置的开始时间:', self.begin, '\t结束时间:', self.end)

    def get_min_index(self, code, jb):
        '''获取实时数据，60分钟,15分钟'''
           # 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz000725&scale=15&ma=no&datalen=64'
        # [{day:"2019-04-10 13:45:00",open:"3.930",high:"3.940",low:"3.910",close:"3.910",volume:"20579496"},
        # {day:"2019-04-10 14:00:00",open:"3.910",high:"3.930",low:"3.910",close:"3.930",volume:"15421922"}
        url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=####&scale=$$$$&ma=no&datalen=64'
        mycode = code.replace('.','')
        url2 = url.replace('####', mycode)
        code_url = url2.replace('$$$$', jb)
        resp = requests.post(code_url).text

        if len(resp) < 10:
            raise MACD_Error('url获取数据失败！')

        txt = resp[2:len(resp) - 2]
        # DataFrame 初始化和添加一行数据
        df_rst = pd.DataFrame(columns=('time', 'close', 'volume'))

        rst = []
        point = 0
        try:
            for data in txt.split('},{'):
                for item in data.split(','):
                    if item.split(':')[0] == 'day':
                        date = item.split(':')[1] + ':' + item.split(':')[2]
                        rst.append(date[1:])
                    if item.split(':')[0] == 'close':
                        rst.append(float(item.split(':')[1][1:-1]))
                    if item.split(':')[0] == 'volume':
                        rst.append(int(item.split(':')[1][1:-1]))
                    if len(rst) == 3:
                        point += 1
                        df_rst.loc[point] = rst
                        rst.clear()
        except BaseException:
            raise MACD_Error('rul 结果解析错误！')
        return df_rst

    def get_index(self, code):
        '''
                根据周期初始化 开始时间，结束时间，获取远程指标数据
        '''
        # 要获取的指标数据列表
        # d=日k线、w=周、m=月、5=5分钟、15=15分钟、30=30分钟、60=60分钟k线数据
        self.code = code
        if self.jb in ['d', 'w', 'm']:
            indexs = 'date,close,volume,amount,turn'
            rs = bs.query_history_k_data_plus(
                code,
                indexs,
                start_date=self.begin,
                end_date=self.end,
                frequency=self.jb,
                adjustflag="2")
            # 复权状态(1：后复权， 2：前复权，3：不复权）
            if rs.error_code != '0':
                raise MACD_Error(code + ':k线指标获取失败！' + rs.error_msg)

            data_list = []
            while (rs.error_code == '0') & rs.next():
                # 获取一条记录，将记录合并在一起
                # data_list[-1].append(float(data_list[-1][-1])/float(data_list[-1][-2]))
                data_list.append(rs.get_row_data())

            result = pd.DataFrame(data_list, columns=rs.fields)
            # 修改列名 date-->time
            if self.jb in ['d', 'w', 'm']:
                result.rename(columns={'date': 'time'}, inplace=True)
            return result

        if self.jb in [ '60', '15'  ]:
            try:
                rst = self.get_min_index(self.code,str(self.jb))
            except MACD_Error:
                raise MACD_Error('url获取数据失败！')
            else:
                return rst


    def get_MACD(self, data, sema=12, lema=26, m_ema=9):
        '''
            根据股票代码计算macd结果，设置macd属性
            data是包含高开低收成交量的标准dataframe
            sema,lema,m_ema分别是macd的三个参数
        '''
        if data.shape[0] < 30:
            raise MACD_Error('K线数据少于30个周期，不计算MACD')
        xx = pd.DataFrame()
        xx['time'] = data['time']
        xx['volume'] = data['volume']
        xx['dif'] = data['close'].ewm(adjust=False,
                                      alpha=2 / (sema + 1),
                                      ignore_na=True).mean() - data['close'].ewm(adjust=False,
                                                                                 alpha=2 / (lema + 1),
                                                                                 ignore_na=True).mean()

        xx['dea'] = xx['dif'].ewm(
            adjust=False, alpha=2 / (m_ema + 1), ignore_na=True).mean()

        xx['macd'] = 2 * (xx['dif'] - xx['dea'])

        ab.set_code(self.code)
        return xx

    def save_golden(self, market='all'):
        df_rst = pd.DataFrame(
            columns=(
                '类别',
                '股票代码',
                '日期',
                '快线强弱',
                '红柱数量',
                '大陆代码'))
        # print('\r', str(10 - i).ljust(10), end='')

        stock_code = stock_base.get_stock_code(market)

        if self.jb == 'm':
            pre = '月K线金叉'
        if self.jb == 'd':
            pre = '日K线金叉'
        if self.jb == 'w':
            pre = '周K线金叉'
        if self.jb == '60':
            pre = '60分钟K线金叉'
        if self.jb == '15':
            pre = '15分钟K线金叉'

        self.save_name = 'D:\\0_stock_macd\\' + '_' + pre + '.csv'
        line = 0
        cnt = stock_code.shape[0]
        print('开始计算,总数 ' + str(cnt) + ' 只')
        for x in range(cnt):
            pre2 = ', 剩余 ' + str(cnt - x - 1) + ' 只，完成 {:.2f}%'.format(
                (x + 1) * 100 / cnt) + ' 选出 ' + str(line) + ' 只'
            print('\r', pre, pre2.ljust(10), end='')
            self.signal.sendmsg(pre+', 总数 ' + str(cnt) + ' 只'+pre2)
            try:
                df = self.get_index(stock_code.iloc[x]['stock_code'])
            except MACD_Error:
                continue

            try:
                df2 = self.get_MACD(df)
            except MACD_Error:
                continue

            try:
                # 金叉且开口向上
                df3 = ab.analyze_golden_red(df2)
            except ab.AnalyzeError:
                continue
            else:

                line += 1
                df_rst.loc[line] = df3

        print('\n\t\t', '完成！请打开：', self.save_name, '\n')
        df_rst.to_csv(self.save_name, index=False, header=True,encoding='utf-8')

    def save_bing_golden(self, market='all'):
        """周线选股时，日线即将金叉，或者已经金叉的日线级别增强判断"""
        df_rst = pd.DataFrame(
            columns=(
                '类别',
                '股票代码',
                '日期',
                '快线强弱',
                '红柱数量',
                '大陆代码'))
        # print('\r', str(10 - i).ljust(10), end='')

        stock_code = stock_base.get_stock_code(market)

        if self.jb == 'm':
            pre = '月K线(即将)金叉'
        if self.jb == 'd':
            pre = '日K线(即将)金叉'
        if self.jb == 'w':
            pre = '周K线(即将)金叉'
        if self.jb == '60':
            pre = '60分钟K(即将)线金叉'
        if self.jb == '15':
            pre = '15分钟K线(即将)金叉'

        self.save_name = 'D:\\0_stock_macd\\' + '_' + pre + '.csv'
        line = 0
        cnt = stock_code.shape[0]
        print('开始计算,总数 ' + str(cnt) + ' 只')
        for x in range(cnt):
            pre2 = ', 剩余 ' + str(cnt - x - 1) + ' 只，完成 {:.2f}%'.format(
                (x + 1) * 100 / cnt) + ' 选出 ' + str(line) + ' 只'
            print('\r', pre, pre2.ljust(10), end='')
            self.signal.sendmsg(pre+', 总数 ' + str(cnt) + ' 只'+pre2)
            try:
                df = self.get_index(stock_code.iloc[x]['stock_code'])
            except MACD_Error:
                continue

            try:
                df2 = self.get_MACD(df)
            except MACD_Error:
                continue

            try:
                df3 = ab.analyze_bing_golden(df2)
            except ab.AnalyzeError:
                continue
            else:
                line += 1
                df_rst.loc[line] = df3

        print('\n\t\t', '完成！请打开：', self.save_name, '\n')
        df_rst.to_csv(self.save_name, index=False, header=True,encoding='utf-8')

    def save_golden_now(self, market='all', isprt=False):
        df_rst = pd.DataFrame(
            columns=(
                '类别',
                '股票代码',
                '日期',
                '快线强弱',
                '将要金叉周期',
                '大陆代码'))
        try:
            stock_code = stock_base.get_stock_code(market)
        except sb.stkBaseError:
            return
        if self.jb == 'm':
            pre = '月K线(刚刚)金叉'
        if self.jb == 'd':
            pre = '日K线(刚刚)金叉'
        if self.jb == 'w':
            pre = '周K线(刚刚)金叉'
        if self.jb == '60':
            pre = '60分钟K线(刚刚)金叉'
        if self.jb == '15':
            pre = '15分钟K线(刚刚)金叉'

        self.save_name = 'D:\\0_stock_macd\\' + '_' + pre + '.csv'
        line = 0
        cnt = stock_code.shape[0]
        print('开始计算,总数 ' + str(cnt) + ' 只')
        for x in range(cnt):
            pre2 = ', 剩余 ' + str(cnt - x - 1) + ' 只，完成 {:.2f}%'.format(
                (x + 1) * 100 / cnt) + ' 选出 ' + str(line) + ' 只'
            print('\r', pre, pre2.ljust(10), end='')
            self.signal.sendmsg(pre+', 总数 ' + str(cnt) + ' 只'+pre2)
            try:
                df = self.get_index(stock_code.iloc[x]['stock_code'])
            except MACD_Error:
                continue

            try:
                df2 = self.get_MACD(df)
            except MACD_Error:
                continue

            try:
                df3 = ab.analyze_golden_now(df2, isprt)
            except ab.AnalyzeError:
                pass
            else:
                line += 1
                df_rst.loc[line] = df3
                continue

            try:
                df3 = ab.analyze_golden(df2, isprt)
            except ab.AnalyzeError:
                continue
            else:
                line += 1
                df_rst.loc[line] = df3

        print('\n \t\t', '完成！\n')
        df_rst.to_csv(self.save_name, index=False, header=True,encoding='utf-8')

    def save_bottom(self, market='all', isprt=False):
        '''保存底背离股票代码'''
        df_rst = pd.DataFrame(
            columns=(
                '指标类别',
                '股票代码',
                '日期',
                '快线强弱',
                '首次金叉时间',
                '大陆代码'))
        # market不是'all'，从传入的文件取代码
        try:
            stock_code = stock_base.get_stock_code(market)
        except stock_base.stkBaseError:
            print(stock_base.stkBaseError)

        if self.jb == 'm':
            pre = '月K线 即将底背离'
        if self.jb == 'd':
            pre = '日K线 即将底背离'
        if self.jb == 'w':
            pre = '周K线 即将底背离'
        if self.jb == '60':
            pre = '60分钟K线 即将底背离'
        if self.jb == '15':
            pre = '15分钟K线 即将底背离'

        self.save_name = 'D:\\0_stock_macd\\' + '_' + pre + '.csv'
        line = 0
        cnt = stock_code.shape[0]
        print('开始计算,总数 ' + str(cnt) + ' 只')
        for x in range(cnt):
            pre2 = ', 剩余 ' + str(cnt - x - 1) + ' 只，完成 {:.2f}%'.format(
                (x + 1) * 100 / cnt) + ' 选出 ' + str(line) + ' 只'
            print('\r', pre, pre2.ljust(10), end='')
            self.signal.sendmsg(pre+', 总数 ' + str(cnt) + ' 只'+pre2)
            try:
                df = self.get_index(stock_code.iloc[x]['stock_code'])
            except MACD_Error:
                continue

            try:
                df2 = self.get_MACD(df)
            except MACD_Error:
                continue
            try:
                dbl_rst = ab.analyze_bottom(df2, isprt)
            except ab.AnalyzeError:
                continue
            else:
                line += 1
                df_rst.loc[line] = dbl_rst

        print('\n \t\t', '完成！\n')
        df_rst.to_csv(self.save_name, index=False, header=True,encoding='utf-8')

    def save_top(self, market='all', isprt=False):
        df_rst = pd.DataFrame(
            columns=(
                '类别',
                '股票代码',
                '日期',
                '快线强弱',
                '将要金叉周期',
                '大陆代码'))
        # market不是'all'，从传入的文件取代码
        stock_code = stock_base.get_stock_code(market)

        if self.jb == 'm':
            pre = '月K线 顶背离'
        if self.jb == 'd':
            pre = '日K线 顶背离'
        if self.jb == 'w':
            pre = '周K线 顶背离'
        if self.jb == '60':
            pre = '60分钟K线 顶背离'
        if self.jb == '15':
            pre = '15分钟K线 顶背离'

        self.save_name = 'D:\\0_stock_macd\\' + '_' + pre + '.csv'
        line = 0
        cnt = stock_code.shape[0]
        print('开始计算,总数 ' + str(cnt) + ' 只')
        for x in range(cnt):

            pre2 = ', 剩余 ' + str(cnt - x - 1) + ' 只，完成 {:.2f}%'.format(
                (x + 1) * 100 / cnt) + ' 选出 ' + str(line) + ' 只'
            print('\r', pre, pre2.ljust(10), end='')
            self.signal.sendmsg(pre+', 总数 ' + str(cnt) + ' 只'+pre2)
            try:
                df = self.get_index(stock_code.iloc[x]['stock_code'])
            except MACD_Error:
                continue

            try:
                df2 = self.get_MACD(df)
            except MACD_Error:
                continue
            df3 = self.analyze_top(df2, isprt)


if __name__ == "__main__":
    macd_60 = MACD_INDEX('60')
    macd_60.save_golden('D:\\0_stock_macd\\_日K线金叉.csv')

    # macd_15 = MACD_INDEX('15')
    # macd_15.save_golden('D:\\0_stock_macd\\_60分钟K线金叉.csv')

    # # 日线已经金叉，算60分钟即将金叉
    # macd_60 = MACD_INDEX('60')
    # # macd_60.save_bing_golden('D:\\0_stock_macd\\_周K线金叉.csv')
    # macd_60.save_bing_golden('D:\\0_stock_macd\\_日K线金叉.csv', False)

    # macd_60 = MACD_INDEX('60')
    # macd_60.set_time('2018-06-01', '2018-12-11')
    #
    # macd_60.save_bottom('all', False)

    # 周K线已经金叉，算日线即将金叉  # macd_d = MACD_INDEX('d')  #  #
    # macd_d.save_bing_golden('D:\\0_stock_macd\\_周K线金叉.csv')

    # stock_code = stock_base.get_stock_code('D:\\0_stock_macd\\_周K线金叉.csv')
    # # # cnt = stock_code.shape[0]

# 单只股票调试
