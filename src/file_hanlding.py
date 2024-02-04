import pandas as pd
import numpy as np

def datadict_to_csv(datadict: dict[str, np.array], file_path: str):
    df = pd.DataFrame.from_dict(datadict)
    df.to_csv(file_path, index=False)

def csv_to_datadict(file_path: str) -> dict[str, np.array]:
    df = pd.read_csv(file_path)

    dict = {}
    for key in df:
        dict[key] = df[key].to_numpy()

    return dict