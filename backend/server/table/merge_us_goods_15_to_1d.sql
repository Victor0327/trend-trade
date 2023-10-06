-- TODO: 国内行情合并的sql不大好写，时间计算太麻烦了，先不用了。
-- merge cn_goods_a0_15 to cn_goods_a0_1d
drop table if exists tmp_cn_goods_a0_1d;

create temp table tmp_cn_goods_a0_1d(like cn_goods_a0_1d);

WITH AdjustedDates AS (
    SELECT
        CASE
            WHEN EXTRACT(HOUR FROM date) >= 21 THEN date + INTERVAL '1 day'
            ELSE date
        END AS adjusted_date,
        open, high, low, close, volume, position
    FROM
        cn_goods_a0_15
)

-- insert into tmp_cn_goods_a0_1d (date, open, high, low, close, volume, position)
insert into cn_goods_a0_1d (date, open, high, low, close, volume, position)

SELECT
    DATE(adjusted_date) as date,
    FIRST_VALUE(open) OVER(PARTITION BY DATE(adjusted_date) ORDER BY adjusted_date ASC) as open,
    MAX(high) as high,
    MIN(low) as low,
    LAST_VALUE(close) OVER(PARTITION BY DATE(adjusted_date) ORDER BY adjusted_date DESC) as close,
    SUM(volume) as volume,
    SUM(position) as position
FROM
    AdjustedDates
WHERE
    EXTRACT(HOUR FROM adjusted_date) >= 21 OR EXTRACT(HOUR FROM adjusted_date) <= 15
    -- 增量数据
    and us_day >= stattime_to_us_day(current_timestamp - '2 hours'::interval)
    -- 历史数据
    --  and us_day >= '2023-04-06'
GROUP BY
    DATE(adjusted_date);

-- 开启事务
begin transaction;

-- 2. 使用与暂存表的内部联接从要更新的目标表中删除行。
delete from cn_goods_a0_1d
using tmp_cn_goods_a0_1d
where 1 = 1
    and tmp_cn_goods_a0_1d.date = cn_goods_a0_1d.date;

-- 3. 插入暂存表中的所有行
insert into cn_goods_a0_1d
select * from tmp_cn_goods_a0_1d;

-- 结束事务
end transaction;

-- 删除暂存表
drop table if exists tmp_cn_goods_a0_1d;