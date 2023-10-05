from apscheduler.schedulers.background import BackgroundScheduler
from cron.crypto_btcusdt_spot_1d import job as crypto_btcusdt_spot_1d
from cron.crypto_btcusdt_perpetual_1d import job as crypto_btcusdt_perpetual_1d
from cron.aip import aip_cron_jobs
from cron.cn_goods_sina_1 import job as cn_goods_sina_1
from cron.cn_goods_sina_15 import job as cn_goods_sina_15
from cron.us_goods_sina_15 import job as us_goods_sina_15
from cron.currency_sina_15 import job as currency_sina_15
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

scheduler.add_job(
    cn_goods_sina_1.run,
    trigger=cn_goods_sina_1.trigger,
    id=cn_goods_sina_1.job_id,
    **cn_goods_sina_1.trigger_args)

logging.info(f"add_job {cn_goods_sina_1.job_id}")

scheduler.add_job(
    cn_goods_sina_15.run,
    trigger=cn_goods_sina_15.trigger,
    id=cn_goods_sina_15.job_id,
    **cn_goods_sina_15.trigger_args)

logging.info(f"add_job {cn_goods_sina_15.job_id}")

scheduler.add_job(
    us_goods_sina_15.run,
    trigger=us_goods_sina_15.trigger,
    id=us_goods_sina_15.job_id,
    **us_goods_sina_15.trigger_args)

logging.info(f"add_job {us_goods_sina_15.job_id}")

scheduler.add_job(
    currency_sina_15.run,
    trigger=currency_sina_15.trigger,
    id=currency_sina_15.job_id,
    **currency_sina_15.trigger_args)

logging.info(f"add_job {currency_sina_15.job_id}")


# aip 定投
for aip_cron_job in aip_cron_jobs:
  scheduler.add_job(
    aip_cron_job.run,
    trigger=aip_cron_job.trigger,
    id=aip_cron_job.job_id,
    **aip_cron_job.trigger_args)
  logging.info(f"add_job {aip_cron_job.job_id}")



scheduler.start()