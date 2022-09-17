

class Strategy:

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj.args = args
        obj.kwargs = kwargs
        return obj

    def __init__(self, *args, **kwargs):
        print(self._candles)
        print(self._broker)


class Engine:

    def __init__(self, candles, broker, strategy):
        self.candles = candles
        self.broker = broker
        self.strategy = strategy


strategy = Strategy('xy', hihi=15)

engine = Engine('candles', 'broker', strategy)
