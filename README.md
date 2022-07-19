# Trader

## Table of Contents
1. [Quick overview](#quick-overview)
2. [Terminology](#terminology)
3. [Implementation details](#implementation-details)
4. [Examples](#examples)

## Quick overview

---

*Trader is a framework which helps you create and run 
trading strategies in backtest or live environment.*

### Supported trading environments (Futures market only)
- Binance
- Backtest


## Terminology

---

- **Broker:** A platform which facilitates buying and selling of a security.
- **Symbol:** A stock symbol is a unique series of letters 
assigned to a security.
- **Interval:** Refers to candle interval. Defines the sampling interval.
- **Market:** A trading market is where you buy and sell securities.
  - *Spot:* The ownership transfers instantly after a buy or sell transaction.
  - *Futures:* Participants buy and sell contracts for delivery on a future date.
- **Asset:** 
- **Balance:** Refers to an individual account balance.
- **Position:** Refers to a Futures (market) position.
- **Long position:** The investor has bought and owns shares of the asset.
- **Short position:** The investor owes the asset to another person but has not bought them yet.
- **Order side:** Determines buy or sell when creating order or position.
- **Order type:** Determines the type of the order.
  - *Limit:* Filled when the price hits the entry price.
  - *Market:* Filled instantly at the current market price without going in the order book.
  - *Stop loss:* Used to mitigate risks. Useful when the market goes against your trade/position.
    - *Limit:* 
    - *Market:* If price hits the defined price the position gets instantly reduced or closed.
  - *Take profit:* Used to protect profits.
    - *Limit:*
    - *Market:*
  - *Trailing stop market:* 
- **Time in force:** Indicates how long an order will remain active before it executes or expires.
  - *GTC* = Good till canceled - Order remains in order book until filled or canceled.
  - *IOC* = Immediate or canceled - Attempts to immediately fill order partially or fully at stated price (or better).
Cancels any unfilled portion.
  - *FOK* = Fill or kill - Attempts to immediately fill order completely at stated price (or better). 
Must be filled completely or not at all!
- **Trader:** 
- **Strategy:** A trading strategy is a systematic methodology 
used for buying and selling in the securities markets. 
A trading strategy is based on predefined rules and criteria 
used when making trading decisions.
- **Indicator:** Technical indicators are used to produce buy and sell signals.
- **Backtesting:** Allows a trader to simulate a strategy on historical data to generate, analyze and visualize results.
- **Live trading:** Refers to real time trading with real amount on a real market.
- **Maker order:** Goes into the order book. Gets executed at a specified price (e.g. Limit order).
- **Taker order:** Executes instantly by taking liquidity out from the order book (e.g. Market order).
- **Liquidation:** Position liquidation is a forced action and happens automatically 
when position loss is greater than the available account balance

## Implementation details

---

### Backtesting framework

**Limitations** 
  * Unable to emulate instantaneous taker (market) orders, 
because only candle open, high, low and close price is known. 
  * Taker orders are always filled on next candle open price.
  * Unable to tell if candle price hit its low or its high first. So the implementation logic is the following:
    * If open price distance from high price is less than its distance from low price 
  than high price was hit first instead of low.
    * If open price distance from high price is greater than its distance from low price 
  than low price was hit first instead of high.
    
### Strategy

Helps the user to create his own strategy.
Write the trading strategy logic here, 
such as when to enter and exit a position, 
when and what orders to create, and so on.

### FuturesTrader

Interface which helps to get account information, get, create or close orders/positions and more.

### Exceptions

The framework uses custom exceptions in order to
unify errors between different brokers and environments.

- TraderError - Base exception for all below.
- BrokerError - Incorrect or unsupported broker.
- SymbolError - Incorrect or unsupported trade symbol.
- MarketError - Incorrect or unsupported market type (Valid values: **FUTURES**, **SPOT**).
- IntervalError - Incorrect or unsupported trade interval.
- SideError - Incorrect order side. (Valid values: **BUY**, **SELL**, **LONG**, **SHORT**)
- OrderTypeError - Incorrect or unsupported order type 
(Valid values: **LIMIT**, **MARKET**, **STOP**, **STOP_MARKET**, **TAKE_PROFIT**, **TAKE_PROFIT_MARKET**, **TRAILING_STOP_MARKET**)
- PositionError - Used when
- BalanceError - 

## Examples

---

*There are 2 options to define a custom strategy either
by writing a python script or by using the UI app.*

### Python script

```python
from trader.data.binance import get_store_candles
from trader.data.database import HDF5CandleStorage

from trader.backtest import BacktestFuturesBroker
from trader.core.model import Balance
from trader.core.enumerate import MA
from trader.core.indicator import DoubleMAIndicator
from trader.core.strategy import IndicatorStrategy

from trader.ui.enumerate import Candlestick

start_cash = 1000
asset = "USDT"
symbol = "BTC"

candles = get_store_candles(
  symbol=symbol,
  interval="1h",
  market="FUTURES",
  storage_type=HDF5CandleStorage,
)

dma = DoubleMAIndicator(fast_period=30, slow_period=50, fast_type=MA.EMA, slow_type=MA.EMA)

strategy = IndicatorStrategy(
  trader=BacktestFuturesBroker(
    balance=Balance(asset=asset, free=start_cash),
    maker_fee_rate=0.0002,
    taker_fee_rate=0.0004,
  ),
  candles=candles,
  leverage=1,
  trade_ratio=0.5,
  asset=asset,
  indicators=[dma],
  entry_long_conditions=[dma.bullish_cross],
  entry_short_conditions=[dma.bearish_cross],
  exit_long_conditions=[dma.bearish_cross],
  exit_short_conditions=[dma.bullish_cross],
)

strategy.run()
strategy.plot(
  candlestick_type=Candlestick.LINE,
  custom_graphs=[dma],
)

```
