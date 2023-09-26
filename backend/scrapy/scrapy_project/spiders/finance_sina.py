import scrapy
import uuid
from service.postgre_engine import DBEngine
from table.t_crawl_insert import get_insert_sql, create_table_and_index_sql
import datetime
import json
import re
from scrapy_project.config import STYLE_ID_DICT, CATEGORY_ID_DICT, PLATFORM_ID_DICT
# SEARCH.JSON

class Spider(scrapy.Spider):
    name = 'finance_sina'
    allowed_domains = [f'{name}.com']
    count = 0

    custom_settings = {
        'FEED_URI': f'output/{name}.json',
        # 'dont_filter': True
    }

    def __init__(self, symbol=None, interval=None, *args, **kwargs):
        super(Spider, self).__init__(*args, **kwargs)
        self.symbol = symbol
        self.interval = interval
        self.start_urls = [
            f"https://stock2.finance.sina.com.cn/futures/api/jsonp.php/var%20_{symbol}_{interval}=/InnerFuturesNewService.getFewMinLine?symbol={symbol}&type={interval}",
        ]


    def parse(self, response):
        # 爬取商品卡片链接
        print('#################################')
        data_str = response.body.decode('utf-8')
        match = re.search(rf'_{self.symbol}_{self.interval}=\((.*?)\);', data_str, re.DOTALL)

        if match:
            json_str = match.group(1)
            data_list = json.loads(json_str)
            params = {
                'symbol': self.symbol,
                'interval': self.interval
            }
            # create_table_sql = create_table_and_index_sql(params)
            db = DBEngine()
            # db.run_insert_sql(create_table_sql)
            insert_data_sql = get_insert_sql(params, data_list)
            db.run_insert_sql(insert_data_sql)
        else:
            print("No match found.")