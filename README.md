## Trader

### Table of Contents
1. [Terminology](#terminology)
2. [Quick overview](#quick-overview)
3. [Implementation details](#implementation-details)
4. [Examples](#examples)

### Terminology

---

- **Broker:**
- **Symbol:** A stock symbol is a unique series of letters 
assigned to a security.
- **Interval:** Refers to candle interval.
- **Market:** Trading market. Spot or Futures
- **Asset:** 
- **Balance:** 
- **Position:** 
- **Order side:** Determines buy or sell when creating order or position.
- **Order type:** Determines the type of the order.
  - *Market:* 
  - *Limit:* 
  - *Stop limit:* 
  - *Stop market:* 
  - *Take profit limit:* 
  - *Take profit market:* 
  - *Trailing stop market:* 
- **Time in force:** Used 
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
- **Backtesting:** 
- **Live trading:**


### Quick overview

---

*Trader is a framework which helps you to implement, 
live trade or backtest trading strategies.*

#### Supported environments
- Binance
- Backtest

### Implementation details

---

#### Strategy

#### FuturesTrader

#### Exceptions

The framework uses custom exceptions in order to
unify errors between environments.

- TraderException - Base exception for all below.
- BrokerError - Invalid broker.
- SymbolError - Invalid trade symbol.
- IntervalError - Invalid trade interval.
- SideError - Invalid order side.
- OrderTypeError - Invalid order type.
- PositionError -
- BalanceError -

### Examples

---

