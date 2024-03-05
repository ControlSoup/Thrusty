from copy import deepcopy

import numpy as np

from .file_hanlding import datadict_to_csv
from .plotting import graph_datadict
from .units import imperial_dictionary, string_to_imperial


class DataStorage:
    def __init__(
        self,
        data_array: np.array,
        name: str = "",
        data_key="time [s]",
    ):

        self.name = name

        self.__data_array = data_array

        # Precompute dx
        self.__dx_array = np.concatenate([np.zeros(1), np.diff(self.__data_array)])
        self.__data_key = data_key

        # Setup data storage
        self.__datadict = {}
        self.__index = 0

    def from_arange(
        start: float, end: float, dx: float, data_key: str = "time [s]", name: str = ""
    ):
        return DataStorage(
            data_array=np.arange(start, end, dx), name=name, data_key=data_key
        )

    def from_linspace(
        start: float, end: float, increments: float, data_key: str, name: str = ""
    ):
        return DataStorage(
            data_array=np.linspace(start, end, increments),
            data_key=data_key,
            name=name,
        )

    def from_geomspace(
        start: float, end: float, increments: float, data_key: int, name=""
    ):
        return DataStorage(
            data_array=np.geomspace(start, end, num=increments, endpoint=True),
            name=name,
            data_key=data_key,
        )

    @property
    def x(self):
        return self.__data_array[self.__index]

    @property
    def max_x(self):
        return self.__data_array[-1]

    @property
    def min_x(self):
        return self.__data_array[0]

    @property
    def dx(self):
        return self.__dx_array[self.__index]

    @property
    def data_array(self):
        return self.__data_array

    @property
    def datadict(self):
        self.__trim_data()

        datadict = deepcopy(self.__datadict)

        datadict[self.__data_key] = self.__data_array

        return datadict

    @property
    def datadict_imperial(self):
        datadict = self.datadict
        return imperial_dictionary(datadict)

    def __trim_data(self):
        for key in self.__datadict:
            self.__datadict[key] = self.__datadict[key][0 : self.__index]
            self.__data_array = self.__data_array[0 : self.__index]

    def next_cycle(self):
        self.__index += 1

        if self.__index > len(self.__data_array) - 1:
            self.__index -= 1
            print(f"WARNING| Max Value of {self.__data_key} has been reached")

    def record(self, key: str, value: float):

        if key not in self.__datadict:
            if self.__index != 0:
                raise ValueError(
                    f"ERROR| Keys may only be intialized at time 0.0 check [{key}]"
                )
            self.__datadict[key] = np.zeros_like(self.__data_array)
            self.__datadict[key][self.__index] = value
        else:
            self.__datadict[key][self.__index] = value

    def record_from_list(self, list: [str, float]):
        for key, val in list:
            self.record(key, val)

    def record_from_dict(self, dict: dict[str, float]):
        for key, val in dict.items():
            self.record(key, val)

    def export_to_csv(self, file_name: str):
        datadict_to_csv(self.datadict, file_name)

    def plot_all(
        self, export_path=None, show_fig=True, title=None, y_axis_tile=None, log_x=False
    ):

        if title is None:
            title = self.name

        graph_datadict(
            datadict=self.datadict,
            title=title,
            x_key=self.__data_key,
            export_path=export_path,
            show_fig=show_fig,
            yaxis_title=y_axis_tile,
            log_x=log_x,
        )

    def plot_imperial(
        self, export_path=None, show_fig=True, title=None, y_axis_tile=None, log_x=False
    ):

        if title is None:
            title = self.name

        graph_datadict(
            datadict=self.datadict_imperial,
            title=title,
            x_key=string_to_imperial(self.__data_key),
            export_path=export_path,
            show_fig=show_fig,
            yaxis_title=y_axis_tile,
            log_x=log_x,
        )

    def reset(self):
        self.__init__(self.data_array, self.name, self.__data_key)

    def print(self):
        datadict = self.datadict

        for key in datadict:
            print(f"|{key}| = {datadict[key][self.__index - 1]}")
