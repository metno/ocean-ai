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

#symlink info 
symlink_path = f'/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/' 

def calculate_anomalies(monthly_files, m_indx, output):
    ds = xr.open_mfdataset(monthly_files)
    monthly_baseline = ds_monthly.sel(month = m_indx).salinity.values
    anomalies = ds.salinity.values - monthly_baseline
    anomalies.to_netcdf(output)  

output = '/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_averages/anomalies'
m_indx = [1,2,3,4,5,6,7,8,9,10,11,12]
names = ['jan', 'feb','march','april','may','june','july','aug','sept','oct','nov','dec']

for i,n in zip(m_indx,names):
    if len(str(i)) == 2:
        calculate_anomalies(monthly_files=f'{symlink_path}norkyst800-2024{i}*',
                            m_indx=m_indx,
                            output=f'{output}/{n}.nc') 
    elif len(str(i)) == 1:
        calculate_anomalies(monthly_files=f'{symlink_path}norkyst800-20240{i}*',
                                    m_indx=m_indx,
                                    output=f'{output}/{n}.nc') 
