import standalone

standalone.run('qs.settings')
from datetime import datetime
import time
from trade.models import StockList
from utils.tushare_util import TushareUtil
import threading
import pandas as pd


def init_stock_info():
    '''
    1分钟只能获取200gp的信息
    起了200个线程，这些线程未必能在1分钟内完成，所以需要不能起太多线程
    '''
    print('================Start================')
    stocks = StockList.objects.all()
    current_date = datetime.now().strftime('%Y%m%d')
    print(current_date)
    i = 0
    for e in stocks:
        t = threading.Thread(target=TushareUtil.instance().get_save_stock_info,
                             args=(e.ts_code, e.list_date, current_date))
        t.setDaemon(False)
        t.start()
        i = i + 1
        print('#%d save %s' % (i, e.ts_code))
        if i == 100:
            time.sleep(120)
            i = 0
    print('================End================')


if __name__ == "__main__":
    '''
    初始化获取所有当前的信息
    '''
    # init_stock_info()

    util = TushareUtil.instance()
    # util.get_save_stock_info('688599.SH', '20201101', '20201201', 'replace', None)
    # util.get_save_stock_info('688599.SH', '20201102', '20201102', 'append', 1)
    # util.get_save_stock_info('688599.SH', '202011023', '20201123', 'append', 1)

    data = util.data_to_pd('688599.SH','trade_date')
    print(data)
    # init_stock_info()
    # data = util.data_2_pd('688526.SH')

    # data = util.ma(data,15)
    # print(data)
    '''
    1.获取所有的gp列表，存到数据库中
    2.每天定时获取一次gp列表，跟之前的数据库中的数据进行对比
        如果有差异，那么重新存库，即覆盖原来的数据。
    3.每天定时根据所有的gp列表，逐条获取当日的信息
        获取后，计算ma相关数据
    4.发现在4点左右，虽然可以获取当天的数据，但是有数据缺失，所以1.先要查一下数据是否有空值，如果有，那么该任务需要后面再一次处理。
    '''
