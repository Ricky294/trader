from trader.backtest import BacktestOrderGroup
from trader.backtest.balance import BacktestBalance
from trader.core import PositionError
from trader.backtest.globals import candle_feed
from trader.core.const.trade_actions import BUY
from trader.core.model import MarketOrder


def test_order_group_with_close_order():

    balance = BacktestBalance(asset="USDT", total=1_000, available=1_000)

    og = BacktestOrderGroup(
        entry_order=MarketOrder(symbol="XYZ", side=BUY, money=1_000),
    )

    candle_feed.latest_high_price = .0
    candle_feed.latest_open_price = .0
    candle_feed.latest_low_price = .0
    candle_feed.latest_close_price = .0
    candle_feed.latest_open_time = 1

    for i in range(10):
        candle_feed.latest_open_time = i + 1
        candle_feed.latest_close_price += 500
        candle_feed.latest_low_price += 400
        candle_feed.latest_high_price += 600

        if candle_feed.latest_high_price > 1_500:
            try:
                og.create_close_order(price=2_000)
            except PositionError:
                break

        og(balance=balance, symbol="XYZ", maker_fee_rate=0.0, taker_fee_rate=0.0, leverage=1)

    x = 5

    pass
