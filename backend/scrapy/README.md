# flamingo-scrapy

新增一个站点的流程
1. 插入一条站点数据到t_crawl_platform
   ```
      INSERT INTO t_crawl_platforms (
        name,
        update_frequency,
        update_page_num,
        created_at,
        updated_at
        )
        values (
        'Gypsypearltx',
        0,
        0,
        '2023-06-05 11:54:24',
        '2023-06-05 11:54:24'
        );
   ```
2. cron_server 文件添加站点爬取的job
3. spiders 文件添加一个新的站点命名文件
4. postgre_engine 改成本地测试模式
5. spiders 文件调整参数，本地试运行，测试完毕看下爬取增加的数量和站点显示的商品数是否一致
6. 改成生产模式，发布到远程服务器然后执行，可执行 python cron_server.py 按计划运行job


2023年09月11日
Heels n spurs
Wild Oak Boutique
Arrow22
The Vintage Emmie
Mania de Vestir
Lane 201
<!--
-->
