from trader.backtest.util import is_stop_loss_hit, is_take_profit_hit, get_closer_order, get_filled_first
from trader.core.const.trade_actions import SELL, BUY
from trader.core.model import StopMarketOrder, TakeProfitMarketOrder, LimitOrder, MarketOrder


def test_is_stop_loss_hit():
    # False
    assert not is_stop_loss_hit(low_price=5, high_price=10, order=StopMarketOrder(symbol='', side=SELL, stop_price=2))
    assert not is_stop_loss_hit(low_price=5, high_price=10, order=StopMarketOrder(symbol='', side=BUY, stop_price=20))

    # True
    assert is_stop_loss_hit(low_price=5, high_price=10, order=StopMarketOrder(symbol='', side=SELL, stop_price=7))
    assert is_stop_loss_hit(low_price=5, high_price=10, order=StopMarketOrder(symbol='', side=SELL, stop_price=20))
    assert is_stop_loss_hit(low_price=5, high_price=10, order=StopMarketOrder(symbol='', side=BUY, stop_price=7))


def test_is_take_profit_hit():
    # False
    assert not is_take_profit_hit(low_price=5, high_price=10, order=TakeProfitMarketOrder(symbol='', side=SELL, stop_price=20))

    # True
    assert is_take_profit_hit(low_price=5, high_price=10, order=TakeProfitMarketOrder(symbol='', side=SELL, stop_price=7))
    assert is_take_profit_hit(low_price=5, high_price=10, order=TakeProfitMarketOrder(symbol='', side=BUY, stop_price=7))


def test_stopped_loss_or_took_profit():
    assert get_closer_order(
        high_price=200,
        low_price=100,
        open_price=140,
        order1=TakeProfitMarketOrder(symbol='', side=BUY, stop_price=199),
        order2=StopMarketOrder(symbol='', side=BUY, stop_price=101)
    ).stop_price == 101

    assert get_closer_order(
        high_price=200,
        low_price=100,
        open_price=149,
        order1=TakeProfitMarketOrder(symbol='', side=SELL, stop_price=199),
        order2=StopMarketOrder(symbol='', side=SELL, stop_price=101)
    ).stop_price == 101

    assert get_closer_order(
        high_price=200,
        low_price=100,
        open_price=160,
        order1=TakeProfitMarketOrder(symbol='', side=BUY, stop_price=199),
        order2=StopMarketOrder(symbol='', side=BUY, stop_price=101)
    ).stop_price == 199

    assert get_closer_order(
        high_price=200,
        low_price=100,
        open_price=190,
        order1=TakeProfitMarketOrder(symbol='', side=SELL, stop_price=199),
        order2=StopMarketOrder(symbol='', side=SELL, stop_price=101)
    ).stop_price == 199

    assert get_closer_order(
        high_price=200,
        low_price=100,
        open_price=150,
        order1=LimitOrder(symbol='', side=BUY, price=170, amount=500),
        order2=TakeProfitMarketOrder(symbol='', side=SELL, stop_price=180)
    ).price == 170

    assert get_closer_order(
        high_price=200,
        low_price=100,
        open_price=150,
        order1=StopMarketOrder(symbol='', side=SELL, stop_price=140),
        order2=LimitOrder(symbol='', side=SELL, price=170, amount=500),
    ).stop_price == 140


def test_get_filled_first():
    assert get_filled_first(
        high_price=200,
        low_price=100,
        open_price=120,
        take_profit_order=TakeProfitMarketOrder(symbol='', side=SELL, stop_price=160),
        stop_order=StopMarketOrder(symbol='', side=SELL, stop_price=110),
        exit_order=MarketOrder(symbol='', side=SELL, amount=500),
        trailing_stop_order=None,
    ).type == 'MARKET'
