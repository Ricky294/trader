import numpy as np

from trader.core.util.vectorized.trade import (
    calculate_money_fee,
    reduce_money_with_fee,
    calculate_quantity_fee,
    reduce_quantity_with_fee,
    cross,
)


def test_cross():
    a = np.array([1, 2, 3, 4, 2, 1, 5])
    assert np.array_equal(cross(a < 2),  [False, False, False, False, False, True, False])
    assert np.array_equal(cross(a <= 2), [False, False, False, False, True, False, False])
    assert np.array_equal(cross(a > 2),  [False, False, True, False, False, False, True])
    assert np.array_equal(cross(a >= 2), [False, True, False, False, False, False, True])

    b = np.array([2, 1, 3, 5, 3, 0, 1])
    assert np.array_equal(cross(a > b),  [False, True, False, False, False, True, False])
    assert np.array_equal(cross(a >= b), [False, True, False, False, False, True, False])


def test_reduce_money_with_fee():
    quantity = 0.001
    price = 50_000

    # fee: 0.0%, leverage: 1x
    assert 50 == reduce_money_with_fee(quantity=quantity, price=price, fee_rate=.0, leverage=1)

    # fee: 0.1%, leverage: 1x
    assert 99.8 == reduce_money_with_fee(quantity=quantity, price=price, fee_rate=.001, leverage=2)

    # fee: 1%, leverage: 2x
    assert 98 == reduce_money_with_fee(quantity=quantity, price=price, fee_rate=.01, leverage=2)

    # fee: 1%, leverage: 10x
    assert 450 == reduce_money_with_fee(quantity=quantity, price=price, fee_rate=.01, leverage=10)


def test_calculate_money_fee():
    amount = 100

    # fee: 0%
    assert 0 == calculate_money_fee(amount=amount, fee_rate=.0, leverage=1)

    # fee: 1%, leverage: 1x
    assert 1 == calculate_money_fee(amount=amount, fee_rate=.01, leverage=1)

    # fee: 1%, leverage: 2x
    assert 2 == calculate_money_fee(amount=amount, fee_rate=.01, leverage=2)

    # fee 0.1%, leverage: 10x
    assert 1 == calculate_money_fee(amount=amount, fee_rate=.001, leverage=10)

    # fee: 1%, leverage: 10x
    assert 10 == calculate_money_fee(amount=amount, fee_rate=.01, leverage=10)


def test_calculate_quantity_fee():
    # fee: 1%
    assert 0.01 == calculate_quantity_fee(quantity=1, fee_rate=0.01)

    # fee: 2%
    assert -0.02 == calculate_quantity_fee(quantity=-1, fee_rate=0.02)

    # fee: 1%
    assert 0.2 == calculate_quantity_fee(quantity=5, fee_rate=0.04)


def test_reduce_quantity_with_fee():
    assert 0.99 == reduce_quantity_with_fee(quantity=1, fee_rate=0.01)

    assert -0.98 == reduce_quantity_with_fee(quantity=-1, fee_rate=0.02)

    assert 4.98 == reduce_quantity_with_fee(quantity=5, fee_rate=0.004)
