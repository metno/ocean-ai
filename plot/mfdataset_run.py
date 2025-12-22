import xarray as xr
import numpy as np 
import glob 
import sys
import argparse

#To make the job easier, I will remove a few variables to take up less memory
#We only use temperature, s_rho, salinity, s_w and all variables for transforming the rho coordinates to depth
#Therefore we might remove wind, speed?

def monthly_mean(file_path, save_path):
    files = glob.glob(file_path)
    print(f'Glob identified the following files: {files}')
    ds = xr.open_mfdataset(files).dropvars('u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward').resample(time = '1M').mean()
    ds.to_netcdf(save_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creating a new netcdf file containing the monthly means of 2024 HINDCAST (Norkyst) with dropped variables that are not used in the calculation of mld')
    parser.add_argument('file_path', help = 'Filepath to the existing datasets. Please enter the full path')
    parser.add_argument('save_path', help='The path to where the new netcdf file should be saved. Please enter the full path')
    args = parser.parse_args()

    file_path = args.file_path
    save_path = args.save_path

monthly_mean(file_path, save_path)
