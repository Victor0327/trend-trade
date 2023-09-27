from crontab import CronTab

# # 创建linux系统当前用户的crontab，当然也可以创建其他用户的，但得有足够权限,如:user='root'
cron_manager  = CronTab(user='root')

def deleteCron(comment):
  for job in cron_manager:
    if job.comment == comment:
      cron_manager.remove(job)
      cron_manager.write()

deleteCron('job')
deleteCron('morning_job')
deleteCron('afternoon_job')
deleteCron('evening_job')


# # 创建任务 指明运行python脚本的命令(crontab的默认执行路径为：当前用户的根路径, 因此需要指定绝对路径)
morning_job = cron_manager.new(command='/usr/bin/trend-trade/backend/scrapy/run_sina_hq.sh >> /usr/bin/trend-trade/backend/scrapy/output/finance_sina_job.log 2>&1 &', comment='morning_job')
afternoon_job = cron_manager.new(command='/usr/bin/trend-trade/backend/scrapy/run_sina_hq.sh >> /usr/bin/trend-trade/backend/scrapy/output/finance_sina_job.log 2>&1 &', comment='afternoon_job')
evening_job = cron_manager.new(command='/usr/bin/trend-trade/backend/scrapy/run_sina_hq.sh >> /usr/bin/trend-trade/backend/scrapy/output/finance_sina_job.log 2>&1 &', comment='evening_job')
# job = cron_manager.new(command='/Users/edz/Codebase/trend-trade/backend/scrapy/run_sina_hq.sh >> /Users/edz/Codebase/trend-trade/backend/scrapy/output/finance_sina_job.log 2>&1 &', comment='job')

# # 设置任务执行周期，每两分钟执行一次(更多方式请稍后参见参考链接)

morning_job.setall('*/15 17-20 * * *')

afternoon_job.setall('*/15 21-23 * * *')

evening_job.setall('*/15 5-8 * * *')



cron_manager.write()


