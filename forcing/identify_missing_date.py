"""
script for finding missing dates in forcing data
Author: Mateusz Matuszak
"""

import xarray as xr
import pandas as pd

def missing_date(file):
    ds = xr.open_dataset(file)
    file_times = ds.time.values
    date_range = pd.date_range(start=file_times[0], end=file_times[-1], freq='3H')
    
    missing_dates = []
    for time in date_range:
        if time not in file_times:
            missing_dates.append(time)
    
    for time in missing_dates:
        print(time)
        
    return missing_dates

def duplicate_date(file):
    ds = xr.open_dataset(file)
    file_times = list(ds.time.values)

    for time in file_times:
        occ = file_times.count(time)
        if occ > 1:
            print(time)
    

if __name__ == '__main__':
    import sys
    file = sys.argv[1]
    missing_date(file)
    print('******')
    duplicate_date(file)