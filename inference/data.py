from glob import glob

import numpy as np
from anemoi.datasets import open_dataset
import xarray as xr
import dask.array as da
import pandas as pd

from map_keys import map_keys

def read_norkyst(fields, filename, times, lead_time, freq='1h'):
    """Read norkyst data, given filename and fields subset to 
    read. Return anemoi-datasets object."""
    select = []
    for field in fields:
        select.extend(map_keys[field]['norkyst'])
    start = times[0]
    end = times[-1]+pd.Timedelta(hours=int(freq[:-1]) * lead_time)
    ds = open_dataset(filename, frequency=freq, start=start, end=end, select=select)
    return ds

def get_norkyst_data(ds, time_idx, fields, lead_time):
    """Fetch data from dataset."""
    slc = slice(time_idx, time_idx + lead_time)
    norkyst = {}
    for field in fields:
        norkyst[field] = np.array(map_keys[field]['transform'](ds, slc, field))
    return norkyst

def get_data(path, time, ens_size=None):
    """
    Args:
        path: str
            Path to directory with nc file.
            Expects subdirs if ens_size is not None

    Outputs:
        data_dict: dict
            Dict in the form of
            data_dict[field][member,lead_time,coords]
    """
    time = time.strftime('%Y-%m-%dT%H')
    if ens_size is None:
        filename = glob(path + f"*{time}.nc")[0]
        ds = xr.open_dataset(filename)
        ds = ds.expand_dims('members').assign_coords(members=1)
    else:
        # load datasets
        datasets = []
        for i in range(ens_size):
            try:
                filename = glob(path + f"{i}/*{time}.nc")[0]
            except IndexError:
                print(f"No inference file found for time stamp {time}, member {i}")
                exit(1)
            ds = xr.open_dataset(filename, chunks={'lead_times': 'auto', 'points': 'auto'})
            datasets.append(ds)

        datasets_with_members = [ds.expand_dims('members').assign_coords(members=[i]) for i, ds in enumerate(datasets)]
        # concatinate datasets
        ds = xr.concat(datasets_with_members, dim='members')

    return ds
