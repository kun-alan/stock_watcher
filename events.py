#!/usr/bin/env python
import os

import pandas as pd
import numpy as np

from stock_common.conf.config import Config
from stock_common.lib.database import Database
from stock_common.lib import util

CONFIGS = Config.get_configs()
logging = CONFIGS.get_logging()
db = Database(CONFIGS)


PRICE_LEVELS = [
    {
        'symbol': 'KLIC',
        'levels': [19, 22],
        'last_level': 22,
    },
    {
        'symbol': 'PG',
        'levels': [86, 94],
        'last_level': 86,
    },
    {
        'symbol': 'FFIV',
        'levels': [88, 117, 146],
        'last_level': 117,
    },
]


GET_QUOTES_RESULT = [
    {
        'PE': 18.12,
        'change_pct': '-0.82%',
        'date': '10/25/2017',
        'index': 'KLIC',
        'last': 21.8,
        'short_ratio': 1.0,
        'time': '4:00pm'
    },
    {
        'PE': 15.53,
        'change_pct': '-0.14%',
        'date': '10/25/2017',
        'index': 'PG',
        'last': 86.86,
        'short_ratio': 4.51,
        'time': '4:00pm'
    },
    {
        'PE': 19.82,
        'change_pct': '+0.13%',
        'date': '10/25/2017',
        'index': 'FFIV',
        'last': 119.31,
        'short_ratio': 4.61,
        'time': '4:00pm'
    },
]


def get_collections_dict(client):
    """
    Last run returned:

    {'admin': ['system.users', 'system.version'],
     'local': ['startup_log'],
     'stock_price': ['prices'],
     'stock_recommender': ['model_results', 'ticker_symbols'],
     'stock_watcher': ['events', 'price_levels']}
    """
    return {
        dbname: client[dbname].collection_names()
        for dbname in client.database_names()
    }


def get_docs(client, dbname, colname, search={}):
    return list(client[dbname][colname].find(search))


def get_price_levels(client):
    return PRICE_LEVELS
    # return get_docs(client, 'stock_watcher', 'price_levels')


@db.connect('MONGO')
def set_stocks_in_mongo(client, price_levels):
    """
    Replace price_levels collection in mongo
    """
    collection = client['stock_watcher'].price_levels
    collection.delete_many({})
    collection.insert_many(price_levels)


@db.connect('MONGO')
def get_stocks_from_mongo(client):
    """
    Read price_levels and merge with dataframe returned by get_quotes
    """
    price_levels_docs = get_price_levels(client)
    df_price_levels = pd.DataFrame(price_levels_docs)
    symbols = list(df_price_levels.symbol)

    df_event_quotes = get_event_quotes(symbols).reset_index()

    df_merged = df_price_levels.merge(
        df_event_quotes, left_on='symbol', right_on='index')
    del df_merged['index']

    # calculate proximity to levels as equal size list
    # take min as new column
    # eventually use last_level as way to eliminate already reported from list
    # sort Dataframe by proximity column for mix of buys and sells!
    # add last_level to PRICE_LEVELS and argparse for updating mongo collection
    # UI could post [50, 66*, 80] as way of updating levels AND last_level

    df_merged.levels = df_merged.levels.apply(lambda x: np.array(x))
    df_merged['proximity'] = abs(df_merged.levels - df_merged['last']) / df_merged.levels
    df_merged['min_proximity'] = df_merged.proximity.apply(lambda x: min(abs(x)))
    # df_merged['ranked_proximity'] = 1 / abs(df_merged.proximity)
    df_merged['which_level'] = df_merged['proximity'].apply(lambda x:x<0.02)

    return df_merged


def get_event_quotes(symbols):
    # return util.get_quote(symbols)
    return pd.DataFrame(GET_QUOTES_RESULT)


def get_merged_quotes():
    return get_stocks_from_mongo()


if __name__ == '__main__':
    # set_stocks_in_mongo(PRICE_LEVELS)
    df_merged = get_merged_quotes()
    print(df_merged)
    import pdb; pdb.set_trace()