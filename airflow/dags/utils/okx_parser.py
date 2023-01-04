import requests
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List
from collections import OrderedDict

INSTRUMENT_TYPES = ['SPOT', 'MARGIN', 'SWAP']
INSTRUMENTS_COLUMNS = OrderedDict(
    inst_type=str,
    inst_id=str,
    uly=str,
    category=int,
    base_ccy=str,
    quote_ccy=str,
    settle_ccy=str,
    ct_val=float,
    ct_mult=float,
    ct_val_ccy=str,
    opt_type=str,
    stk=float,
    list_time=datetime,
    exp_time=datetime,
    lever=float,
    tick_sz=float,
    lot_sz=float,
    min_sz=float,
    ct_type=str,
    alias=str,
    state=str
)

INSTRUMENTS_COLUMNS_MAPPER = dict(
    instType='inst_type',
    instId='inst_id',
    uly='uly',
    category='category',
    baseCcy='base_ccy',
    quoteCcy='quote_ccy',
    settleCcy='settle_ccy',
    ctVal='ct_val',
    ctMult='ct_mult',
    ctValCcy='ct_val_ccy',
    optType='opt_type',
    stk='stk',
    listTime='list_time',
    expTime='exp_time',
    lever='lever',
    tickSz='tick_sz',
    lotSz='lot_sz',
    minSz='min_sz',
    ctType='ct_type',
    alias='alias',
    state='state'
)

CANDLESTICKS_HISTORY_COLUMNS_DT = OrderedDict(
    ticker=str,
    ts=datetime,
    open=float,
    high=float,
    low=float,
    close=float,
    vol=float,
    vol_ccy=float,
    vol_ccy_quote=float,
    confirm=int
)

CANDLESTICKS_HISTORY_COLUMNS = ['ts', 'open', 'high', 'low', 'close', 'vol', 'vol_ccy', 'vol_ccy_quote', 'confirm']

class OKXParser:

    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }

    def __init__(self, url='https://aws.okx.com'):
        """
        Class for parsing OKX data via REST API v5
        :param url: REST API URL
        """
        self.url = url

    def preprocess(self, df, cols):
        result = df.copy()
        for col in df.columns:
            if cols[col] == datetime:
                result[col] = pd.to_datetime(result[col], unit='ms', utc=True)
            elif cols[col] == str:
                pass
            else:
                result[col] = result[col].astype(cols[col])
        return result

    def get_instruments(self, instType, uly=None, instId=None) -> pd.DataFrame:
        """
        Get all the instruments by instrument type

        `GET /api/v5/public/instruments`

        :param instType: Instrument type. Currently supported: [SPOT, SWAP, MARGIN]
        :param uly: Underlying, only applicable to FUTURES/SWAP/OPTION
        :param instId: Instrument ID (not required)
        :return: pd.DataFrame
        """
        if instType not in INSTRUMENT_TYPES:
            raise ValueError(f'{instType} is not a type of an instrument. Please use one of {INSTRUMENT_TYPES}')
        command = '/api/v5/public/instruments'
        params = dict(
            instType=instType,
            uly=uly,
            instId=instId
        )
        result = requests.get(self.url + command, params=params, headers=self.headers)
        result = pd.DataFrame(result.json()['data'])
        if set(result.columns) != set(INSTRUMENTS_COLUMNS_MAPPER.keys()):
            raise ValueError('Please fill underlying asset as uly parameter')
        result = result.rename(mapper=INSTRUMENTS_COLUMNS_MAPPER, axis='columns')
        result = result.replace('', np.nan, )
        return result[INSTRUMENTS_COLUMNS.keys()]

    def get_candlesticks_history(self, instId, after=None, before=None, bar=None, limit=None) -> pd.DataFrame:
        """

        :param instId:
        :param after:
        :param before:
        :param bar:
        :param limit:
        :return:
        """
        command = '/api/v5/market/history-candles'
        params = dict(
            instId=instId,
            after=after,
            before=before,
            bar=bar,
            limit=limit
        )
        result = requests.get(self.url + command, params=params, headers=self.headers)
        result = pd.DataFrame(result.json()['data'], columns=CANDLESTICKS_HISTORY_COLUMNS)
        result.insert(0, column='ticker', value=instId)
        return result

