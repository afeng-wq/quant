from qs.trade.models import StockList
from qs.utils.db_util import DBUtil
from qs.utils.tushare_util import TushareUtil

if __name__ == "__main__":
    util = TushareUtil.instance()
    data = util.get_stock_list()
    print(data)
    db_util = DBUtil.instance()
    db_util.init(data,"stock_list")

    stock = StockList.objects.get(index=1)
    print(StockList)

    data = util.get_stock_info(ts_code='000001.SZ',start_date='20201124',end_date='20201124')
    db_util.init(data,"000001.SZ")
    print ('aaa')