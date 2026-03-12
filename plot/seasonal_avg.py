import xarray as xr 
import numpy as np 
import glob
import sys
import argparse
import time

fp = '/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/*.nc'

def mean_sesavg(save_path):

    start_time = time.perf_counter()

    files = glob.glob(fp)
    files = sorted(files)

    def month_mean(nc_files, start_date, end_date, month_name):
        list_month = []
        list_month.extend(nc_files[start_date:end_date])
        print(f'The identified filepaths for {month_name} are: {list_month}')
        ds = xr.open_mfdataset(list_month, engine = 'h5netcdf', chunks={'time' : 10, 'lon' : 100, 'lat' : 100}).drop_vars(['u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'Uwind_eastward', 'Vwind_northward']).resample(time = '1M').mean()
        print(f'The month of {month_name} has the following files: {list_month}')
        return ds

    ds_jan = month_mean(files, 0, 31, 'January')
    ds_feb = month_mean(files, 31, 60, 'February')
    ds_march = month_mean(files, 60, 91, 'March')
    ds_april = month_mean(files, 91, 121, 'April')
    ds_may = month_mean(files, 121, 152, 'May')
    ds_june = month_mean(files, 152, 182, 'June')
    ds_july = month_mean(files, 182, 213, 'July')
    ds_aug = month_mean(files, 213, 244, 'August')
    ds_sept = month_mean(files, 244, 274, 'September')
    ds_oct = month_mean(files, 274, 305, 'October')
    ds_nov = month_mean(files, 305, 335, 'November')
    ds_dec = month_mean(files, 335, 366, 'December')

    ds = xr.concat([ds_jan, ds_feb, ds_march, ds_april, ds_may, ds_june, ds_july, ds_aug, ds_sept, ds_oct, ds_nov, ds_dec], dim = 'time')
    print('Concat of the monthly mean was successfull')
    print(ds.head) 
    
    if 'summary_no' in ds.attrs:
        del ds.attrs['summary_no']
    if 'keywords' in ds.attrs:
        del ds.attrs['keywords']

    print('Made it to the calculations of the seasonal averages')
    #This code is from the xarray tutorial: https://docs.xarray.dev/en/latest/examples/monthly-means.html
    month_length = ds.time.dt.days_in_month
    weights = (month_length.groupby("time.season") / month_length.groupby("time.season").sum())
    # Test that the sum of the weights for each season is 1.0
    np.testing.assert_allclose(weights.groupby("time.season").sum().values, np.ones(4))
    # Calculate the weighted average
    ds_weighted = (ds * weights).groupby("time.season").sum(dim="time")

    print('Made it to creating a netcdf file of the results')
    for season in ds_weighted.season.values:
        ds_season = ds_weighted.sel(season = season)
        ds_season.to_netcdf(f'{save_path}/{season}.nc', engine = 'netcdf4')
    #ds_weighted.to_netcdf(f'{save_path}', engine = 'netcdf4')
    #Takes too much mem to transfer to netcdf so Ill try converting to zarr files 
    print(f'The datasets of the seasonal averages have been transformed into netdf files')

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    statement_time = f'End of function. Elapsed time is: {elapsed_time}'
    return statement_time

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Calculation of seasonal averages of Norkyst dataset with monthly means')
    parser.add_argument('-sp' , '--save_path', help = 'Please enter wished saving path for the new netcdf file')
    args = parser.parse_args()
    save_path = args.save_path

mean_sesavg(save_path)