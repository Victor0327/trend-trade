#!/bin/sh

# 更改到指定目录
# cd /usr/bin/trend-trade/backend/scrapy

# 读取配置文件并进行迭代
while IFS=, read -r symbol interval; do

    scrapy crawl finance_sina -a symbol=$symbol -a interval=$interval >> ./output/finance_sina_15_sh.log 2>&1 &

    sleep 5

done < sina_hq_15_config.txt
