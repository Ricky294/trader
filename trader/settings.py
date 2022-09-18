import json
import logging

from trader import SETTINGS_PATH
from trader.core.const import Market, Notifications

from util.file_util import read_config
from util.inspect_util import is_public
from util.iter_util import get_class_attrs
from util.meta import StaticMeta


class Settings(metaclass=StaticMeta):
    """
    Contains application global settings.

    Changing these settings will affect how the application behaves.
    """

    backtest_log_level = logging.WARNING

    live_log_level = logging.INFO
    live_file_log_path: str = ''
    candle_stream_log: bool = True

    event_logging = False

    notifications: Notifications = Notifications.ALL

    error_localization: bool = True

    leverage_max: int = 10

    precision_money: int = 3
    precision_price: int = 3
    precision_profit: int = 4
    precision_fee: int = 6
    precision_quantity: int = 4
    precision_balance: int = 4

    market = Market.FUTURES

    trailing_rate_max_percentage: float = 5.0
    trailing_rate_step_size: float = 0.1

    @staticmethod
    def save() -> None:
        """Saves all current settings."""
        settings = {
            attr_name: attr
            for attr_name, attr
            in get_class_attrs(Settings).items()
            if is_public(attr_name) and not callable(attr)
        }

        settings['market'] = str(settings['market'])

        json_str = json.dumps(settings)
        with open(SETTINGS_PATH, 'w') as f:
            f.write(json_str)

    @staticmethod
    def set_saved() -> None:
        """
        Sets saved settings.

        :raises FileNotFoundError: If settings has not been saved or settings file does not exist.
        """
        try:
            settings = read_config(SETTINGS_PATH)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                'Save global settings before trying to set a saved version. \n'
                f'Hint: Call {Settings.__qualname__}.{Settings.save.__name__}() '
                f'before {Settings.__qualname__}.{Settings.set_saved.__name__}()'
            ) from e

        for attr_name, attr in settings.items():
            setattr(Settings, attr_name, attr)

        Settings.market = Market.from_value(Settings.market)

    @staticmethod
    def set_default() -> None:
        """Sets default settings."""
        Settings.backtest_log_level = logging.WARNING

        Settings.live_log_level = logging.INFO
        Settings.live_file_log_path = ''
        Settings.candle_stream_log = False

        Settings.notifications = True

        Settings.error_localization = True

        Settings.leverage_max = 10

        Settings.precision_money = 3
        Settings.precision_price = 3
        Settings.precision_profit = 4
        Settings.precision_fee = 6
        Settings.precision_quantity = 4
        Settings.precision_balance = 4

        Settings.market = Market.FUTURES
