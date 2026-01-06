import xarray as xr
import numpy as np 
import glob 
import sys
import argparse

#To make the job easier, I will remove a few variables to take up less memory
#We only use temperature, s_rho, salinity, s_w and all variables for transforming the rho coordinates to depth
#Therefore we might remove wind, speed?

#the files are too big, maybe do a month at a time? 

def monthly_mean(save_path, month):
    files = glob.glob("/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/*.nc")
    files = sorted(files)
    print(f'Glob identified the following files: {files}')

    list = month
    list = []
    if month == 'January':
        dates = (0,31)
    elif month == 'February':
        dates = (31,60)
    elif month == 'March':
        dates = (60,91)
    elif month == 'April':
        dates = (91,121)
    elif month == 'May':
        dates = (121,152)
    elif month == 'June':
        dates = (152,182)
    elif month == 'July':
        dates = (182,213)
    elif month == 'August':
        dates = (213,244)
    elif month == 'September':
        dates = (244,274)
    elif month == 'October':
        dates = (274,305)
    elif month == 'November':
        dates = (305,335)
    elif month == 'December':
        dates = (335,366)
    else:
        raise ValueError('Please specify which month to calculate monthly means for, such as January')

    list.extend(files[dates[0]:dates[1]])
    ds = xr.open_mfdataset(list, engine = 'h5netcdf', chunks={'time' : 1}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()
    #Because there is an issue with the encoding of the summaries and the keywords, we have to manually remove those 
    if 'summary_no' in ds.attrs:
        del ds.attrs['summary_no']
    if 'keywords' in ds.attrs:
        del ds.attrs['keywords']

    ds.to_netcdf(f'{save_path}/{month}.nc')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creating a new netcdf file containing the monthly means of 2024 HINDCAST (Norkyst) with dropped variables that are not used in the calculation of mld')
    parser.add_argument('-sp', '--save_path', help='The path to where the new netcdf file should be saved. Please enter the full path')
    parser.add_argument('-mn', '--month', help = 'Please enter the month you wish to create the monthly mean for')
    args = parser.parse_args()
    save_path = args.save_path
    month = args.month

monthly_mean(save_path, month)