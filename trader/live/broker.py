from abc import ABC

from functools import partial

from trader.core.const import BrokerEvent
from trader.core.interface import FuturesBroker

from util.notification import show_notification
from util.observer import Observer


class NotificationObserver(Observer):

    def update(self, event: BrokerEvent, *args, **kwargs):
        # Title: Position close     Message: New balance: 220 USD (+15.145)
        # Title: Position open      Message: New BTCUSDT position with 1x leverage 50 USDT.
        # Title: Leverage change    Message: Leverage = 7

        title = event.text()
        notif_func = partial(show_notification, title=title)

        match event:
            case BrokerEvent.ON_POSITION_OPEN:
                notif_func()
            case BrokerEvent.ON_POSITION_CLOSE:
                notif_func()
            case BrokerEvent.ON_LEVERAGE_CHANGE:
                notif_func()


class LiveFuturesBroker(FuturesBroker, ABC):
    ...
