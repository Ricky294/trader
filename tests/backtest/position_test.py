from trader.backtest.model import BacktestPosition
from trader.core.const.trade_actions import LONG, SHORT
import pytest

from trader.core.exception import LiquidationError


def test_position_long_1x_profit():
    pos_long = BacktestPosition(
        symbol="XYZ", entry_price=100, entry_time=1, money=100.0, side=LONG, leverage=1, entry_fee=.0
    )

    assert pos_long.profit == .0

    pos_long.update_profit(200)
    assert pos_long.profit == 100.0

    pos_long.update_profit(400)
    assert pos_long.profit == 300.0

    pos_long.liquidation_check(low_price=0.1, high_price=500, balance=100.0)


def test_position_long_2x_profit():
    pos_long2x = BacktestPosition(symbol="XYZ", entry_price=100, entry_time=1, money=100.0, side=LONG, leverage=2,
                                  entry_fee=.0)
    assert pos_long2x.profit == .0

    pos_long2x.update_profit(200)
    assert pos_long2x.profit == 200.0

    pos_long2x.update_profit(400)
    assert pos_long2x.profit == 600.0

    pos_long2x.liquidation_check(low_price=50.01, high_price=500, balance=100.0)

    with pytest.raises(LiquidationError):
        pos_long2x.liquidation_check(low_price=49.99, high_price=500, balance=100.0)


def test_position_short_1x_profit():
    pos_short = BacktestPosition(symbol="XYZ", entry_price=100, entry_time=1, money=100.0, side=SHORT, leverage=1,
                                 entry_fee_rate=.0)
    assert pos_short.profit == .0

    pos_short.update_profit(200)
    assert pos_short.profit == -100.0

    pos_short.update_profit(400)
    assert pos_short.profit == -300.0

    pos_short.liquidation_check(low_price=10, high_price=199, balance=100.0)

    with pytest.raises(LiquidationError):
        pos_short.liquidation_check(low_price=10, high_price=201, balance=100.0)


def test_position_short_2x_profit():
    pos_short2x = BacktestPosition(symbol="XYZ", entry_price=100, entry_time=1, money=100.0, side=SHORT, leverage=2,
                                   entry_fee=.0)

    assert pos_short2x.profit == .0

    pos_short2x.update_profit(200)
    assert pos_short2x.profit == -200.0

    pos_short2x.update_profit(400)
    assert pos_short2x.profit == -600.0

    pos_short2x.liquidation_check(low_price=10, high_price=149, balance=100.0)
    with pytest.raises(LiquidationError):
        pos_short2x.liquidation_check(low_price=10, high_price=151, balance=100.0)
