from trader.backtest import BacktestPosition


def test_long_position():
    bp = BacktestPosition(
        symbol="BTCUSDT",
        entry_time=1,
        entry_price=100,
        entry_quantity=1,
        leverage=1,
    )

    assert 100 == bp.profit()

    bp.adjust(2, 200, 1)

    assert 100 == bp.profit()
    assert 500 == bp.profit()


def test_short_position():
    bp = BacktestPosition(
        symbol="BTCUSDT",
        entry_time=1,
        entry_price=100,
        entry_quantity=-1,
        leverage=1
    )

    assert -100 == bp.profit()

    bp.adjust(2, 200, -1)

    assert -100 == bp.profit()

