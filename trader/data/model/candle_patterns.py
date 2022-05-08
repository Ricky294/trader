import numpy as np
import talib


class TALibCandlePatterns:

    __slots__ = ("_ohlc",)

    def __init__(self, open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray):
        self._ohlc = open, high, low, close

    def two_crows(self) -> np.ndarray:
        return talib.CDL2CROWS(*self._ohlc)

    def three_line_strike(self) -> np.ndarray:
        return talib.CDL3LINESTRIKE(*self._ohlc)

    def three_black_crows(self) -> np.ndarray:
        return talib.CDL3BLACKCROWS(*self._ohlc)

    def three_inside(self) -> np.ndarray:
        return talib.CDL3INSIDE(*self._ohlc)

    def three_outside_up_down(self) -> np.ndarray:
        return talib.CDL3OUTSIDE(*self._ohlc)

    def three_stars_in_south(self) -> np.ndarray:
        return talib.CDL3STARSINSOUTH(*self._ohlc)

    def three_white_soldiers(self) -> np.ndarray:
        return talib.CDL3WHITESOLDIERS(*self._ohlc)

    def abandoned_baby(self, penetration=0.3) -> np.ndarray:
        return talib.CDLABANDONEDBABY(*self._ohlc, penetration=penetration)

    def advance_block(self) -> np.ndarray:
        return talib.CDLADVANCEBLOCK(*self._ohlc)

    def breakaway(self) -> np.ndarray:
        return talib.CDLBREAKAWAY(*self._ohlc)

    def closing_marubozu(self) -> np.ndarray:
        return talib.CDLCLOSINGMARUBOZU(*self._ohlc)

    def belt_hold(self) -> np.ndarray:
        return talib.CDLBELTHOLD(*self._ohlc)

    def conceal_baby_swallow(self) -> np.ndarray:
        return talib.CDLCONCEALBABYSWALL(*self._ohlc)

    def counter_attack(self) -> np.ndarray:
        return talib.CDLCOUNTERATTACK(*self._ohlc)

    def dark_cloud_cover(self, penetration=0.5) -> np.ndarray:
        return talib.CDLDARKCLOUDCOVER(*self._ohlc, penetration=penetration)

    def doji(self) -> np.ndarray:
        return talib.CDLDOJI(*self._ohlc)

    def doji_star(self) -> np.ndarray:
        return talib.CDLDOJISTAR(*self._ohlc)

    def dragonfly_doji(self) -> np.ndarray:
        return talib.CDLDRAGONFLYDOJI(*self._ohlc)

    def engulfing(self) -> np.ndarray:
        return talib.CDLENGULFING(*self._ohlc)

    def evening_doji_star(self, penetration=0.3) -> np.ndarray:
        return talib.CDLEVENINGDOJISTAR(*self._ohlc, penetration=penetration)

    def evening_star(self, penetration=0.3) -> np.ndarray:
        return talib.CDLEVENINGSTAR(*self._ohlc, penetration=penetration)

    def gap_side_side_white(self) -> np.ndarray:
        return talib.CDLGAPSIDESIDEWHITE(*self._ohlc)

    def gravestone_doji(self) -> np.ndarray:
        return talib.CDLGRAVESTONEDOJI(*self._ohlc)

    def hammer(self) -> np.ndarray:
        return talib.CDLHAMMER(*self._ohlc)

    def hanging_man(self) -> np.ndarray:
        return talib.CDLHANGINGMAN(*self._ohlc)

    def harami(self) -> np.ndarray:
        return talib.CDLHARAMI(*self._ohlc)

    def harami_cross(self) -> np.ndarray:
        return talib.CDLHARAMICROSS(*self._ohlc)

    def high_wave(self) -> np.ndarray:
        return talib.CDLHIGHWAVE(*self._ohlc)

    def hikkake(self) -> np.ndarray:
        return talib.CDLHIKKAKE(*self._ohlc)

    def hikakke_modified(self) -> np.ndarray:
        return talib.CDLHIKKAKEMOD(*self._ohlc)

    def homing_pigeon(self) -> np.ndarray:
        return talib.CDLHOMINGPIGEON(*self._ohlc)

    def identical_three_crows(self) -> np.ndarray:
        return talib.CDLIDENTICAL3CROWS(*self._ohlc)

    def in_neck(self) -> np.ndarray:
        return talib.CDLINNECK(*self._ohlc)

    def inverted_hammer(self) -> np.ndarray:
        return talib.CDLINVERTEDHAMMER(*self._ohlc)

    def kicking(self) -> np.ndarray:
        return talib.CDLKICKING(*self._ohlc)

    def kicking_by_length(self) -> np.ndarray:
        return talib.CDLKICKINGBYLENGTH(*self._ohlc)

    def ladder_bottom(self) -> np.ndarray:
        return talib.CDLLADDERBOTTOM(*self._ohlc)

    def long_legged_doji(self) -> np.ndarray:
        return talib.CDLLONGLEGGEDDOJI(*self._ohlc)

    def long_line(self) -> np.ndarray:
        return talib.CDLLONGLINE(*self._ohlc)

    def marubozu(self) -> np.ndarray:
        return talib.CDLMARUBOZU(*self._ohlc)

    def matching_low(self) -> np.ndarray:
        return talib.CDLMATCHINGLOW(*self._ohlc)

    def mat_hold(self, penetration=0.5) -> np.ndarray:
        return talib.CDLMATHOLD(*self._ohlc, penetration=penetration)

    def morning_doji_star(self, penetration=0.3) -> np.ndarray:
        return talib.CDLMORNINGDOJISTAR(*self._ohlc, penetration=penetration)

    def morning_star(self, penetration=0.3) -> np.ndarray:
        return talib.CDLMORNINGSTAR(*self._ohlc, penetration=penetration)

    def on_neck(self) -> np.ndarray:
        return talib.CDLONNECK(*self._ohlc)

    def piercing(self) -> np.ndarray:
        return talib.CDLPIERCING(*self._ohlc)

    def rickshaw_man(self) -> np.ndarray:
        return talib.CDLRICKSHAWMAN(*self._ohlc)

    def rising_falling_three_methods(self) -> np.ndarray:
        return talib.CDLRISEFALL3METHODS(*self._ohlc)

    def separating_lines(self) -> np.ndarray:
        return talib.CDLSEPARATINGLINES(*self._ohlc)

    def shooting_star(self) -> np.ndarray:
        return talib.CDLSHOOTINGSTAR(*self._ohlc)

    def short_line(self) -> np.ndarray:
        return talib.CDLSHORTLINE(*self._ohlc)

    def spinning_top(self) -> np.ndarray:
        return talib.CDLSPINNINGTOP(*self._ohlc)

    def stalled_pattern(self) -> np.ndarray:
        return talib.CDLSTALLEDPATTERN(*self._ohlc)

    def stick_sandwich(self) -> np.ndarray:
        return talib.CDLSTICKSANDWICH(*self._ohlc)

    def takuri(self) -> np.ndarray:
        return talib.CDLTAKURI(*self._ohlc)

    def tasuki_gap(self) -> np.ndarray:
        return talib.CDLTASUKIGAP(*self._ohlc)

    def thrusting(self) -> np.ndarray:
        return talib.CDLTHRUSTING(*self._ohlc)

    def tristar(self) -> np.ndarray:
        return talib.CDLTRISTAR(*self._ohlc)

    def unique_three_river(self) -> np.ndarray:
        return talib.CDLUNIQUE3RIVER(*self._ohlc)

    def upside_gap_two_crows(self) -> np.ndarray:
        return talib.CDLUPSIDEGAP2CROWS(*self._ohlc)

    def upside_downside_gap_three_methods(self) -> np.ndarray:
        return talib.CDLXSIDEGAP3METHODS(*self._ohlc)
