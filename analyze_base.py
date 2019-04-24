'''分析macd指标的基础函数模块'''
import pandas as pd
# 当前的股票代码
CURR_CODE = ''


class AnalyzeError(Exception):
    """"各函数返回异常结果时抛出的异常"""

    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg


def set_code(code):
    global CURR_CODE
    CURR_CODE = code


def get_code():
    global CURR_CODE
    return CURR_CODE


def analyze_dead(macd, isprt=False):
    ''' macd最后一次交叉是死叉，才有返回值，返回包括 死叉日期，死叉后红柱数量，绿柱高度，快线高度
            save_golden方法计算完macd后调用，后续应继续调用判断 是否即将金叉的方法 analyze_bing_golden
    '''
    rst = pd.DataFrame(columns=[macd.columns.values])
    cnt_lv = 0
    cnt = macd.shape[0]
    if cnt < 30:
        raise AnalyzeError(get_code() + '，macd数据少于30周期,不判断死叉！')
    # isprt是否打印输入的macd数组，用于调试
    # if isprt:
    #     print(macd)
    # 如果当前macd红柱表示已经金叉，不判断直接返回
    if macd.iloc[-1]['macd'] > 0:
        raise AnalyzeError(get_code() + '，已经金叉！')
    for i in range(1, cnt - 1):
        # macd>0 为红柱，计数并向前找小于0的时间为金叉点
        if macd.iloc[-i]['macd'] < 0:
            cnt_lv += 1  # 绿柱计数
            continue
        else:
            rst = macd.iloc[-i + 1:].reset_index(drop=True)
            return rst
    raise AnalyzeError(get_code() + '，没有找到死叉！')


def analyze_bing_golden(macd, isprt=False):
    ''' 用于判断是否将要金叉macd已经死叉还未金叉，如果快线斜率在3个周期内发生金叉则返回
            macd死叉后的macd指标，pandas.DataFrame类型 save_golden方法计算完macd发生死叉后调用，
            零轴下死叉适用 frame.iloc[frame['test2'].idxmin()]['test3']
    '''

    rst = []
    try:
        dead_macd = analyze_dead(macd, isprt)
    except AnalyzeError:
        raise AnalyzeError(get_code() + ', 不用判断即将金叉')

    if dead_macd.iloc[-1]['dea'] > 0:
        raise AnalyzeError(get_code() + ', 零轴上，不用判断即将金叉')
    dead_len = dead_macd.shape[0]

    # 死叉macd为负值 所以取最小值
    idx_min = dead_macd['macd'].idxmin()
    # 绿线最低值发生在当前
    if dead_len == idx_min + 1:
        raise AnalyzeError(get_code() + ', 死叉后开口正在放大！')
    # 取最低点后的数据
    macd_jc = dead_macd.iloc[idx_min:].reset_index(drop=True)
    dead_len = macd_jc.shape[0]
    if isprt:
        print('\nMACD最低点后的数据是：\n')
        print(macd_jc)
    if dead_len > 3:
        x = []
        # 最低点后如果有3根以上的柱子再判断趋势，缩短y，加长n
        for idx in range(0, dead_len - 1):
            if macd_jc.iloc[idx]['macd'] - \
                    macd_jc.iloc[(idx + 1)]['macd'] >= 0:
                x.append('n')
            else:
                if isprt:
                    print(idx, ':', macd_jc.iloc[idx]['macd'],
                          '-', macd_jc.iloc[(idx + 1)]['macd'])
                x.append('y')
        if x[-1] == 'y':
            rst.append('即将金叉')
        if isprt:
            print('\nMACD最低点后的 趋势\n', x)
    else:
        # 不足4跟，最后一根比前面一根短
        if dead_macd.iloc[-1]['macd'] <= dead_macd.iloc[-2]['macd']:
            rst.append('即将金叉')

    if len(rst) == 1:
        rst.append(get_code().split('.')[1])
        rst.append(dead_macd.iloc[0]['time'])
        rst.append(dead_macd.iloc[-1]['macd'])
        rst.append(dead_macd.iloc[-2]['macd'])
        rst.append(get_code())
        return rst
    else:
        raise AnalyzeError(get_code() + ', 不是即将金叉！')


def analyze_golden_red(macd, isprt=False):
    '''最后3个周期是红柱且越来越长'''
    try:
        rst = analyze_golden(macd, isprt)
    except AnalyzeError:
        raise AnalyzeError(get_code() + '，不是金叉！')
    # 3根红柱以上，判断最后3根越来越长
    if rst[4] > 3:
        if macd.iloc[-1]['macd'] > macd.iloc[-2]['macd'] > macd.iloc[-3]['macd']:
            return rst
        else:
            raise AnalyzeError(get_code() + '，金叉后红柱没有持续变长！')
    else:
        return rst

def analyze_golden_now(macd, isprt=False):
    '''刚刚金叉，红柱出现1--2根'''
    try:
        rst = analyze_golden(macd, isprt)
    except AnalyzeError:
        raise AnalyzeError(get_code() + '，不是金叉！')
    # 3根红柱以上，判断最后3根越来越长
    if rst[4] < 3:
        return rst
    else:
        raise AnalyzeError(get_code() + '，金叉后红柱没有持续变长！')

