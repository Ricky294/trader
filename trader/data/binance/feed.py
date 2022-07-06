from __future__ import annotations

from datetime import datetime
from typing import Iterable, Type

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

from trader.data.database import CandleStorage
from trader.data.log import get_data_logger
from trader.data.util import interval_to_seconds
from trader.data.enumerate import Market
from trader.data.model import Candles
from trader.data.schema import OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME
from trader.data.binance.schema import NAME_TO_INDEX

SPOT_CANDLE_URL = "https://api.binance.com/api/v3/klines"
FUTURES_CANDLE_URL = "https://fapi.binance.com/fapi/v1/klines"


def filter_columns(array: np.ndarray, columns: Iterable[str]):
    """
    Only keeps data from `array` specified in `columns`.

    :param array: Data
    :param columns: Columns to keep.
    :return: numpy array generator
    """

    return tuple(array[:, NAME_TO_INDEX[col]] for col in columns)


def get_first_candle_timestamp(
        symbol: str,
        interval: str,
        market: str | Market,
) -> int:
    """Returns the first available candle data timestamp on binance `symbol`, `interval`, `market` in seconds."""

    if str(market).upper() == "SPOT":
        url = SPOT_CANDLE_URL
    elif str(market).upper() == "FUTURES":
        url = FUTURES_CANDLE_URL
    else:
        raise ValueError(f"Invalid market type: {market}")

    return int(requests.get(
        f"{url}?symbol={symbol.upper()}&interval={interval}&limit=1&startTime=0"
    ).json()[-1][0] / 1000)


def _build_url(
        symbol: str,
        interval: str,
        market: str | Market,
        end_ts: float | int = None,
        limit=1000,
):
    if str(market).upper() == "SPOT":
        url = SPOT_CANDLE_URL
    elif str(market).upper() == "FUTURES":
        url = FUTURES_CANDLE_URL
    else:
        raise ValueError(f"Invalid market type: {market}")

    query_params = f"symbol={symbol.upper()}&interval={interval}&limit={limit}"

    if end_ts is not None:
        query_params += f"&endTime={int(end_ts * 1000)}"

    return f"{url}?{query_params}"


def estimate_total_items(
        symbol: str,
        interval: str,
        market: str | Market,
        start_ts: float | int,
        end_ts: float | int = None,
):
    """Estimated the total number of candles to download."""

    first_ts = get_first_candle_timestamp(symbol, interval, market)
    if start_ts > first_ts:
        first_ts = start_ts

    last_ts = int(datetime.now().timestamp())
    if end_ts is not None and end_ts < last_ts:
        last_ts = end_ts

    total_items = (last_ts - first_ts) / interval_to_seconds(interval)

    return total_items


def get_candles_as_list(
        symbol: str,
        interval: str,
        market: str | Market,
        start_ts: float | int,
        end_ts: float | int = None,
        limit=1000,
) -> list[list]:
    """
    Returns `symbol` historical candles from binance `market`
    on `interval` from `start_ts` to `end_ts`.

    :param symbol: Cryptocurrency pair (e.g BTCUSDT).
    :param interval: Timeframe between candles.
    :param market: SPOT or FUTURES market
    :param start_ts: Start timestamp in seconds.
    :param end_ts: End timestamp in seconds. If None it defaults to latest.
    :param limit: Maximum number of fetched candles by iteration.
    :return: list of lists
    """

    url = _build_url(symbol=symbol, interval=interval, market=market, end_ts=end_ts)
    total_items = int(estimate_total_items(symbol=symbol, interval=interval, market=market, start_ts=start_ts, end_ts=end_ts))

    url_with_start_ts = f"{url}&startTime={int(start_ts * 1000)}"

    data = []

    get_data_logger().info(f"Downloading {symbol} candles in {interval} intervals from binance {market} market.")

    with tqdm(total=total_items) as pbar:
        while True:
            new_data: list[list] = requests.get(url_with_start_ts).json()
            data.extend(new_data)
            pbar.update(len(new_data))

            if len(new_data) < limit:
                pbar.close()
                break

            url_with_start_ts = f"{url}&startTime={new_data[-1][0] + 1}"

    get_data_logger().info(f"Finished downloading ≈{total_items} candle(s).")
    return data


