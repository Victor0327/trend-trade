from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

def my_job():
    print("Reminder at", datetime.now())

scheduler = BackgroundScheduler()

# 添加一个任务并为其分配一个ID
job_id = "my_job_id"
scheduler.add_job(my_job, 'cron', id=job_id, day=3, hour=16, minute=13)

scheduler.start()

time.sleep(10)  # 为了演示，让程序运行10秒

# 暂停任务
scheduler.pause_job(job_id)
print(f"Job {job_id} paused!")

time.sleep(10)  # 让程序再运行10秒

# 恢复任务
scheduler.resume_job(job_id)
print(f"Job {job_id} resumed!")

time.sleep(10)  # 再次让程序运行10秒

# 删除任务
scheduler.remove_job(job_id)
print(f"Job {job_id} removed!")

# 为了展示效果，我们再使用一个循环来阻止程序立即结束
# 你可以替换这部分为你主程序的代码
try:
    while True:
        time.sleep(10)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
