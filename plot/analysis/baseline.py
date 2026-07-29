#import necessary packages
import numpy as np 
import xarray as xr

#import glob and select symlink for 2024
import glob
filepath_daily_avg = '/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_averages/daily_avg'
ds_all_years = glob.glob(f'{filepath_daily_avg}/*/*.nc')
ds = xr.open_mfdataset(ds_all_years, engine='netcdf4')

#Make monthly mean and group by each month
ds = ds.sortby('time')
monthly_mean = ds.resample(time = 'M').mean('time')
ds_monthly = ds.groupby('time.month').mean('time')
print(f'successfully created the baseline month')

#symlink info 
symlink_path = f'/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/' 

def calculate_anomalies(monthly_files, m_indx, output):
    ds_calc = xr.open_mfdataset(monthly_files).isel(s_rho = -1, s_w = -1)
    print(f'Successfully opened the monthly sets')
    monthly_baseline = ds_monthly.sel(month = m_indx).salinity.values
    anomalies = ds_calc.salinity.values - monthly_baseline
    print(f'Successfully calculated the anomalies')
    ds_calc['salinity_anomalies'] = (('time', 'Y', 'X'), anomalies)
    print(f'Successfully appended the anomalies to the existing dataset')
    ds_calc.to_netcdf(output)     
    print(f'finished')

output = '/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_averages/anomalies/january.nc'
ds_with_anomalies = calculate_anomalies(monthly_files=f'{symlink_path}norkyst800-202401*',
                        m_indx=1,
                        output=output)



