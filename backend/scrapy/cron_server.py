from crontab import CronTab

# # 创建linux系统当前用户的crontab，当然也可以创建其他用户的，但得有足够权限,如:user='root'
cron_manager  = CronTab(user='root')

# # 创建任务 指明运行python脚本的命令(crontab的默认执行路径为：当前用户的根路径, 因此需要指定绝对路径)
job = cron_manager.new(command='/usr/bin/trend-trade/backend/scrapy/run_sina_hq.sh >> /usr/bin/trend-trade/backend/scrapy/output/finance_sina_job.log 2>&1 &', comment='job')
# job = cron_manager.new(command='/Users/edz/Codebase/trend-trade/backend/scrapy/run_sina_hq.sh >> /Users/edz/Codebase/trend-trade/backend/scrapy/output/finance_sina_job.log 2>&1 &', comment='job')

# # 设置任务执行周期，每两分钟执行一次(更多方式请稍后参见参考链接)
# 下午16点执行
# job.setall('0 8 * * *')
job.setall('53 11 * * *')
# job.setall('25 19 * * *')


def deleteCron(comment):
  for job in cron_manager:
    if job.comment == comment:
      cron_manager.remove(job)
      cron_manager.write()

# deleteCron('job')

cron_manager.write()


