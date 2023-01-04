create table if not exists crypto_trade.candlesticks_history (
    ticker String,
    ts DateTime(),
    open Float32,
    high Float32,
    low Float32,
    close Float32,
    vol Float32,
    vol_ccy Float32,
    vol_ccy_quote Float32, 
    confirm UInt8,
    updated DateTime() default now()
)
engine = MergeTree()
order by (ticker, ts)
partition by toDateTime(ts, 1)
;

drop database if exists default;