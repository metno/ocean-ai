import xarray as xr
import numpy as np 
import glob 
import sys
import argparse

#To make the job easier, I will remove a few variables to take up less memory
#We only use temperature, s_rho, salinity, s_w and all variables for transforming the rho coordinates to depth
#Therefore we might remove wind, speed?

#the files are too big, maybe do a month at a time? 

def monthly_mean(save_path):
    files = glob.glob("/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/*.nc")
    files = sorted(files)
    print(f'Glob identified the following files: {files}')

    jan = []
    feb = []
    march = []
    april = []
    may = []
    june = []
    july = []
    aug = []
    sept = []
    oct = []
    nov = []
    dec = []

    months = (jan, feb, march, april, may, june, july, aug, sept, oct, nov, dec)
    dates = (0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)

    for i in range(12):
        if i < 11:
            months[i].extend(files[dates[i]:dates[i+1]])
        elif i ==11:
            months[i].extend(files[dates[i]:])
        else:
            continue
        
    ds_jan = xr.open_mfdataset(jan, engine = 'h5netcdf', chunks={'time' : 1}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()
    ds_feb = xr.open_mfdataset(feb, engine = 'h5netcdf', chunks={'time' : 1}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()
    ds_march = xr.open_mfdataset(march, engine = 'h5netcdf', chunks={'time' : 1}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()
    ds_april = xr.open_mfdataset(april, engine = 'h5netcdf', chunks={'time' : 1}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()
    ds_may = xr.open_mfdataset(may, engine = 'h5netcdf', chunks={'time' : 1}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()
    ds_june = xr.open_mfdataset(june, engine = 'h5netcdf', chunks={'time' : 1}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()
    ds_july = xr.open_mfdataset(july, engine = 'h5netcdf', chunks={'time' : 1}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()
    ds_aug = xr.open_mfdataset(aug, engine = 'h5netcdf', chunks={'time' : 1}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()
    ds_sept = xr.open_mfdataset(sept, engine = 'h5netcdf', chunks={'time' : 1}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()
    ds_oct = xr.open_mfdataset(oct, engine = 'h5netcdf', chunks={'time' : 1}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()
    ds_nov = xr.open_mfdataset(nov, engine = 'h5netcdf', chunks={'time' : 1}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()
    ds_dec = xr.open_mfdataset(dec, engine = 'h5netcdf', chunks={'time' : 1}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()

    ds = xr.concat([ds_jan, ds_feb, ds_march, ds_april, ds_may, ds_june, ds_july, ds_aug, ds_sept, ds_oct, ds_nov, ds_dec], dim = 'time').sortby('time')
    ds.to_netcdf(save_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creating a new netcdf file containing the monthly means of 2024 HINDCAST (Norkyst) with dropped variables that are not used in the calculation of mld')
    parser.add_argument('-sp', '--save_path', help='The path to where the new netcdf file should be saved. Please enter the full path')
    args = parser.parse_args()
    save_path = args.save_path

monthly_mean(save_path)