def get_candles_as_array(
        symbol,
        interval: str,
        market: str | Market,
        start_ts: float | int,
        end_ts: float | int = None,
        columns: Iterable[str] = (OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME),
) -> np.ndarray:
    """
    Returns `symbol` historical candles from binance FUTURES or SPOT
    on `interval` from `start_ts` to `end_ts`.

    `column` options:
        - OPEN_TIME
        - OPEN_PRICE
        - HIGH_PRICE
        - LOW_PRICE
        - CLOSE_TIME
        - VOLUME
        - CLOSE_TIME
        - QUOTE_ASSET_VOLUME
        - NUMBER_OF_TRADES
        - TAKER_BUY_BASE_ASSET_VOLUME
        - TAKER_BUY_QUOTE_ASSET_VOLUME

    :param symbol: Cryptocurrency pair (e.g BTCUSDT).
    :param interval: Timeframe between candles.
    :param market: SPOT=1 or FUTURES=2 market
    :param start_ts: Start timestamp in seconds.
    :param end_ts: End timestamp in seconds. If None it defaults to latest.
    :param columns: Included columns in numpy array.
    :return: numpy array
    """

    candle_list = get_candles_as_list(
        symbol=symbol,
        interval=interval,
        market=market,
        start_ts=start_ts,
        end_ts=end_ts,
    )

    candle_array = np.array(candle_list, dtype=np.float)

    # Convert OPEN TIME from milliseconds to seconds
    candle_array[:, 0] /= 1000
    # Convert CLOSE TIME from milliseconds to seconds
    candle_array[:, 6] /= 1000

    filtered_candle_array = np.vstack(filter_columns(candle_array, columns)).T
    return filtered_candle_array[:-1]


def get_candles_as_dataframe(
        base_currency: str,
        quote_currency: str,
        interval: str,
        market: str | Market,
        start_ts: float | int,
        end_ts: float | int = None,
        columns: Iterable[str] = (OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME),
):
    """
    Returns `symbol` historical candles from binance futures
    on `interval` from `start_ts` to `end_ts`.

    `column` options:
        - OPEN_TIME
        - OPEN_PRICE
        - HIGH_PRICE
        - LOW_PRICE
        - CLOSE_TIME
        - VOLUME
        - CLOSE_TIME
        - QUOTE_ASSET_VOLUME
        - NUMBER_OF_TRADES
        - TAKER_BUY_BASE_ASSET_VOLUME
        - TAKER_BUY_QUOTE_ASSET_VOLUME

    :param base_currency: Left side of the currency pair (e.g. 'BTC').
    :param quote_currency: Right side of the currency pair (e.g. 'USDT').
    :param interval: Timeframe between candles.
    :param market: SPOT=1 or FUTURES=2 market
    :param start_ts: Start timestamp in seconds.
    :param end_ts: End timestamp in seconds. If None it defaults to latest.
    :param columns: Included columns in pandas dataframe.
    :return: pandas DataFrame
    """

    symbol = base_currency + quote_currency
    candles = get_candles_as_array(
        symbol=symbol,
        interval=interval,
        market=market,
        start_ts=start_ts,
        end_ts=end_ts,
        columns=columns,
    )

    df = pd.DataFrame(candles, columns=tuple(columns))
    df.meta = {
        "base_currency": base_currency,
        "quote_currency": quote_currency,
    }

    return df


def get_tohlcv_candles(
        base_currency: str,
        quote_currency: str,
        interval: str,
        market: str | Market,
        start_ts: float | int,
        end_ts: float | int = None,
):
    """
    Returns a Candles object with the following schema:
        - OPEN_TIME
        - OPEN_PRICE
        - HIGH_PRICE
        - LOW_PRICE
        - CLOSE_TIME
        - VOLUME
    """
    symbol = base_currency + quote_currency

    np_candles = get_candles_as_array(
        symbol=symbol,
        interval=interval,
        market=market,
        start_ts=start_ts,
        end_ts=end_ts,
        columns=(OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME),
    )

    return Candles(
        np_candles, symbol=symbol, interval=interval, market=market,
        meta={"base_currency": base_currency, "quote_currency": quote_currency},
    )


def get_store_candles(
        base_currency: str,
        quote_currency: str,
        interval: str,
        market: str | Market,
        storage_type: Type[CandleStorage],
        storage_dir="data/binance",
        columns=(OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME),
):
    """
    Downloads data from binance if not present in local storage under `storage_path`
    and appends local storage with the new data.

    :param base_currency: Left side of the currency pair (e.g. 'BTC').
    :param quote_currency: Right side of the currency pair (e.g. 'USDT').
    :param interval: Candle sampling timeframe (e.g. '1h').
    :param market: Gets the historical candles from market.
    :param storage_type:
    :param storage_dir: Path to store candle data.
    :param columns: Columns to include in the result list
    :return: Candles object
    """

    symbol = base_currency + quote_currency
    storage = storage_type(dir_path=storage_dir, symbol=symbol, interval=interval, market=market)

    try:
        stored_data = storage.get()
        last_data = stored_data[-1] + 1
        latest_open = int(last_data[0])
    except (FileNotFoundError, KeyError):
        latest_open = 0

    downloaded_data = get_candles_as_array(
        symbol=symbol,
        interval=interval,
        market=market,
        start_ts=latest_open,
        columns=columns,
    )

    if downloaded_data.size != 0:
        storage.append(downloaded_data)

    return Candles(
        storage.get(), symbol=symbol, interval=interval, market=market,
        meta={"base_currency": base_currency, "quote_currency": quote_currency},
    )
