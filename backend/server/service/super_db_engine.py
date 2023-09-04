from pandas import DataFrame

class SuperDBEngine:

   def __init__(self):
      self.cursor = None
      self.conn = None

   def run_sql(self) -> DataFrame:
      return DataFrame()