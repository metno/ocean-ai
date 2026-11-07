import xarray as xr
import glob

""" 
Script for resampling datasets into: 
    - Yearly mean data
    - Seasonal data
    - Monthly mean data 
"""

##To reduce mem usage - the code will be dealing with one and one variable even though its not an ideal build-up neither
def open_files(filepath, output_path, Norkyst = False):
    """
    Opening files from a given filepath. 
    Please ensure the argument filepath consists of a full path to the .nc files you wish to resample. 
    Also ensure that an output path is added 
    """
    filenames = glob.glob(f'{filepath}/*.nc')
    if Norkyst is not False:
        ds = xr.open_mfdataset(filenames, engine = 'netcdf4').isel(s_rho = -1, s_w = -1)
    if Norkyst is False:
        ds = xr.open_mfdataset(filenames, engine = 'netcdf4')

    salinity = ds.salinity_0
    temperature = ds.temperature_0
    v_northward = ds.v_northward_0
    u_eastward = ds.u_eastward_0
    zeta = ds.zeta

    ds_monthly_s = salinity.resample(time = 'MS').mean().compute() #computing before saving to save mem 
    ds_monthly_t = temperature.resample(time = 'MS').mean().compute()
    ds_monthly_v = v_northward.resample(time = 'MS').mean().compute()
    ds_monthly_u = u_eastward.resample(time = 'MS').mean().compute()
    ds_monthly_z = zeta.resample(time = 'MS').mean().compute() 

    ds_final_monthly = xr.merge([ds_monthly_s, ds_monthly_t, ds_monthly_u, ds_monthly_v, ds_monthly_z])
    ds_final_monthly.to_netcdf(f'{output_path}/monthly_mean.nc')
    print(f'The resampled monthly mean for all four variables is now saved to the provided output path')

    #Now resample these to a year
    yearly_avg_s = ds_monthly_s.resample(time = 'Y').mean().compute()
    yearly_avg_t = ds_monthly_t.resample(time = 'Y').mean().compute()
    yearly_avg_v = ds_monthly_v.resample(time = 'Y').mean().compute()
    yearly_avg_u = ds_monthly_u.resample(time = 'Y').mean().compute()
    yearly_avg_z = ds_monthly_z.resample(time = 'Y').mean().compute()

    ds_final_yearly = xr.merge([yearly_avg_s, yearly_avg_t, yearly_avg_v, yearly_avg_u, yearly_avg_z])
    ds_final_yearly.to_netcdf(f'{output_path}/yearly_mean.nc')
    print(f'The resampled yearly mean for all four variables is now saved to the provided output path')

    #Now lets make it seasonal
    month_length = ds.time.dt.days_in_month
    #Preview
    print(f'Please ensure that all seasons have a weight sum of 1.0 in the following statement! If not, refer to https://docs.xarray.dev/en/stable/examples/monthly-means.html.')
    print(weights.groupby('time.season').sum().values) #Should equal for all seasons (ie. 1, 1, 1, 1)
    weights = month_length.groupby('time.season') / month_length.groupby('time.season').sum(skipna = False)
    ds_weighted = (ds_final_monthly*weights).groupby('time.season').sum(dim = 'time', skipna = False)
    ds_weighted.to_netcdf(f'{output_path}/seasonal_means.nc')

    print(f'All resampled means are saved to {output_path}!')


filepath = '/lustre/storeB/project/fou/hi/foccus/malene/run-ocean-anemoi/ppi/external_checkpoint_inference/results/rollout_benchmark_lr3.5e6-rs3-i0-m3/step_51000_e14'
output_path = '/lustre/storeB/project/fou/hi/foccus/malene/run-ocean-anemoi/ppi/external_checkpoint_inference/results/rollout_benchmark_lr3.5e6-rs3-i0-m3/step_51000_e14/resampled_means'
open_files(filepath, output_path, Norkyst = False)