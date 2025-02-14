

#script for preparing static variables for anemoi datasets

# Author: Mateusz Matuszak

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas
import datetime as datetime

def static_h(ds, time_start=datetime.datetime(2024,1,1,0), time_end=datetime.datetime(2025,1,1,0)):
    # TODO kan dette generaliseres mer?
    time_start_string = time_start.strftime("%Y-%m-%d %H:%M:%S")
    x = np.array(ds.X.values)
    y = np.array(ds.Y.values)
    
    hours_since = [0]
    k=0
    while time_start < time_end:
        time_start += datetime.timedelta(hours=1)
        k+=1
        hours_since.append(k)
    hours_since = np.array(hours_since)

    h = ds.h

    h_array = np.zeros([len(hours_since), np.shape(ds.h)[0], np.shape(ds.h)[1]])
    
    h_array[:,:,:] = h.values
    
    h_ds = xr.Dataset(
        coords = dict(
            X=(['X'], x, {'units':'meter','standard_name':'projection_x_coordinate'}),
            Y=(['Y'], y, {'units':'meters', 'standard_name':'projection_y_coordinate'}),
            time=(['time'], hours_since*60*60, {'long_name':'time since initialization', 'units':f'seconds since {time_start_string}', 'standard_name':'time', 'calendar':'gregorian'})
            ),
        data_vars = dict(
            lon=(['Y', 'X'], np.array(ds.lon.values), {'grid_mapping': 'projection_stere','units':'degree_east', 'standard_name':'longitude','long_name':'longitude'}),
            lat=(['Y', 'X'], np.array(ds.lat.values), {'grid_mapping': 'projection_stere','units':'degree_north', 'standard_name':'latitude', 'long_name': 'latitude'}),
            h=(['time', 'Y', 'X'], h_array, {'standard_name':'sea_floor_depth_below_sea_level', 'long_name':'sea_floor_depth_below_sea_level', 'grid_mapping':'projection_stere', 'units':'meter'})
        )
    )
    h_ds['projection_stere'] = ds.projection_stere
    h_ds.to_netcdf('h.nc', encoding={'time': {'dtype':'double'}, 'h':{'zlib': True, 'complevel': 4}})

def extract_variable_without_time(ds, var, outfile='h_no_time.nc'):
    ds = ds[var]
    ds.to_netcdf(outfile)

if __name__ == '__main__':
    file = '/lustre/storeB/project/fou/hi/oper/norkyst_v3/forecast/his_zdepths/2024/01/01/norkyst800_his_zdepth_20240101T00Z_m00_AN.nc'
    ds = xr.open_dataset(file)
    extract_variable_without_time(ds, 'h')
