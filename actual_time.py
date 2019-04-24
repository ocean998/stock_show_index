import requests
import pandas as pd



class MACD_Error(Exception):
    """"各函数返回异常结果时抛出的异常"""

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg



def get_min_index(code, jb):
    '''获取实时数据，60分钟,15分钟'''
    url = 'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=####&scale=$$$$&ma=no&datalen=64'
    url2 = url.replace('####', code)
    code_url = url2.replace('$$$$', jb)
    resp = requests.post(code_url).text
    print(code_url)
    if len(resp) < 10:
        raise MACD_Error('url获取数据失败！')
    print(resp)
    txt = resp[2:len(resp) - 2]

    df_rst = pd.DataFrame( columns=('date', 'close', 'volume') )

    # 解析网页返回，格式如下
    # [{day: "2019-03-14 09:45:00", open: "3.890", high: "3.960", low: "3.870", close: "3.960", volume: "123837211"},
    #  {day: "2019-03-14 10:00:00", open: "3.950", high: "3.960", low: "3.880", close: "3.890", volume: "119944347"}]

    rst = []
    point = 0
    try:
        for data in txt.split('},{'):
            for item in data.split(','):
                if item.split(':')[0] == 'day':
                    date = item.split(':')[1]+':'+item.split(':')[2]
                    rst.append(date[1:])
                if item.split(':')[0] == 'close':
                    rst.append(float(item.split(':')[1][1:-1]))
                if item.split(':')[0] == 'volume':
                    rst.append(int(item.split(':')[1][1:-1]))
                if len(rst) == 3:
                    point += 1
                    df_rst.loc[ point ] = rst
                    rst.clear()
    except:
        raise MACD_Error('rul 结果解析错误！')
    print(df_rst)


# http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz000725&scale=15&ma=no&datalen=5
# http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sz00725&scale=15&ma=no&datalen=16
if __name__ == '__main__':
    get_min_index('sz000725', str(15))
