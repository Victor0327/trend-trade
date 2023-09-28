from crontab import CronTab

# # 创建linux系统当前用户的crontab，当然也可以创建其他用户的，但得有足够权限,如:user='root'
cron_manager  = CronTab(user='root')

def deleteCron(comment):
  for job in cron_manager:
    if job.comment == comment:
      cron_manager.remove(job)
      cron_manager.write()

# deleteCron('job')
deleteCron('morning_job')
deleteCron('afternoon_job')
deleteCron('evening_job')
deleteCron('morning_1_job')
deleteCron('afternoon_1_job')
deleteCron('evening_1_job')
deleteCron('morning_15_job')
deleteCron('afternoon_15_job')
deleteCron('evening_15_job')



morning_15_job = cron_manager.new(command='/usr/bin/trend-trade/backend/scrapy/run_sina_hq_15.sh >> /usr/bin/trend-trade/backend/scrapy/output/finance_sina_15_job.log 2>&1 &', comment='morning_15_job')
afternoon_15_job = cron_manager.new(command='/usr/bin/trend-trade/backend/scrapy/run_sina_hq_15.sh >> /usr/bin/trend-trade/backend/scrapy/output/finance_sina_15_job.log 2>&1 &', comment='afternoon_15_job')
evening_15_job = cron_manager.new(command='/usr/bin/trend-trade/backend/scrapy/run_sina_hq_15.sh >> /usr/bin/trend-trade/backend/scrapy/output/finance_sina_15_job.log 2>&1 &', comment='evening_15_job')

morning_1_job = cron_manager.new(command='/usr/bin/trend-trade/backend/scrapy/run_sina_hq_1.sh >> /usr/bin/trend-trade/backend/scrapy/output/finance_sina_1_job.log 2>&1 &', comment='morning_1_job')
afternoon_1_job = cron_manager.new(command='/usr/bin/trend-trade/backend/scrapy/run_sina_hq_1.sh >> /usr/bin/trend-trade/backend/scrapy/output/finance_sina_1_job.log 2>&1 &', comment='afternoon_1_job')
evening_1_job = cron_manager.new(command='/usr/bin/trend-trade/backend/scrapy/run_sina_hq_1.sh >> /usr/bin/trend-trade/backend/scrapy/output/finance_sina_1_job.log 2>&1 &', comment='evening_1_job')


morning_15_job.setall('*/15 1-4 * * *')
afternoon_15_job.setall('*/15 5-7 * * *')
evening_15_job.setall('*/15 13-16 * * *')

morning_1_job.setall('*/20 1-4 * * *')
afternoon_1_job.setall('*/20 5-7 * * *')
evening_1_job.setall('*/20 13-16 * * *')



cron_manager.write()


