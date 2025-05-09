import xarray as xr

def combine(file, vars):
    
    all_files = []
    for var in vars:
        all_files.append(file + '_' + var + '.nc')
    
    ds = xr.open_mfdataset(all_files)
    ds.to_netcdf(file+'.nc')
        



if __name__ == '__main__':
    file = '/lustre/storeB/project/fou/hi/foccus/datasets/norkyst-v3-hindcast/interp_forcings/arome_meps_2_5km_2017010100-2017090606_ext_NF800'
    vars = ['Pair', 'Uwind', 'Vwind', 'Tair', 'Qair', 'cloud', 'rain']
    combine(file, vars)