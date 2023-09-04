import psycopg2
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
  }
}

class DBEngine(SuperDBEngine):

    def __init__(self, env = 'test'):
        db_config = config[env]
        print(db_config)
        conn = psycopg2.connect(
          database=db_config['database'],
          user="postgres",
          password=db_config['password'],
          host=db_config['host'],
          port="5432")

        cursor = conn.cursor()
        self.cursor = cursor
        self.conn = conn

    def run_sql_to_df(self, sql):
        self.cursor.execute(sql)
        self.conn.commit()
        col_names = []
        result = {}
        if self.cursor.description is None:
           return pd.DataFrame()
        column_count = len(self.cursor.description)
        for i in range(column_count):
          desc = self.cursor.description[i]
          col_names.append(desc[0])
        data = self.cursor.fetchall()
        result['head'] = col_names
        result['data'] = data
        df = pd.DataFrame(list(result.get('data')),columns=result.get('head'))
        return df

    def run_sql_to_list(self, sql):
        self.cursor.execute(sql)
        self.conn.commit()
        data = self.cursor.fetchall()

        return data

    def get_conn(self):
      return self.conn
