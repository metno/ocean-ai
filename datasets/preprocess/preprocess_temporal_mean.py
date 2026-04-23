import xarray as xr

def temporal_mean(files, output, depth=None):
    '''
        Very simple function to produce mean files
    '''
    ds = xr.open_mfdataset(files)

    if depth is not None:
        if 's_rho' in ds.variables:
            ds = ds.isel(s_rho=depth)
        elif 'depth' in ds.variables:
            ds = ds.isel(depth=depth)

    ds_m = ds.mean('time')
    ds_m.to_netcdf(output)
    return ds_m

    
    


if __name__ == '__main__':
    temporal_mean('/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/norkyst800-202405*', 
                  '/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_averages/norkyst800-202405_avg.nc',
                  depth=-1)