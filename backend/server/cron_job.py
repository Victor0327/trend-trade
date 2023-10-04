from apscheduler.schedulers.background import BackgroundScheduler
from cron.crypto_btcusdt_spot_1d import job as crypto_btcusdt_spot_1d
from cron.crypto_btcusdt_perpetual_1d import job as crypto_btcusdt_perpetual_1d
from cron.aip import aip_cron_jobs
import logging

scheduler = BackgroundScheduler()

scheduler.add_job(
    crypto_btcusdt_spot_1d.run,
    trigger=crypto_btcusdt_spot_1d.trigger,
    id=crypto_btcusdt_spot_1d.job_id,
    **crypto_btcusdt_spot_1d.trigger_args)

logging.info(f"add_job {crypto_btcusdt_spot_1d.job_id}")

scheduler.add_job(
    crypto_btcusdt_perpetual_1d.run,
    trigger=crypto_btcusdt_perpetual_1d.trigger,
    id=crypto_btcusdt_perpetual_1d.job_id,
    **crypto_btcusdt_perpetual_1d.trigger_args)

logging.info(f"add_job {crypto_btcusdt_perpetual_1d.job_id}")

for aip_cron_job in aip_cron_jobs:
  scheduler.add_job(
    aip_cron_job.run,
    trigger=aip_cron_job.trigger,
    id=aip_cron_job.job_id,
    **aip_cron_job.trigger_args)
  logging.info(f"add_job {aip_cron_job.job_id}")



scheduler.start()