from copy import deepcopy

import numpy as np

from .file_hanlding import datadict_to_csv
from .plotting import graph_datadict
from .units import imperial_dictionary, string_to_imperial


class DataStorage:
    def __init__(
        self,
        dt_s,
        max_time_s,
        name: str = "",
        alternate_time_array=None,
        time_key="time [s]",
    ):

        self.name = name

        # Setup how time will be tracked
        self.__max_time_s = max_time_s
        self.__dt_s = dt_s

        if alternate_time_array is None:
            self.__time_array_s = np.arange(0, self.__max_time_s, self.__dt_s)
        else:
            self.__time_array_s = alternate_time_array

        self.__time_key = time_key

        # Setup data storage
        self.__datadict = {}
        self.__index = 0
    
    def from_arange(
        start: float, 
        end: float, 
        increments: float, 
        time_key: str, 
        name=""
    ):
        return DataStorage(
            1, end, name, np.arange(start, end, increments),time_key=time_key
        )


    def from_linspace(
        start: float, 
        end: float, 
        increments: float, 
        time_key: str, 
        name=""
    ):
        return DataStorage(
            1, end, name, np.linspace(start, end, increments), time_key=time_key
        )

    def from_geomspace(
        start: float, 
        end: float, 
        increments: float, 
        time_key: str, 
        name=""
    ):
        return DataStorage(
            1,
            end,
            name,
            np.geomspace(start, end, num=increments, endpoint=True),
            time_key=time_key,
        )

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
    
    @property
    def datadict_imperial(self):
        datadict = self.datadict
        return imperial_dictionary(datadict)

    def __trim_data(self):
        for key in self.__datadict:
            self.__datadict[key] = self.__datadict[key][0 : self.__index]
            self.__time_array_s = self.__time_array_s[0 : self.__index]

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

    def record_from_list(self, list: [str, float]):
        for key, val in list:
            self.record_data(key, val)

    def record_from_dict(self, dict: dict[str, float]):
        for key, val in dict.items():
            self.record_data(key, val)

    def export_to_csv(self, file_name: str):
        datadict_to_csv(self.datadict, file_name)

    def plot_all(
        self, 
        export_path=None, 
        show_fig=True, 
        title=None, 
        y_axis_tile=None, 
        log_x=False
    ):

        if title is None:
            title = self.name

        graph_datadict(
            datadict=self.datadict,
            title=title,
            x_key=self.__time_key,
            export_path=export_path,
            show_fig=show_fig,
            yaxis_title=y_axis_tile,
            log_x=log_x,
        )

    def plot_imperial(
        self, 
        export_path=None, 
        show_fig=True, 
        title=None, 
        y_axis_tile=None, 
        log_x=False
    ):

        if title is None:
            title = self.name

        graph_datadict(
            datadict=self.datadict_imperial,
            title=title,
            x_key=string_to_imperial(self.__time_key),
            export_path=export_path,
            show_fig=show_fig,
            yaxis_title=y_axis_tile,
            log_x=log_x,
        )

    def reset(self, confirm=False):
        if confirm:
            self.__init__(self.dt_s, self.max_time_s, self.name)
        else:
            print("WARNING| Please confirm you want to reset data (confirm=True)")

    def print(self):
        datadict = self.datadict

        for key in datadict:
            print(f"|{key}| = {datadict[key][self.__index - 1]}")
