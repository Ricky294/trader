import copy

from trader.core.indicator import Indicator, Result
from trader.core.model import Candles


class OptimizedResult(Result):

    def __init__(self, result: Result):
        self.counter = 0

        fields_and_methods = dir(result)
        fields = vars(result)

        user_defined_methods = tuple(
            field_or_method
            for field_or_method in fields_and_methods
            if field_or_method not in fields and not field_or_method.startswith("_")
        )

        method_results = {method_name: getattr(result, method_name)() for method_name in user_defined_methods}

        def arr_split(arr):
            def wrapper():
                return arr[:self.counter]
            return wrapper

        for name, result in method_results.items():
            self.__dict__[name] = arr_split(result)


class OptimizedIndicator(Indicator):

    def __init__(self, candles: Candles, indicator: Indicator):
        self.all_result = indicator(candles)
        self.current_result = OptimizedResult(copy.deepcopy(self.all_result))
        self.array_fields = {
            key: val for key, val in self.all_result.__dict__.items()
            if hasattr(val, "__getitem__")
        }

    def __call__(self, candles: Candles):
        candle_size = candles.shape[0]
        for key, val in self.array_fields.items():
            self.current_result.__dict__[key] = val[:candle_size]

        self.current_result.counter = candle_size
        return self.current_result