def analyze_golden(macd, isprt=False):
    ''' macd最后一次交叉是金叉才有返回值，否则返回空列表，
            返回包括金叉日期，金叉后红柱数量，红柱高度，快线高度
            save_golden方法计算完macd后调用
    '''
    cnt_hz = 0
    rst = []
    cnt = int(macd.shape[0])
    if cnt < 30:
        raise AnalyzeError(get_code() + '，macd数据少于30周期,不判断金叉！')

    if isprt:
        print(macd)
    # 如果当前macd绿柱不判断直接返回
    if macd.iloc[-1]['macd'] < 0:
        raise AnalyzeError(get_code() + '，绿柱不是金叉！')
    for i in range(1, cnt - 1):
        # macd>0 为红柱，计数并向前找小于0的时间为金叉点
        if macd.iloc[-i]['macd'] > 0:
            cnt_hz += 1  # 红柱计数
            continue
        else:
            # MACD 金叉
            if macd.iloc[-1]['macd'] < macd.iloc[-2]['macd'] < macd.iloc[-3]['macd']:
                raise AnalyzeError(get_code() + '，金叉后开口方向没有向上！')
            rst.append('golden')
            rst.append(get_code().split('.')[1])
            rst.append(macd.iloc[-i + 1]['time'])
            if macd.iloc[-i]['dif'] >= 0.001:
                rst.append('up0')
            else:
                rst.append('down0')
            # 第一个金叉判断完成退出[4]
            rst.append(cnt_hz)
            rst.append(get_code())
            return rst

    raise AnalyzeError(get_code() + '，不是金叉！')


def analyze_top(macd, isptt=False):
    ''' 分析macd 顶背离
    '''
    rst = []
    rst2 = []
    cnt = int(macd.shape[0])
    if cnt < 40:
        raise AnalyzeError(get_code() + '，macd数据少于40周期,不判断顶背离！')

    # 绿柱结束直接退出
    if macd.iloc[-1]['macd'] < 0:
        raise AnalyzeError(get_code() + '，macd最后为绿柱！')

    rst.append(macd.iloc[-1]['time'])
    rst2.append(macd.iloc[-1]['macd'])
    for idx in range(1, cnt - 1):
        if len(rst2) == 1:
            # 从右向左第一次为死叉,macd应从红转绿,记录最后的红线时间
            if macd.iloc[-idx]['macd'] >= 0:
                rst.append(macd.iloc[-1]['time'])
                rst2.append(macd.iloc[-idx]['macd'])
        if len(rst2) == 2:
            # 从右向左第二次为金叉,macd应从绿转红,记录最后的绿线时间
            if macd.iloc[-idx]['macd'] < 0:
                rst.append(macd.iloc[-1]['time'])
                rst2.append(macd.iloc[-idx]['macd'])
        if len(rst2) == 3:
            # 从右向左第三次为死叉,macd应从红转绿,记录最后的红线时间
            if macd.iloc[-idx]['macd'] >= 0:
                rst.append(macd.iloc[-1]['time'])
                rst2.append(macd.iloc[-idx]['macd'])

    if len(rst) == 4:
        if isptt:
            print(rst)
            print(rst2)
        return rst2
    else:
        raise AnalyzeError(get_code() + '，不是顶背离！')


def analyze_bottom(macd, isptt=False):
    ''' 分析macd 底背离 从右向左 先有死叉再有金叉，再判断将要金叉，及其与左边金叉高度
    '''
    rst = ['time']
    rst2 = []
    cnt = int(macd.shape[0])
    if cnt < 40:
        raise AnalyzeError(get_code() + '，MACD少于40周期，不判断底背离！')

    # 红柱结束直接退出
    if macd.iloc[-1]['macd'] > 0:
        raise AnalyzeError(get_code() + '，以红柱结束，已过底背离！')

    rst.clear()
    rst.append(macd.iloc[-1]['time'])
    rst2.append(macd.iloc[-1]['dif'])

    for idx in range(1, cnt - 1):
        if len(rst2) == 1:
            # 从右向左先死叉,macd应从红转绿,记录最后的红线时间
            if macd.iloc[-idx]['macd'] >= 0:
                rst.append(macd.iloc[-idx]['time'])
                rst2.append(macd.iloc[-idx]['dif'])
        if len(rst2) == 2:
            # 从右向左死叉后又金叉,macd应从绿转红,记录最后的绿线时间
            if macd.iloc[-idx]['macd'] < 0:
                rst.append(macd.iloc[-idx]['time'])
                rst2.append(macd.iloc[-idx]['dif'])

    if len(rst2) == 3:
        # rst2[0]：dif将要金叉的高度 ， rst2[2]：第一次金叉的高度,  都要在0轴下
        if -0.05 > rst2[0] > rst2[2]:
            # 符合底背离条件，需要再判断是否即将金叉
            try:
                bing_golden = analyze_bing_golden(macd, isptt)
            except AnalyzeError:
                raise AnalyzeError(get_code() + '，不是底背离，没有将要金叉！')

            # 将要金叉，符合背离，本只股票，将要底背离
            if isptt:
                print('\n 股票代码：', get_code())
                print(rst)
                print(rst2)
            dbl = []
            dbl.append('即将底背离')
            dbl.append(get_code().split('.')[1])
            dbl.append(rst[0])
            dbl.append(rst2[0])
            dbl.append(rst[2])
            dbl.append(rst2[2])
            return dbl

        else:
            raise AnalyzeError(get_code() + '，不是底背离，三次交叉不符合条件！')
    else:
        raise AnalyzeError(get_code() + '，不是底背离，不是三次交叉！')
