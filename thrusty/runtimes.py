import numpy as np
import pandas as pd
from copy import deepcopy
from .file_hanlding import datadict_to_csv
from .plotting import graph_by_key, graph_datadict

class DataStorage():
    def __init__(self, dt_s, max_time_s):

        # Setup how time will be tracked
        self.__max_time_s = max_time_s
        self.__dt_s = dt_s
        self.__time_array_s = np.arange(0, self.__max_time_s, self.__dt_s)
        self.__time_key = 'time [s]'

        # Setup data storage
        self.__datadict = {}
        self.__index = 0

    @property
    def max_time_s(self):
        return self.__max_time_s

    @property
    def dt_s(self):
        return self.__dt_s

    @property
    def time_array_s(self):
        return self.__time_array_s

    @property
    def datadict(self):
        self.__trim_data()

        datadict = deepcopy(self.__datadict)

        datadict[self.__time_key] = self.__time_array_s

        return datadict

    def __trim_data(self):
        for key in self.__datadict:
            self.__datadict[key] = self.__datadict[key][0:self.__index + 1]
            self.__time_array_s = self.__time_array_s[0:self.__index + 1]

    def next_cycle(self):
        self.__index += 1

        if self.__index > len(self.__time_array_s) - 1:
            self.__index -= 1
            print("WARNING| Max Value of time has been reached")

    def record_data(self, key: str, value: float):

        if key not in self.__datadict:
            if self.__index != 0:
                raise ValueError(
                    f"ERROR| Keys may only be intialized at time 0.0 check [{key}]"
                )
            self.__datadict[key] = np.zeros_like(self.__time_array_s)
            self.__datadict[key][self.__index] = value
        else:
            self.__datadict[key][self.__index] = value

    def record_list(self, list: [str, float]):
        for key, val in list:
            self.record_data(key, val)

    def export_to_csv(self, file_path: str):
        datadict_to_csv(self.datadict, file_path)

    def plot_all(self, export_path = None, show_fig=True):
        graph_datadict(
            self.datadict,
            self.__time_key,
            export_path,
            show_fig=show_fig
        )


