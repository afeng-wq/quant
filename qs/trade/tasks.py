from celery import task
import time
from celery.task import periodic_task
from qs import celery_app
from trade.models import StockList
import threading
from utils.tushare_util import TushareUtil


@celery_app.task
def sendmail(email):
    print('start send email to %s' % email)
    time.sleep(5)  # 休息5秒
    print('success')
    return True


@periodic_task(run_every=10)
def get_stock_daily_info():
    util = TushareUtil.instance()

    stock_list = StockList.objects.all()
    print("len of  stock_list %s", stock_list.count())

    for e in stock_list:
        t1 = threading.Thread(target=music, args=(u'爱情买卖',))
        print(e)