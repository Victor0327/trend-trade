#!/bin/sh

# 读取配置文件并进行迭代
while IFS=, read -r symbol interval; do

    /home/flamingo/anaconda3/bin/scrapy crawl finance_sina -a symbol=$symbol -a interval=$interval >> /usr/bin/trend-trade/backend/scrapy/output/finance_sina_sh.log 2>&1 &
    # scrapy crawl finance_sina -a symbol=$symbol -a interval=$interval >> ./output/finance_sina_sh.log 2>&1 &

    # 等待5s
    sleep 5

done < sina_hq_config.txt
