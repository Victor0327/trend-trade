import psycopg2
from psycopg2 import pool
import pandas as pd
import os
from service.super_db_engine import SuperDBEngine

# 发布前注释掉
# os.environ['DB_ENV'] = 'dev'

config = {
  'test': {
    'host': 'flamingo-test.csgp3g81cy2o.us-west-1.rds.amazonaws.com',
    'password': '2cHC1O3QuwGPwLiK0JSqrA==',
    'database': 'kong'
  },
  'tencent': {
    'host': '43.138.180.64',
    'password': '2cHC1O3QuwGPwLiK0JSqrA==',
    'database': 'trade'
  }
}

class DBEngine(SuperDBEngine):

    def __init__(self, env = 'tencent'):
        db_config = config[env]
        print(db_config)
        # 创建连接池
        self.conn_pool = psycopg2.pool.SimpleConnectionPool(1, 10,
                                               user="postgres",
                                               password=db_config['password'],
                                               host=db_config['host'],
                                               port="5432",
                                               database=db_config['database'])


    def run_sql_to_df(self, sql):
        conn = self.conn_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()

        col_names = []
        result = {}
        if cursor.description is None:
           return pd.DataFrame()
        column_count = len(cursor.description)
        for i in range(column_count):
          desc = cursor.description[i]
          col_names.append(desc[0])
        data = cursor.fetchall()
        cursor.close()
        self.conn_pool.putconn(conn)


        result['head'] = col_names
        result['data'] = data
        df = pd.DataFrame(list(result.get('data')),columns=result.get('head'))
        return df

    def run_sql_to_dict_list(self, sql):
        conn = self.conn_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        data = cursor.fetchall()

        result = []
        if cursor.description is None:
           return []
        column_count = len(cursor.description)
        for row in data:
          new_row = {}
          for i in range(column_count):
            desc = cursor.description[i]
            new_row[desc[0]] = row[i]
          result.append(new_row)

        cursor.close()
        self.conn_pool.putconn(conn)


        return result

    def run_sql_to_tuple_list(self, sql):
        conn = self.conn_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        data = cursor.fetchall()
        cursor.close()
        self.conn_pool.putconn(conn)

        return data

    def run_sql_to_commit(self, sql):
        conn = self.conn_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        self.conn_pool.putconn(conn)
        return True

post_db = DBEngine(env='tencent')
