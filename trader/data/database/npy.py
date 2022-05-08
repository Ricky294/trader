from __future__ import annotations

import numpy as np
import nputils as npu

from trader.data.util import check_ndim_is_2
from trader.data.database import CandleStorage
from trader.data.enum import Market


class NPYCandleStorage(CandleStorage):
    
    @staticmethod
    def file_extension():
        return "npy"

    def __init__(self, dir_path: str, symbol: str, interval: str, market: str | Market):
        super(NPYCandleStorage, self).__init__(dir_path=dir_path, symbol=symbol, interval=interval, market=market)

    def append(self, data: any):
        """
        Creates and writes `data` to the file if not exists.

        If exists, it concatenates the `data` with the stored data and overwrites the file.

        :param data: Data to append
        :return: None
        :raises ValueError: If data shape length is not 2 or if the data's last dimension length does not match the dataset's.
        """

        data = npu.to_array(data)
        check_ndim_is_2(data)

        try:
            stored_data = self.get()
            data_to_save = np.concatenate((stored_data, data))
        except FileNotFoundError:
            data_to_save = data
        np.save(self.path, data_to_save)

    def get(self):
        data = np.load(self.path)
        return data
