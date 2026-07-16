import xarray as xr

def temporal_mean_daily(files, output, depth=None):
    '''
        Very simple function to produce mean files to use for the salinity anomalies. 
    '''    
        
    ds = xr.open_mfdataset(files)
    if depth is not None:
        if 's_rho' in ds.variables:
            ds = ds.isel(s_rho=depth)
        elif 'depth' in ds.variables:
            ds = ds.isel(depth=depth)

    if 's_w' in ds.variables:
        ds = ds.isel(s_w=depth)
    
    if 'salinity' in ds.variables:
        ds_salt = ds.salinity 
    
    ds_m = ds_salt.resample(time = 'D').mean()
    ds_m.to_netcdf(output)
    return ds_m


if __name__ == '__main__':
    for i in [1,2,3,4,5,6,7,8,9,10,11,12]:
        if len(str(i)) == 2:
            temporal_mean_daily(f'/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/norkyst800-2024{i}*', 
                  f'/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_averages/anomalies/daily_avg/norkyst800-2024{i}_avg.nc',
                  depth=-1)
        elif len(str(i)) == 1:
            temporal_mean_daily(f'/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/norkyst800-20240{i}*', 
                  f'/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_averages/anomalies/daily_avg/norkyst800-20240{i}_avg.nc',
                  depth=-1)