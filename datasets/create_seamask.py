# Script to preprocess data before using anemoi-datasets

# Authors: Ina Kullmann & Mateusz Matuszak


## 1) Find seafloor mask for all layers
## landmask as well

## 2) iterate through masks and layers, remove nan (only surface)

## 3) find all remaining nans, which should be in ocean

## 4) set nearest neighbour (or a similar approach) for these nan values


# Author: Mateusz Matuszak

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas
import datetime as datetime

#file = '/lustre/storeB/project/fou/hi/foccus/datasets/symlink_folder/symlinks_norkystv3/norkyst800_his_zdepth_20240102T00Z_m00_AN.nc'
#ds = xr.open_dataset(file)

def define_mask(ds, time_start = datetime.datetime(2024,1,1,0), time_end = datetime.datetime(2024,1,3,20)):
    '''
    This extends the surface mask to all layers, and adds a time dimension
    '''
    depths = np.array(ds.depth.values)
    surface_mask = xr.open_dataset('norkyst_landmask.nc')
    #time_dim = xr.date_range(time_start, time_end, freq='h', calendar='gregorian')
    
    #TODO her kan man optimalisere masse senere
    time_start_string = time_start.strftime("%Y-%m-%d %H:%M:%S")
    hours_since = [0]
    k=0
    while time_start < time_end:
        time_start += datetime.timedelta(hours=1)
        k+=1
        hours_since.append(k)
    hours_since = np.array(hours_since)

    full_mask = np.zeros([len(hours_since), len(depths), np.shape(ds.h)[0], np.shape(ds.h)[1]])
    for i, depth in enumerate(depths):
        if depth <= 10:
            full_mask[:,i] = surface_mask.mask_rho.values
        else:
            layer_mask = np.array(ds.h.values)
            layer_mask = np.where(layer_mask < depth, 0, 1)
            full_mask[:,i] = layer_mask
    
    x = np.array(ds.X.values)
    y = np.array(ds.Y.values)
    mask_array = xr.Dataset(
        coords = dict(
            X=(['X'], x, {'units':'meter','standard_name':'projection_x_coordinate'}),
            Y=(['Y'], y, {'units':'meters', 'standard_name':'projection_y_coordinate'}),
            depth=(['depth'], depths, {'positive':'down','axis':'Z','standard_name':'depth', 'long_name': 'depth', 'units':'meter'}),
            time=(['time'], hours_since*60*60, {'long_name':'time since initialization', 'units':f'seconds since {time_start_string}', 'standard_name':'time', 'calendar':'gregorian'})),
        
        data_vars = dict(
            lon=(['Y', 'X'], np.array(ds.lon.values), {'grid_mapping': 'projection_stere','units':'degree_east', 'standard_name':'longitude','long_name':'longitude'}),
            lat=(['Y', 'X'], np.array(ds.lat.values), {'grid_mapping': 'projection_stere','units':'degree_north', 'standard_name':'latitude', 'long_name': 'latitude'}),
            land_binary_mask=(['time','depth','Y', 'X'], full_mask, {'standard_name': 'land_binary_mask', 'long_name':'land_binary_mask'})))
    mask_array['projection_stere'] = ds.projection_stere
    mask_array.to_netcdf('landsea_mask.nc', encoding={'time': {'dtype':'double'}})

    return full_mask

def only_surface_mask(ds, time_start = datetime.datetime(2024,1,1,0), time_end = datetime.datetime(2025,1,1,0)):
    '''
    adds a time dimension to surface mask
    '''

    surface_mask = xr.open_dataset('norkyst_landmask.nc')
    
    #TODO her kan man optimalisere masse senere
    time_start_string = time_start.strftime("%Y-%m-%d %H:%M:%S")
    hours_since = [0]
    k=0
    while time_start < time_end:
        time_start += datetime.timedelta(hours=1)
        k+=1
        hours_since.append(k)
    hours_since = np.array(hours_since)

    full_mask = np.zeros([len(hours_since), np.shape(ds.h)[0], np.shape(ds.h)[1]])
    full_mask[:,:,:] = surface_mask.mask_rho.values

    x = np.array(ds.X.values)
    y = np.array(ds.Y.values)
    mask_array = xr.Dataset(
        coords = dict(
            X=(['X'], x, {'units':'meter','standard_name':'projection_x_coordinate'}),
            Y=(['Y'], y, {'units':'meters', 'standard_name':'projection_y_coordinate'}),
            time=(['time'], hours_since*60*60, {'long_name':'time since initialization', 'units':f'seconds since {time_start_string}', 'standard_name':'time', 'calendar':'gregorian'})),
        
        data_vars = dict(
            lon=(['Y', 'X'], np.array(ds.lon.values), {'grid_mapping': 'projection_stere','units':'degree_east', 'standard_name':'longitude','long_name':'longitude'}),
            lat=(['Y', 'X'], np.array(ds.lat.values), {'grid_mapping': 'projection_stere','units':'degree_north', 'standard_name':'latitude', 'long_name': 'latitude'}),
            land_binary_mask=(['time','Y', 'X'], full_mask, {'standard_name': 'land_binary_mask', 'long_name':'land_binary_mask'})))
    mask_array['projection_stere'] = ds.projection_stere
    mask_array.to_netcdf('/lustre/storeB/project/fou/hi/foccus/mateuszm/OceanAI/datasets/surface_mask.nc', encoding={'time': {'dtype':'double'}, 'land_binary_mask':{'zlib': True, 'complevel': 4}})

    return full_mask

def extract_mask_from_file(file, output):
    '''
    Extracts the mask from file and writes it to file
    '''
    ds = xr.open_dataset(file)
    proj = xr.open_dataset('/lustre/storeB/project/fou/hi/oper/norkyst_v3/forecast/his_zdepths/2024/05/11/norkyst800_his_zdepth_20240511T00Z_m00_AN.nc')['projection_stere']
    mask = ds.mask_rho.values
    
    x = np.array(ds.xi_rho.values)
    y = np.array(ds.eta_rho.values)
    mask_array = xr.Dataset(
        coords = dict(    
            X=(['X'], x, {'units':'meter','standard_name':'projection_x_coordinate'}),
            Y=(['Y'], y, {'units':'meters', 'standard_name':'projection_y_coordinate'})),
        data_vars = dict(
            lon=(['Y', 'X'], np.array(ds.lon_rho.values), {'grid_mapping': 'projection_stere','units':'degree_east', 'standard_name':'longitude','long_name':'longitude'}),
            lat=(['Y', 'X'], np.array(ds.lat_rho.values), {'grid_mapping': 'projection_stere','units':'degree_north', 'standard_name':'latitude', 'long_name': 'latitude'}),
            land_binary_mask=(['Y', 'X'], mask, {'standard_name': 'land_binary_mask', 'long_name':'land_binary_mask'})
    ))
    mask_array['projection_stere']=proj
    mask_array.to_netcdf(output)

    

if __name__ == '__main__':
    path = '/lustre/storeB/project/fou/hi/oper/norkyst_v3/forecast/his/2024/05/01/'
    files = ['norkyst800_his_sdepth_20240501T00Z_m00_AN.nc', 'norkyst160_his_sdepth_20240501T00Z_m70_AN.nc', 'norkyst160_his_sdepth_20240501T00Z_m71_AN.nc']
    output_path = '/lustre/storeB/project/fou/hi/foccus/datasets/'
    outputs = ['norkyst_v3-800m_mask.nc', 'norkyst_v3-160m-70_mask.nc', 'norkyst_v3-160m-71_mask.nc']
    for i in range(len(files)):
        extract_mask_from_file(path+files[i], output=output_path+outputs[i])
