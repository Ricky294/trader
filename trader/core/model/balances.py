import pandas as pd

from trader.core.model import Balance
from trader.data.model import Models


class Balances(Models[Balance]):

    def to_dataframe(self, *drop_columns: str, drop_na=True) -> pd.DataFrame:
        df = super().to_dataframe(*drop_columns, drop_na=drop_na)
        df['profit'] = df['total'].diff()
        return df
