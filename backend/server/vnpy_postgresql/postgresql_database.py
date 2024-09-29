from datetime import datetime
from typing import List

from peewee import (
    AutoField,
    CharField,
    DateTimeField,
    FloatField,
    IntegerField,
    Model,
    PostgresqlDatabase as PeeweePostgresqlDatabase,
    ModelSelect,
    ModelDelete,
    fn,
    chunked,
)

from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.object import BarData, TickData
from vnpy.trader.database import (
    BaseDatabase,
    BarOverview,
    TickOverview,
    DB_TZ,
    convert_tz
)
from vnpy.trader.setting import SETTINGS


db: PeeweePostgresqlDatabase = PeeweePostgresqlDatabase(
    database=SETTINGS["database.database"],
    user=SETTINGS["database.user"],
    password=SETTINGS["database.password"],
    host=SETTINGS["database.host"],
    port=SETTINGS["database.port"],
    autorollback=True
)

# """K线数据表映射对象"""
db_bar_fields = {
    'id': AutoField(),

    'symbol': CharField(),
    'exchange': CharField(),
    'datetime': DateTimeField(),
    'interval': CharField(),

    'volume': FloatField(),
    'turnover': FloatField(),
    'open_interest': FloatField(),
    'open_price': FloatField(),
    'high_price': FloatField(),
    'low_price': FloatField(),
    'close_price': FloatField(),
}

db_bar_meta_fields = {
    'database': db,
    'indexes': ((("symbol", "exchange", "interval", "datetime"), True),)
}

# """TICK数据表映射对象"""
db_tick_fields = {
    'id': AutoField(),

    'symbol': CharField(),
    'exchange': CharField(),
    'datetime': DateTimeField(),

    'name': CharField(),
    'volume': FloatField(),
    'turnover': FloatField(),
    'open_interest': FloatField(),
    'last_price': FloatField(),
    'last_volume': FloatField(),
    'limit_up': FloatField(),
    'limit_down': FloatField(),

    'open_price': FloatField(),
    'high_price': FloatField(),
    'low_price': FloatField(),
    'pre_close': FloatField(),

    'bid_price_1': FloatField(),
    'bid_price_2': FloatField(null=True),
    'bid_price_3': FloatField(null=True),
    'bid_price_4': FloatField(null=True),
    'bid_price_5': FloatField(null=True),

    'ask_price_1': FloatField(),
    'ask_price_2': FloatField(null=True),
    'ask_price_3': FloatField(null=True),
    'ask_price_4': FloatField(null=True),
    'ask_price_5': FloatField(null=True),

    'bid_volume_1': FloatField(),
    'bid_volume_2': FloatField(null=True),
    'bid_volume_3': FloatField(null=True),
    'bid_volume_4': FloatField(null=True),
    'bid_volume_5': FloatField(null=True),

    'ask_volume_1': FloatField(),
    'ask_volume_2': FloatField(null=True),
    'ask_volume_3': FloatField(null=True),
    'ask_volume_4': FloatField(null=True),
    'ask_volume_5': FloatField(null=True),

    'localtime': DateTimeField(null=True),
}

db_tick_meta_fields = {
    'database': db,
    'indexes': ((("symbol", "exchange", "datetime"), True),),
}

# """K线汇总数据表映射对象"""
db_bar_overview_fields = {
    'id': AutoField(),

    'symbol': CharField(),
    'exchange': CharField(),
    'interval': CharField(),
    'count': IntegerField(),
    'start': DateTimeField(),
    'end': DateTimeField(),
}

db_bar_overview_meta_fields = {
    'database': db,
    'indexes': ((("symbol", "exchange", "interval"), True),),
}

# """tick汇总数据表映射对象"""
db_tick_overview_fields = {
    'id': AutoField(),

    'symbol': CharField(),
    'exchange': CharField(),
    'count': IntegerField(),
    'start': DateTimeField(),
    'end': DateTimeField(),
}

db_tick_overview_meta_fields = {
    'database': db,
    'indexes': ((("symbol", "exchange"), True),),
}



