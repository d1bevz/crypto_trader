from airflow import DAG
from airflow.decorators import task
from airflow.models import variable, connection
from airflow.hooks.base import BaseHook
from airflow.utils import db
from sqlalchemy import create_engine
import logging
import pendulum, datetime, time
from datetime import timedelta
log = logging.getLogger(__name__)
log.info('Importing parser')
from utils.okx_parser import OKXParser, CANDLESTICKS_HISTORY_COLUMNS_DT
import os


parser = OKXParser()
log.info('Parse connection')
clickhouse = BaseHook.get_connection('MY_PROD_DATABASE')
print(clickhouse.get_uri())
log.info('Creating clickhouse engine')
clickhouse = create_engine(clickhouse.get_uri())

# instruments = [
#     'BTC-USDT', 'ETH-USDT', 'OKB-USDT', 'OKT-USDT', 'LTC-USDT',
#     'DOT-USDT', 'DOGE-USDT', 'LUNA-USDT', 'PEOPLE-USDT',
#     'SHIB-USDT', 'TONCOIN-USDT', 'NEAR-USDT', 'TRX-USDT',
#     'WAVES-USDT'
# ]
instruments = ['BTC-USDT', 'ETH-USDT']


with DAG(
        dag_id='get_candlesticks_history_by_minutes',
        schedule_interval='0 * * * *',
        start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
        catchup=True,
        tags=['mining', 'market_data', 'minutes']
) as dag:
    log.info('Starting DAG')
    for instrument in instruments:
        @task(task_id=f"get_{instrument}", retries=3, execution_timeout=timedelta(seconds=10))
        def get_candlesticks_history(instrument_id, ts=None):
            ts = int(time.mktime(pendulum.parse(ts).timetuple()) * 1000)
            candlesticks_history = parser.get_candlesticks_history(instrument_id, after=ts, limit=60)
            if len(candlesticks_history)>0:
                candlesticks_history = parser.preprocess(candlesticks_history, CANDLESTICKS_HISTORY_COLUMNS_DT)
                log.info('Loading data')
                candlesticks_history.to_sql(name='candlesticks_history', con=clickhouse, if_exists='append', index=False)
                return 'Success'
            else:
                return 'No data'


        get_candlesticks_history(instrument)
