from trader.backtest.model import BacktestPosition
from trader.core.super_enum import OrderSide
import pytest

from trader.core.exception import LiquidationError


def test_position_long_1x_profit():
    pos_long = BacktestPosition(
        symbol="XYZ",
        entry_time=1,
        entry_price=100,
        side=OrderSide.LONG,
        amount=100.0,
        quantity=1.0,
        leverage=1,
    )

    assert pos_long.profit == .0

    pos_long.update(200)
    assert pos_long.profit == 100.0

    pos_long.update(400)
    assert pos_long.profit == 300.0

    pos_long.liquidation_check(low_price=0.1, high_price=500, balance=100.0)


def test_position_long_2x_profit():
    pos_long2x = BacktestPosition(symbol="XYZ", entry_price=100, entry_time=1, amount=100.0, side=OrderSide.LONG, leverage=2)
    assert pos_long2x.profit == .0

    pos_long2x.update(200)
    assert pos_long2x.profit == 200.0

    pos_long2x.update(400)
    assert pos_long2x.profit == 600.0

    pos_long2x.liquidation_check(low_price=50.01, high_price=500, balance=100.0)

    with pytest.raises(LiquidationError):
        pos_long2x.liquidation_check(low_price=49.99, high_price=500, balance=100.0)


def test_position_short_1x_profit():
    pos_short = BacktestPosition(symbol="XYZ", entry_price=100, entry_time=1, amount=100.0, side=OrderSide.SHORT, leverage=1)
    assert pos_short.profit == .0

    pos_short.update(200)
    assert pos_short.profit == -100.0

    pos_short.update(400)
    assert pos_short.profit == -300.0

    pos_short.liquidation_check(low_price=10, high_price=199, balance=100.0)

    with pytest.raises(LiquidationError):
        pos_short.liquidation_check(low_price=10, high_price=201, balance=100.0)


def test_position_short_2x_profit():
    pos_short2x = BacktestPosition(symbol="XYZ", entry_price=100, entry_time=1, amount=100.0, side=OrderSide.SHORT, leverage=2)

    assert pos_short2x.profit == .0

    pos_short2x.update(200)
    assert pos_short2x.profit == -200.0

    pos_short2x.update(400)
    assert pos_short2x.profit == -600.0

    pos_short2x.liquidation_check(low_price=10, high_price=149, balance=100.0)
    with pytest.raises(LiquidationError):
        pos_short2x.liquidation_check(low_price=10, high_price=151, balance=100.0)
