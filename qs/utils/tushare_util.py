import os

import tushare as ts
from sqlalchemy import create_engine, VARCHAR
import pandas as pd
import threading
from sqlalchemy.exc import ProgrammingError
import configparser as cp


class TushareUtil(object):
    _instance_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        config = cp.ConfigParser()
        config.read(os.path.join(os.path.abspath('.'), 'config.ini'))
        token = config['tushare']['token']
        username = config['mysql']['username']
        password = config['mysql']['password']
        host = config['mysql']['host']
        port = config['mysql']['port']
        database = config['mysql']['database']
        ts.set_token(token)
        self.pro = ts.pro_api()
        con_str = 'mysql+pymysql://%s:%s@%s:%s/%s' % (username, password, host, port, database)
        self.conn = create_engine(con_str, encoding='utf8',
                                  max_overflow=100,  # 超过连接池大小外最多创建的连接
                                  pool_size=50,  # 连接池大小
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

    def data_to_pd(self, ts_code, field):
        #sql = "select * from `%s`" % (ts_code)
        #必须设置order by，否则计算会错误
        sql = "select * from `%s` order by %s" % (ts_code, field)
        print(sql)
        data = pd.read_sql_query(sql, self.conn)
        return data

    def save(self, data, table_name, action="append",dtype=None):
        '''
        :param data: pandas格式的数据
        :param table_name: 数据表名
        :param action: 取值范围replace,add,fail
        :return:None
        '''
        pd.io.sql.to_sql(data, table_name, self.conn, if_exists=action, dtype=dtype)

    def get_save_stock_list(self, table_name):
        data = self.pro.query('stock_basic', exchange='', list_status='L',
                              fields='ts_code,symbol,name,area,industry,list_date')
        data.set_index('symbol', inplace=True)
        print(data)
        col_name = ['ts_code']
        new_data = pd.DataFrame(data, columns=col_name)
        print(new_data)
        sql = "select symbol,ts_code from %s; " % (table_name)
        try:
            old_data = pd.read_sql_query(sql, self.conn)
            old_data.set_index('symbol', inplace=True)
            print(old_data)
            # 用于判断是否数据有更新，没有就做不做数据库的更新
            if not old_data.equals(new_data):
                self.save(data, table_name, action="replace", dtype={'symbol': VARCHAR(data.index.get_level_values('symbol').str.len().max())})
            else:
                print('no new stock, ingore get_save_stock_list')
        except ProgrammingError:
            print("No stock_list table exists,create it")
            self.save(data, table_name, action="replace", dtype={'symbol': VARCHAR(data.index.get_level_values('symbol').str.len().max())})
        return data

    def get_stock_info(self, ts_code, start_date, end_date, limit=None):
        """
        ts_code:代码，通过get_stock_list获取的ts_code
        start_date:开始日期，格式YYYYMMDD，例子20201101
        end_date:截止日期，格式YYYYMMDD，例子20201101
        """
        data = ts.pro_bar(ts_code=ts_code, api=None, start_date=start_date, end_date=end_date, freq='D', asset='E',
                          exchange='', adj='qfq', factors=['vr', 'tor'], adjfactor=False, offset=None, limit=limit,
                          contract_type='', retry_count=3)
        return data

    def get_save_stock_info(self, ts_code, start_date, end_date, action, limit=1):
        """
        ts_code:代码，通过get_stock_list获取的ts_code
        start_date:开始日期，格式YYYYMMDD，例子20201101
        end_date:截止日期，格式YYYYMMDD，例子20201101
        """
        data = ts.pro_bar(ts_code=ts_code, api=None, start_date=start_date, end_date=end_date, freq='D', asset='E',
                          exchange='', adj='qfq', factors=['vr', 'tor'], adjfactor=False, offset=None, limit=limit,
                          contract_type='', retry_count=3)
        data.set_index('trade_date', inplace=True)
        self.save(data, ts_code, action, dtype={'trade_date': VARCHAR(data.index.get_level_values('trade_date').str.len().max())})
        return data

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

    def close(self):
        self.conn.dispose()

    def get_trade_calendar(self, exchange, start_date, end_date):
        '''
        获取各大交易所交易日历数据,默认提取的是上交所
        https://tushare.pro/document/2?doc_id=26
        :param exchange:交易所 SSE上交所,SZSE深交所,CFFEX 中金所,SHFE 上期所,CZCE 郑商所,DCE 大商所,INE 上能源,IB 银行间,XHKG 港交所
        :param start_date:开始日期
        :param end_date:结束日期
        :param is_open 是否交易 '0'休市 '1'交易
        :return:
        '''
        data = self.pro.trade_cal(exchange='', start_date=start_date, end_date=end_date)
        return data

    def campany_basic_info(self):
        data = self.pro.stock_company(exchange='SZSE',
                                      fields='ts_code,chairman,manager,secretary,reg_capital,setup_date,province')
        return data

    def get_all_list_date(self, data):
        '''
        :param data:原始的dataframe
        :return:包含'ts_code', 'list_date'两列数据的dataframe
        '''
        col_name = ['ts_code', 'list_date']
        list_data_df = pd.DataFrame(data, columns=col_name)
        return list_data_df
