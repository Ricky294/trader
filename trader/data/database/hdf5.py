from __future__ import annotations

import h5py as h5
import numpy as np
import nputils as npu

from trader.data.util import check_ndim_is_2
from trader.data.database import CandleStorage


class HDF5CandleStorage(CandleStorage):

    dataset_name = 'candles'

    @staticmethod
    def file_extension():
        return 'h5'

    def __init__(
            self,
            dir_path: str,
            symbol: str,
            interval: str,
            market: str,
    ):
        super().__init__(dir_path, symbol, interval, market)

    def append(self, data: any):
        """
        Creates a h5 file if not exists and appends the `data` to the dataset.

        :param data: Data to store
        :return: None
        :raises ValueError: If data shape length is not 2 or if the data's last dimension length does not match the dataset's.
        """

        data = npu.to_array(data)
        check_ndim_is_2(data)

        with h5.File(self.path, 'a') as hf:
            try:
                dataset = hf[self.dataset_name]
                if dataset.shape[-1] != data.shape[-1]:
                    raise ValueError(
                        f'HDF5 dataset and the data to append must have the same shape on the 2nd dimension '
                        f'(dataset: {dataset.shape[-1]}, data: {data.shape[-1]}).'
                    )

                hf[self.dataset_name].resize((hf[self.dataset_name].shape[0] + data.shape[0]), axis=0)
                hf[self.dataset_name][-data.shape[0]:] = data
            except KeyError:
                hf.create_dataset(self.dataset_name, data=data, maxshape=(None, data.shape[-1]))

    def get(self):
        """
        Gets the data from `dataset_name` as a numpy array.

        :return: numpy array
        :raises FileNotFoundError: If file not exists.
        """
        with h5.File(self.path, 'r') as hf:
            dataset = hf.get(self.dataset_name)
            if dataset is None:
                raise KeyError(f'Dataset with name: {self.dataset_name} is not found!')

            data: np.ndarray = dataset[:]
            return data
