from trader.backtest import BacktestPosition
from trader.core.const.trade_actions import LONG
from copy import deepcopy


pos1_ = BacktestPosition(symbol="XYZ", entry_price=2, entry_time=1, money=50.0, side=LONG, leverage=1)
pos2_ = BacktestPosition(symbol="XYZ", entry_price=2, entry_time=1, money=50.0, side=LONG, leverage=1)
pos3_ = BacktestPosition(symbol="XYZ", entry_price=2, entry_time=2, money=50.0, side=LONG, leverage=1)


def test_position():
    pos1 = deepcopy(pos1_)
    assert 50.0 == pos1.money()
    assert 50.0 == pos1.money(True)
    assert 25.0 == pos1.quantity()
    assert 25.0 == pos1.quantity(True)

    assert pos1.is_closed() is False

    pos1.set_close(time=2, price=4)

    assert pos1.is_closed() is True

    assert 50.0 == pos1.profit()


def test_equality():
    pos1 = deepcopy(pos1_)
    pos2 = deepcopy(pos2_)
    pos3 = deepcopy(pos3_)

    assert pos1 == pos2

    assert len({pos1, pos2, pos3}) == 2
