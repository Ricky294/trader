from trader.core.util.trade import calculate_money, calculate_fee


def test_calculate_money():
    quantity = 0.001
    price = 50_000

    # fee: 0.0%, leverage: 1x
    assert 50 == calculate_money(quantity=quantity, price=price, fee_rate=.0, leverage=1)

    # fee: 0.1%, leverage: 1x
    assert 99.8 == calculate_money(quantity=quantity, price=price, fee_rate=.001, leverage=2)

    # fee: 1%, leverage: 2x
    assert 98 == calculate_money(quantity=quantity, price=price, fee_rate=.01, leverage=2)

    # fee: 1%, leverage: 10x
    assert 450 == calculate_money(quantity=quantity, price=price, fee_rate=.01, leverage=10)


def test_calculate_fee():
    quantity = 0.001
    price = 50_000

    # fee: 0%
    assert 0 == calculate_fee(quantity=quantity, price=price, fee_rate=.0, leverage=1)

    # fee: 1%, leverage: 1x
    assert 0.5 == calculate_fee(quantity=quantity, price=price, fee_rate=.01, leverage=1)

    # fee: 1%, leverage: 2x
    assert 2 == calculate_fee(quantity=quantity, price=price, fee_rate=.01, leverage=2)

    # fee 0.1%, leverage: 10x
    assert 5 == calculate_fee(quantity=quantity, price=price, fee_rate=.001, leverage=10)

    # fee: 1%, leverage: 10x
    assert 50 == calculate_fee(quantity=quantity, price=price, fee_rate=.01, leverage=10)
