import tushare as ts
from sqlalchemy import create_engine
import pandas as pd
import threading

from sqlalchemy.exc import ProgrammingError

from trade.models import StockList


class TushareUtil(object):
    _instance_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        ts.set_token('072d2f70f82b1dbe88c0c374a95b8ada98da017b5ff31545ff4b437e')
        self.pro = ts.pro_api()
        self.conn = create_engine('mysql+pymysql://root:wangqiang@localhost:3306/stock',
                                  encoding='utf8',
                                  max_overflow=10,  # 超过连接池大小外最多创建的连接
                                  pool_size=5,  # 连接池大小
                                  pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
                                  pool_recycle=-1)  # 多久之后对线程池中的线程进行一次连接的回收（重置）

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
        data = self.pro.query('stock_basic', exchange='', list_status='L',
                              fields='ts_code,symbol,name,area,industry,list_date')
        col_name = ['ts_code']
        new_data = pd.DataFrame(data, columns=col_name)
        sql = ''' select ts_code from stock_list; '''
        try:
            old_data = pd.read_sql_query(sql, self.conn)
            if not old_data.equals(new_data):
                pd.io.sql.to_sql(data, 'stock_list', self.conn, if_exists="replace")
            else:
                print('no new stock,ingore get_stock_list')
        except ProgrammingError:
            print("No stock_list table exists,create it")
            pd.io.sql.to_sql(data, 'stock_list', self.conn, if_exists="replace")

    def get_stock_info(self, ts_code, start_date, end_date, limit=None):
        """
        ts_code:代码，通过get_stock_list获取的ts_code
        start_date:开始日期，格式YYYYMMDD，例子20201101
        end_date:截止日期，格式YYYYMMDD，例子20201101
        """
        data = ts.pro_bar(ts_code=ts_code, api=None, start_date=start_date, end_date=end_date, freq='D', asset='E',
                          exchange='', adj='qfq', factors=['vr', 'tor'], adjfactor=False, ma=[5,10,20,72,120], offset=None, limit=limit,
                          contract_type='', retry_count=3)

        pd.io.sql.to_sql(data, ts_code, self.conn, if_exists="replace")

    def income(self, ts_code, start_date, end_date):
        """
        参考：https://tushare.pro/document/2?doc_id=33
        ts_code:代码，通过get_stock_list获取的ts_code
        start_date:开始日期，格式YYYYMMDD，例子20201101
        end_date:截止日期，格式YYYYMMDD，例子20201101
        """
        income_data = self.pro.income(ts_code=ts_code, start_date=start_date, end_date=end_date,
                                      fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,basic_eps,diluted_eps')
        return income_data

    def income_vip(self, period):
        income_vip_data = self.pro.income_vip(period=period,
                                              fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,basic_eps,diluted_eps')
        return income_vip_data

    def save(self, data, table_name, action="append"):
        '''
        :param data: pandas格式的数据
        :param table_name: 数据表名
        :param action: 取值范围replace,add,fail
        :return:None
        '''
        pd.io.sql.to_sql(data, table_name, self.conn, if_exists=action)

    def close(self):
        self.conn.dispose()

    def save_stock_daily(self, ts_code, date):
        data = self.get_stock_daily(ts_code, date)
        self.save(data, ts_code, 'append')

    def save_stock_info(self, ts_code, start_date, end_date):
        data = self.get_stock_info(ts_code, start_date, end_date)
        self.save(data, ts_code, 'replace')

    def trade_calendar(self,exchange,start_date, end_date):
        '''
        获取各大交易所交易日历数据,默认提取的是上交所
        https://tushare.pro/document/2?doc_id=26
        :param exchange:交易所 SSE上交所,SZSE深交所,CFFEX 中金所,SHFE 上期所,CZCE 郑商所,DCE 大商所,INE 上能源,IB 银行间,XHKG 港交所
        :param start_date:开始日期
        :param end_date:结束日期
        :param is_open 是否交易 '0'休市 '1'交易
        :return:
        '''
        self.pro.trade_cal(exchange='', start_date=start_date, end_date=end_date)

    def campany_basic_info(self):
       self.pro.stock_company(exchange='SZSE', fields='ts_code,chairman,manager,secretary,reg_capital,setup_date,province')

    def get_list_date(self, data):
        '''
        :param data:原始的dataframe
        :return:包含'ts_code', 'list_date'两列数据的dataframe
        '''
        col_name = ['ts_code', 'list_date']
        list_data_df = pd.DataFrame(data, columns=col_name)
        return list_data_df
