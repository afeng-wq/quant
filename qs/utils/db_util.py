from sqlalchemy import create_engine
import pandas as pd
import threading

class DBUtil(object):
    _instance_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        self.conn = create_engine('mysql+pymysql://root:wangqiang@localhost:3306/stock',
        encoding='utf8',
        max_overflow=10,  # 超过连接池大小外最多创建的连接
        pool_size=5,  # 连接池大小
        pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
        pool_recycle=-1)  # 多久之后对线程池中的线程进行一次连接的回收（重置）     

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(DBUtil, "_instance"):
            with DBUtil._instance_lock:
                if not hasattr(DBUtil, "_instance"):
                    DBUtil._instance = DBUtil(*args, **kwargs)
        return DBUtil._instance

    def add2db(self,data,table_name):
        pd.io.sql.to_sql(data, table_name, self.conn, if_exists='append')

    def init(self,data,table_name):
        pd.io.sql.to_sql(data, table_name, self.conn, if_exists='replace')

    def close(self):
        self.conn.dispose()

    # def get_latest_stock_price(self,ts_code):


