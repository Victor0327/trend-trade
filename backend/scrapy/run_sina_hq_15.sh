#!/bin/sh

# 更改到指定目录
cd /usr/bin/trend-trade/backend/scrapy

# 读取配置文件并进行迭代
while IFS=, read -r symbol interval; do

    /home/flamingo/anaconda3/bin/scrapy crawl finance_sina -a symbol=$symbol -a interval=$interval >> /usr/bin/trend-trade/backend/scrapy/output/finance_sina_15_sh.log 2>&1 &

    sleep 10

done < /usr/bin/trend-trade/backend/scrapy/sina_hq_15_config.txt
