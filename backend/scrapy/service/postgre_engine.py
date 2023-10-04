import psycopg2
import pandas as pd
import os

# 发布前注释掉
# os.environ['ENV'] = 'dev'

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

class DBEngine:

    def __init__(self, env = 'tencent'):
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

    def run_sql(self, sql):
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

    def run_insert_sql(self, sql):
        self.cursor.execute(sql)
        # print(sql)
        self.conn.commit()

    def get_conn(self):
      return self.conn

post_db = DBEngine(env='tencent')