def create_class(class_name, class_fields, meta_fields):
    Meta = type('Meta', (), meta_fields)
    return type(class_name, (Model,), {**class_fields, 'Meta': Meta})


class PostgresqlDatabase(BaseDatabase):
    """PostgreSQL数据库接口"""

    def __init__(self, table_name_prefix=None, table_name_suffix=None) -> None:
        """"""
        self.db: PeeweePostgresqlDatabase = db
        self.db.connect()

        def get_table_name(original_name):
            if table_name_prefix:
                return f'{table_name_prefix}_{original_name}'
            elif table_name_suffix:
                return f'{original_name}_{table_name_suffix}'
            else:
                return original_name

        # 动态类创建索联合索引可能有问题，必要时手动创建联合索引
        self.DbBarData = create_class('DbBarData', db_bar_fields, {
            **db_bar_meta_fields,
            'table_name': get_table_name('dbbardata')
        })
        self.DbBarOverview = create_class('DbBarOverview', db_bar_overview_fields, {
            **db_bar_overview_meta_fields,
            'table_name': get_table_name('dbbaroverview')
        })
        self.DbTickData = create_class('DbTickData', db_tick_fields, {
            **db_tick_meta_fields,
            'table_name': get_table_name('dbtickdata')
        })
        self.DbTickOverview = create_class('DbTickOverview', db_tick_overview_fields, {
            **db_tick_overview_meta_fields,
            'table_name': get_table_name('dbtickoverview')
        })
        print(self.DbBarData._meta.indexes)

        self.db.create_tables([self.DbBarData, self.DbTickData, self.DbBarOverview, self.DbTickOverview])

    def save_bar_data(self, bars: List[BarData], stream: bool = False) -> bool:
        """保存K线数据"""
        # 读取主键参数
        bar: BarData = bars[0]
        symbol: str = bar.symbol
        exchange: Exchange = bar.exchange
        interval: Interval = bar.interval

        # 将BarData数据转换为字典，并调整时区
        data: list = []

        for bar in bars:
            bar.datetime = convert_tz(bar.datetime)

            d: dict = bar.__dict__
            d["exchange"] = d["exchange"].value
            d["interval"] = d["interval"].value
            d.pop("gateway_name")
            d.pop("vt_symbol")
            data.append(d)

        # 使用upsert操作将数据更新到数据库中 chunked批量操作加快速度
        with self.db.atomic():
            for c in chunked(data, 100):
                self.DbBarData.insert_many(c).on_conflict(
                    update={
                        self.DbBarData.volume: self.DbBarData.volume,
                        self.DbBarData.turnover: self.DbBarData.turnover,
                        self.DbBarData.open_interest: self.DbBarData.open_interest,
                        self.DbBarData.open_price: self.DbBarData.open_price,
                        self.DbBarData.high_price: self.DbBarData.high_price,
                        self.DbBarData.low_price: self.DbBarData.low_price,
                        self.DbBarData.close_price: self.DbBarData.close_price
                    },
                    conflict_target=(
                        self.DbBarData.symbol,
                        self.DbBarData.exchange,
                        self.DbBarData.interval,
                        self.DbBarData.datetime,
                    ),
                ).execute()

        # 更新K线汇总数据
        overview: self.DbBarOverview = self.DbBarOverview.get_or_none(
            self.DbBarOverview.symbol == symbol,
            self.DbBarOverview.exchange == exchange.value,
            self.DbBarOverview.interval == interval.value,
        )

        if not overview:
            overview = self.DbBarOverview()
            overview.symbol = symbol
            overview.exchange = exchange.value
            overview.interval = interval.value
            overview.start = bars[0].datetime
            overview.end = bars[-1].datetime
            overview.count = len(bars)
        elif stream:
            overview.end = bars[-1].datetime
            overview.count += len(bars)
        else:
            overview.start = min(bars[0].datetime, overview.start)
            overview.end = max(bars[-1].datetime, overview.end)

            s: ModelSelect = self.DbBarData.select().where(
                (self.DbBarData.symbol == symbol)
                & (self.DbBarData.exchange == exchange.value)
                & (self.DbBarData.interval == interval.value)
            )
            overview.count = s.count()

        overview.save()

        return True

    def save_tick_data(self, ticks: List[TickData], stream: bool = False) -> bool:
        """保存TICK数据"""
        # 读取主键参数
        tick: TickData = ticks[0]
        symbol: str = tick.symbol
        exchange: Exchange = tick.exchange

        # 将TickData数据转换为字典，并调整时区
        data: list = []

        for tick in ticks:
            tick.datetime = convert_tz(tick.datetime)

            d: dict = tick.__dict__
            d["exchange"] = d["exchange"].value
            d.pop("gateway_name")
            d.pop("vt_symbol")
            data.append(d)

        # 使用upsert操作将数据更新到数据库中
        with self.db.atomic():
            for d in data:
                self.DbTickData.insert(d).on_conflict(
                    update=d,
                    conflict_target=(
                        self.DbTickData.symbol,
                        self.DbTickData.exchange,
                        self.DbTickData.datetime,


                    ),
                ).execute()

            for c in chunked(data, 100):
                self.DbTickData.insert_many(c).on_conflict(
                    update={
                        self.DbTickData.name: self.DbTickData.name,
                        self.DbTickData.volume: self.DbTickData.volume,
                        self.DbTickData.turnover: self.DbTickData.turnover,
                        self.DbTickData.open_interest: self.DbTickData.open_interest,
                        self.DbTickData.last_price: self.DbTickData.last_price,
                        self.DbTickData.last_volume: self.DbTickData.last_volume,
                        self.DbTickData.limit_up: self.DbTickData.limit_up,
                        self.DbTickData.limit_down: self.DbTickData.limit_down,
                        self.DbTickData.open_price: self.DbTickData.open_price,
                        self.DbTickData.high_price: self.DbTickData.high_price,
                        self.DbTickData.low_price: self.DbTickData.low_price,
                        self.DbTickData.pre_close: self.DbTickData.pre_close,
                        self.DbTickData.bid_price_1: self.DbTickData.bid_price_1,
                        self.DbTickData.bid_price_2: self.DbTickData.bid_price_2,
                        self.DbTickData.bid_price_3: self.DbTickData.bid_price_3,
                        self.DbTickData.bid_price_4: self.DbTickData.bid_price_4,
                        self.DbTickData.bid_price_5: self.DbTickData.bid_price_5,
                        self.DbTickData.ask_price_1: self.DbTickData.ask_price_1,
                        self.DbTickData.ask_price_2: self.DbTickData.ask_price_2,
                        self.DbTickData.ask_price_3: self.DbTickData.ask_price_3,
                        self.DbTickData.ask_price_4: self.DbTickData.ask_price_4,
                        self.DbTickData.ask_price_5: self.DbTickData.ask_price_5,
                        self.DbTickData.bid_volume_1: self.DbTickData.bid_volume_1,
                        self.DbTickData.bid_volume_2: self.DbTickData.bid_volume_2,
                        self.DbTickData.bid_volume_3: self.DbTickData.bid_volume_3,
                        self.DbTickData.bid_volume_4: self.DbTickData.bid_volume_4,
                        self.DbTickData.bid_volume_5: self.DbTickData.bid_volume_5,
                        self.DbTickData.ask_volume_1: self.DbTickData.ask_volume_1,
                        self.DbTickData.ask_volume_2: self.DbTickData.ask_volume_2,
                        self.DbTickData.ask_volume_3: self.DbTickData.ask_volume_3,
                        self.DbTickData.ask_volume_4: self.DbTickData.ask_volume_4,
                        self.DbTickData.ask_volume_5: self.DbTickData.ask_volume_5,
                        self.DbTickData.localtime: self.DbTickData.localtime,
                    },
                    conflict_target=(
                        self.DbTickData.symbol,
                        self.DbTickData.exchange,
                        self.DbTickData.datetime,
                    ),
                ).execute()

        # 更新Tick汇总数据
        overview: self.DbTickOverview = self.DbTickOverview.get_or_none(
            self.DbTickOverview.symbol == symbol,
            self.DbTickOverview.exchange == exchange.value,
        )

        if not overview:
            overview: self.DbTickOverview = self.DbTickOverview()
            overview.symbol = symbol
            overview.exchange = exchange.value
            overview.start = ticks[0].datetime
            overview.end = ticks[-1].datetime
            overview.count = len(ticks)
        elif stream:
            overview.end = ticks[-1].datetime
            overview.count += len(ticks)
        else:
            overview.start = min(ticks[0].datetime, overview.start)
            overview.end = max(ticks[-1].datetime, overview.end)

            s: ModelSelect = self.DbTickData.select().where(
                (self.DbTickData.symbol == symbol)
                & (self.DbTickData.exchange == exchange.value)
            )
            overview.count = s.count()

        overview.save()

        return True

    def load_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval,
        start: datetime,
        end: datetime
    ) -> List[BarData]:
        """读取K线数据"""
        s: ModelSelect = (
            self.DbBarData.select().where(
                (self.DbBarData.symbol == symbol)
                & (self.DbBarData.exchange == exchange.value)
                & (self.DbBarData.interval == interval.value)
                & (self.DbBarData.datetime >= start)
                & (self.DbBarData.datetime <= end)
            ).order_by(self.DbBarData.datetime)
        )

        bars: List[BarData] = []
        for db_bar in s:
            bar: BarData = BarData(
                symbol=db_bar.symbol,
                exchange=Exchange(db_bar.exchange),
                datetime=datetime.fromtimestamp(db_bar.datetime.timestamp(), DB_TZ),
                interval=Interval(db_bar.interval),
                volume=db_bar.volume,
                turnover=db_bar.turnover,
                open_interest=db_bar.open_interest,
                open_price=db_bar.open_price,
                high_price=db_bar.high_price,
                low_price=db_bar.low_price,
                close_price=db_bar.close_price,
                gateway_name="DB"
            )
            bars.append(bar)

        return bars

    def load_tick_data(
        self,
        symbol: str,
        exchange: Exchange,
        start: datetime,
        end: datetime
    ) -> List[TickData]:
        """读取TICK数据"""
        s: ModelSelect = (
            self.DbTickData.select().where(
                (self.DbTickData.symbol == symbol)
                & (self.DbTickData.exchange == exchange.value)
                & (self.DbTickData.datetime >= start)
                & (self.DbTickData.datetime <= end)
            ).order_by(self.DbTickData.datetime)
        )

        ticks: List[TickData] = []
        for db_tick in s:
            tick: TickData = TickData(
                symbol=db_tick.symbol,
                exchange=Exchange(db_tick.exchange),
                datetime=datetime.fromtimestamp(db_tick.datetime.timestamp(), DB_TZ),
                name=db_tick.name,
                volume=db_tick.volume,
                turnover=db_tick.turnover,
                open_interest=db_tick.open_interest,
                last_price=db_tick.last_price,
                last_volume=db_tick.last_volume,
                limit_up=db_tick.limit_up,
                limit_down=db_tick.limit_down,
                open_price=db_tick.open_price,
                high_price=db_tick.high_price,
                low_price=db_tick.low_price,
                pre_close=db_tick.pre_close,
                bid_price_1=db_tick.bid_price_1,
                bid_price_2=db_tick.bid_price_2,
                bid_price_3=db_tick.bid_price_3,
                bid_price_4=db_tick.bid_price_4,
                bid_price_5=db_tick.bid_price_5,
                ask_price_1=db_tick.ask_price_1,
                ask_price_2=db_tick.ask_price_2,
                ask_price_3=db_tick.ask_price_3,
                ask_price_4=db_tick.ask_price_4,
                ask_price_5=db_tick.ask_price_5,
                bid_volume_1=db_tick.bid_volume_1,
                bid_volume_2=db_tick.bid_volume_2,
                bid_volume_3=db_tick.bid_volume_3,
                bid_volume_4=db_tick.bid_volume_4,
                bid_volume_5=db_tick.bid_volume_5,
                ask_volume_1=db_tick.ask_volume_1,
                ask_volume_2=db_tick.ask_volume_2,
                ask_volume_3=db_tick.ask_volume_3,
                ask_volume_4=db_tick.ask_volume_4,
                ask_volume_5=db_tick.ask_volume_5,
                localtime=db_tick.localtime,
                gateway_name="DB"
            )
            ticks.append(tick)

        return ticks

    def delete_bar_data(
        self,
        symbol: str,
        exchange: Exchange,
        interval: Interval
    ) -> int:
        """删除K线数据"""
        d: ModelDelete = self.DbBarData.delete().where(
            (self.DbBarData.symbol == symbol)
            & (self.DbBarData.exchange == exchange.value)
            & (self.DbBarData.interval == interval.value)
        )
        count: int = d.execute()

        # 删除K线汇总数据
        d2: ModelDelete = self.DbBarOverview.delete().where(
            (self.DbBarOverview.symbol == symbol)
            & (self.DbBarOverview.exchange == exchange.value)
            & (self.DbBarOverview.interval == interval.value)
        )
        d2.execute()
        return count

    def delete_tick_data(
        self,
        symbol: str,
        exchange: Exchange
    ) -> int:
        """删除TICK数据"""
        d: ModelDelete = self.DbTickData.delete().where(
            (self.DbTickData.symbol == symbol)
            & (self.DbTickData.exchange == exchange.value)
        )
        count: int = d.execute()

        # 删除Tick汇总数据
        d2: ModelDelete = self.DbTickOverview.delete().where(
            (self.DbTickOverview.symbol == symbol)
            & (self.DbTickOverview.exchange == exchange.value)
        )
        d2.execute()

        return count

    def get_bar_overview(self) -> List[BarOverview]:
        """查询数据库中的K线汇总信息"""
        # 如果已有K线，但缺失汇总信息，则执行初始化
        data_count: int = self.DbBarData.select().count()
        overview_count: int = self.DbBarOverview.select().count()
        if data_count and not overview_count:
            self.init_bar_overview()

        s: ModelSelect = self.DbBarOverview.select()
        overviews: List[BarOverview] = []
        for overview in s:
            overview.exchange = Exchange(overview.exchange)
            overview.interval = Interval(overview.interval)
            overviews.append(overview)
        return overviews

    def get_tick_overview(self) -> List[TickOverview]:
        """查询数据库中的Tick汇总信息"""
        s: ModelSelect = self.DbTickOverview.select()
        overviews: list = []
        for overview in s:
            overview.exchange = Exchange(overview.exchange)
            overviews.append(overview)
        return overviews

    def init_bar_overview(self) -> None:
        """初始化数据库中的K线汇总信息"""
        s: ModelSelect = (
            self.DbBarData.select(
                self.DbBarData.symbol,
                self.DbBarData.exchange,
                self.DbBarData.interval,
                fn.COUNT(self.DbBarData.id).alias("count")
            ).group_by(
                self.DbBarData.symbol,
                self.DbBarData.exchange,
                self.DbBarData.interval
            )
        )

        for data in s:
            overview: self.DbBarOverview = self.DbBarOverview()
            overview.symbol = data.symbol
            overview.exchange = data.exchange
            overview.interval = data.interval
            overview.count = data.count

            start_bar: self.DbBarData = (
                self.DbBarData.select()
                .where(
                    (self.DbBarData.symbol == data.symbol)
                    & (self.DbBarData.exchange == data.exchange)
                    & (self.DbBarData.interval == data.interval)
                )
                .order_by(self.DbBarData.datetime.asc())
                .first()
            )
            overview.start = start_bar.datetime

            end_bar: self.DbBarData = (
                self.DbBarData.select()
                .where(
                    (self.DbBarData.symbol == data.symbol)
                    & (self.DbBarData.exchange == data.exchange)
                    & (self.DbBarData.interval == data.interval)
                )
                .order_by(self.DbBarData.datetime.desc())
                .first()
            )
            overview.end = end_bar.datetime

            overview.save()
