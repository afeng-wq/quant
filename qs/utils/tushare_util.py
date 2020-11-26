import tushare as ts
import threading

class TushareUtil(object):
    _instance_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        ts.set_token('072d2f70f82b1dbe88c0c374a95b8ada98da017b5ff31545ff4b437e')
        self.pro = ts.pro_api()

    @classmethod
    def instance(cls, *args, **kwargs):
        """
        单例方法
        """
        if not hasattr(TushareUtil, "_instance"):
            with TushareUtil._instance_lock:
                if not hasattr(TushareUtil, "_instance"):
                    TushareUtil._instance = TushareUtil(*args, **kwargs)
        return TushareUtil._instance

    def get_stock_list(self):
        data = self.pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        return data

    def get_stock_info(self,ts_code,start_date,end_date):
        """
        ts_code:代码，通过get_stock_list获取的ts_code
        start_date:开始日期，格式YYYYMMDD，例子20201101
        end_date:截止日期，格式YYYYMMDD，例子20201101
        """
        data = ts.pro_bar(ts_code=ts_code, api=None, start_date=start_date, end_date=end_date, freq='D', asset='E', exchange='', adj='qfq', factors=['vr', 'tor'], adjfactor=False, offset=None, limit=None, contract_type='', retry_count=3)
        return data

    def income(self,ts_code,start_date,end_date):
        """
        参考：https://tushare.pro/document/2?doc_id=33
        ts_code:代码，通过get_stock_list获取的ts_code
        start_date:开始日期，格式YYYYMMDD，例子20201101
        end_date:截止日期，格式YYYYMMDD，例子20201101
        """
        income_data = self.pro.income(ts_code=ts_code, start_date=start_date, end_date=end_date, fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,basic_eps,diluted_eps')
        return income_data

    def income_vip(self,period):
        income_vip_data = self.pro.income_vip(period=period,fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,basic_eps,diluted_eps')
        return income_vip_data






