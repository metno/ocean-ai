import xarray as xr
import netCDF4

def fix_proj(file):
    nk800 = xr.open_dataset('/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2012/norkyst800-20121226.nc').isel(time=0, s_rho=0)[['lon', 'lat', 'projection_stere']]
    ds = xr.open_dataset(file)
    ds['projection_stere'] = nk800.projection_stere
    ds.to_netcdf(file.replace('.nc', 'fixed_proj.nc'))

def fix_time(file):
    with netCDF4.Dataset(file, 'r+') as ds:
        ds['time'].units = 'hours since 1970-01-01'
        ds.sync()

if __name__ == '__main__':
    import sys
    file = sys.argv[1]
    fix_time(file)
