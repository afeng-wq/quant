import pandas as pd


def ma(data, avg):
    '''
    获取平均值
    :param data:pandas数据
    :param avg:赋值方式，列表形式，必须是数字格式的list，如[5,10,20，72]
    :return:
    '''
    if ma is not None and len(ma) > 0:
        for a in ma:
            if isinstance(a, int):
                data['ma%s' % avg] = pd.Series.rolling(data['close'], avg).mean().map(lambda x: '%.4f' % x).shift(-(avg - 1))
                data['ma%s' % avg] = data['ma%s' % avg].astype(float)
                data['ma_v_%s' % avg] = pd.Series.rolling(data['vol'], avg).map(lambda x: '%.4f' % x).shift(-(avg - 1))
                data['ma_v_%s' % avg] = data['ma_v_%s' % avg].astype(float)
    return data
