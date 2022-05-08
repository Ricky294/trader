#!/usr/bin/env python3
"""
2021-03-26: Reverse-engineer by searching for the following terms in features*.js:
    - bracketMaintenanceMarginRate
    - cumFastMaintenanceAmount
    - bracketNotionalFloor
    - bracketNotionalCap
"""


# (max) position, maintenance margin, maintenance amount
from __future__ import annotations

import pandas as pd

from trader.core.const.trade_actions import BUY, SELL
from trader.core.enumerate import OrderSide
from trader.core.exception import BalanceError
from trader.core.util.trade import side_to_int

maint_lookup_table = [
    (     50_000,  0.4,           0),
    (    250_000,  0.5,          50),
    (  1_000_000,  1.0,       1_300),
    ( 10_000_000,  2.5,      16_300),
    ( 20_000_000,  5.0,     266_300),
    ( 50_000_000, 10.0,   1_266_300),
    (100_000_000, 12.5,   2_516_300),
    (200_000_000, 15.0,   5_016_300),
    (300_000_000, 25.0,  25_016_300),
    (500_000_000, 50.0, 100_016_300),
]


def binance_btc_liq_balance(wallet_balance, contract_qty, entry_price):
    for max_position, maint_margin_rate_pct, maint_amount in maint_lookup_table:
        maint_margin_rate = maint_margin_rate_pct / 100
        liq_price = (wallet_balance + maint_amount - contract_qty*entry_price) / (abs(contract_qty) * (maint_margin_rate - (1 if contract_qty>=0 else -1)))
        base_balance = liq_price * abs(contract_qty)
        if base_balance <= max_position:
            break
    return round(liq_price, 2)


def binance_btc_liq_leverage(leverage, contract_qty, entry_price):
    wallet_balance = abs(contract_qty) * entry_price / leverage
    print(f'[Wallet-balance-equivalent of {wallet_balance}]', end='')
    return binance_btc_liq_balance(wallet_balance, contract_qty, entry_price)


def liquidation_price(
        side: int | str | OrderSide,
        entry_price: float,
        quantity: float,
        balance: float,
        leverage: int,
):
    if leverage * entry_price * balance < quantity * entry_price:
        raise ValueError("Insufficient wallet balance (initial margin) to open a position.")

    side = side_to_int(side)

    wallet_balance = abs(quantity) * entry_price / leverage

    liq_price = (wallet_balance - quantity * entry_price) / (abs(quantity) * (-1 if quantity >= 0 else 1))
    return liq_price
    # return abs(quantity) * entry_price / leverage if side == BUY else


if __name__ == '__main__':

    x = pd.DataFrame({"x": [5,10,11]})

    side = SELL
    entry_price = 250
    quantity = 1
    balance = 250
    leverage = 1

    required_balance = entry_price * quantity / leverage

    if balance < required_balance:
        raise BalanceError(
            f"To open position with {leverage}x leverage with {quantity} quantity, the required balance is: "
            f"{required_balance} but your available balance is: {balance}"
        )

    allowed_liquidation_price_change = balance / quantity / leverage

    liq_price = entry_price - allowed_liquidation_price_change if side == BUY else entry_price + allowed_liquidation_price_change

    liq_price
