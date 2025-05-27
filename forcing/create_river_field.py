"""
script for obtaining river data on NK800 grid
Author: Mateusz Matuszak
"""

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import datetime as datetime

def river_values():
    """
    Creates a netCDF file with river variables stored on the NK800 grid.
    """
    river = xr.open_dataset('/lustre/storeB/project/fou/hi/foccus/datasets/norkyst-v3-hindcast/forcing/misc/river.nc').isel(s_rho=0, river_time=slice(0,2))
    nk800 = xr.open_dataset('/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2023/norkyst800-20230726.nc').isel(time=0)[['lon','lat']]
    reference_date = np.datetime64('1970-01-01T00:00:00', 's')

    times = np.zeros_like(river.river_time.values, dtype='int')
    temp = np.zeros([len(times), len(nk800.Y), len(nk800.X)])
    salt = np.zeros([len(times), len(nk800.Y), len(nk800.X)])
    transport = np.zeros([len(times), len(nk800.Y), len(nk800.X)])
    direction = np.zeros([len(times), len(nk800.Y), len(nk800.X)])
    Vshape = np.zeros([len(times), len(nk800.Y), len(nk800.X)])

    for time in range(len(times)):
        difference_in_seconds = (river.isel(river_time=time).river_time.values - reference_date).astype('timedelta64[s]')
        difference_in_hours = difference_in_seconds / np.timedelta64(1, 'h')
        times[time] = difference_in_hours
        for i in range(0,10): #1815):
            pos = [int(river.isel(river=i).river_Xposition.values), int(river.isel(river=i).river_Eposition.values)]
            temp[time, pos[1], pos[0]] = river.isel(river=i, river_time=time).river_temp.values
            salt[time, pos[1], pos[0]] = river.isel(river=i, river_time=time).river_salt.values
            transport[time, pos[1], pos[0]] = river.isel(river=i, river_time=time).river_transport.values
            direction[time, pos[1], pos[0]] = river.isel(river=i, river_time=time).river_direction.values
            Vshape[time, pos[1], pos[0]] = river.isel(river=i, river_time=time).river_Vshape.values

    river_ds = xr.Dataset(
        coords = dict(
            X=(['X'], np.array(nk800.X.values), {'units':'meter','standard_name':'projection_x_coordinate'}),
            Y=(['Y'], np.array(nk800.Y.values), {'units':'meters', 'standard_name':'projection_y_coordinate'}),
            time=(['time'], times, {'long_name':'time since initialization', 'units':f'seconds since 1970-01-01 00:00:00', 'standard_name':'time', 'calendar':'gregorian'}),
        ),
        data_vars = dict(
            lon=(['Y', 'X'], np.array(nk800.lon.values), {'grid_mapping': 'projection_stere','units':'degree_east', 'standard_name':'longitude','long_name':'longitude'}),
            lat=(['Y', 'X'], np.array(nk800.lat.values), {'grid_mapping': 'projection_stere','units':'degree_north', 'standard_name':'latitude', 'long_name': 'latitude'}),
            river_temp=(['time', 'Y', 'X'], temp, {'grid_mapping': 'projection_stere', 'units': 'Celsius', 'long_name': 'river runoff potential temperature'}),
            river_salt=(['time', 'Y', 'X'], salt, {'grid_mapping': 'projection_stere', 'units': 'PSU', 'long_name': 'river runoff salinity'}),
            river_transport=(['time', 'Y', 'X'], transport, {'grid_mapping': 'projection_stere', 'units': 'meter3 second-1', 'long_name': 'river runoff vertically integrated mass transport'}),
            river_direction=(['time', 'Y', 'X'], direction, {'grid_mapping': 'projection_stere', 'units': 'nondimensional', 'long_name': 'river runoff direction'}),
            river_Vshape=(['time', 'Y', 'X'], Vshape, {'grid_mapping': 'projection_stere', 'units': 'nondimensional', 'long_name': 'river runoff mass transport vertical profile'}))
        )

    river_ds.to_netcdf('river.nc', encoding={'time': {'dtype':'double'}})

def river_binary_mask():
    """
    Creates a netCDF file with river positions stored as a binary mask on the NK800 grid. 
    """
    river = xr.open_dataset('/lustre/storeB/project/fou/hi/foccus/datasets/norkyst-v3-hindcast/forcing/misc/river.nc').isel(s_rho=0, river_time=0)
    nk800 = xr.open_dataset('/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2023/norkyst800-20230726.nc').isel(time=0)[['lon','lat', 'projection_stere']]
    river_pos = np.zeros([len(nk800.Y), len(nk800.X)])
    for r in range(len(river.river.values)):
        pos = [int(river.isel(river=r).river_Xposition.values), int(river.isel(river=r).river_Eposition.values)]
        river_pos[pos[1], pos[0]] = 1

    river_ds = xr.Dataset(
        coords = dict(
            X=(['X'], np.array(nk800.X.values), {'units':'meter','standard_name':'projection_x_coordinate'}),
            Y=(['Y'], np.array(nk800.Y.values), {'units':'meters', 'standard_name':'projection_y_coordinate'}),
        ),
        data_vars = dict(
            lon=(['Y', 'X'], np.array(nk800.lon.values), {'grid_mapping': 'projection_stere','units':'degree_east', 'standard_name':'longitude','long_name':'longitude'}),
            lat=(['Y', 'X'], np.array(nk800.lat.values), {'grid_mapping': 'projection_stere','units':'degree_north', 'standard_name':'latitude', 'long_name': 'latitude'}),
            river_binary_mask=(['Y', 'X'], river_pos, {'grid_mapping': 'projection_stere', 'standard_name': 'river_binary_mask', 'long_name': 'river_binary_mask'}))
        )
    river_ds['projection_stere'] = nk800.projection_stere
    river_ds.to_netcdf('river_positions.nc')
river_binary_mask()




