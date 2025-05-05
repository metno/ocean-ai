import fimex
import os
import datetime
import netCDF4
import numpy as np

def interpolate_atm_forcing(atm_file):
    # can't use fimex when files don't have proj string built in. Go to hor_interop function below
    #TODO Fimex will most likely be faster than most other things, so remember to use this when we get files with actual proj strings
    with netCDF4.Dataset(atm_file, mode='a') as ncfile:
        try:
            pl = ncfile.createVariable('projection_lambert', float)
            pl.grid_mapping_name = 'lambert_conformal_conic'
            pl.standard_parallel = '63.3, 63.3'
            pl.latitude_of_projection_origin = 63.3
            pl.longitude_of_central_meridian = 15.
            pl.earth_radius = 6371000.
            pl.proj4 = '+proj=lcc +lat_0=63.3 +lon_0=15 +lat_1=63.3 +lat_2=63.3 +no_defs +R=6.371e+06'
        except:
            pass
        
        for var in ncfile.variables:
            print(var)
            if var not in ['time', 'projection_lambert']:
                ncfile[var].grid_mapping = 'projection_lambert'
            if var == 'lon':
                ncfile[var].standard_name='longitude'
            if var == 'lat':
                ncfile[var].standard_name='latitude'
        ncfile.history = ''
        ncfile.Conventions = 'CF-1.6'
    
    atm_cfg = 'fimex/atm.cfg'
    cfg = fimex.FimexConfig()
    cfg.read_cfg(atm_cfg)
    cfg.addattr('input', 'file', atm_file)
    cfg.addattr('output', 'file', atm_file.replace('.nc', '_NK800.nc'))
    cfg.addattr("extract", "reduceTime.start", datetime.datetime(2020,1,1,2))
    cfg.addattr("extract", "reduceTime.end", datetime.datetime(2020,1,1,4))
    #cfg.addattr('ncml', 'config', 'fimex/arome_meps_names.ncml')
    cfg.run_fimex(fimex_kwargs={'-n': str(8)})

def hor_interp(lati,loni,lato,lono,vari,method='nearest'):
    from scipy.interpolate import griddata
    import sys
    #From Nils, https://gitlab.met.no/ocean-ice/tools/toolbox/-/blob/main/toolbox/roms/ROMStools.py?ref_type=heads
    #This will interpolate the input variable to the output grid
    if ( len(vari.shape) == 1 ):
        varo = griddata((lati,loni),vari,(lato,lono), method)
    elif ( len(vari.shape) == 2 ):
        varo = griddata((np.hstack(lati),np.hstack(loni)),np.hstack(vari),(lato,lono), method)
    elif ( len(vari.shape) == 3 ):
        t, ydum, xdum = vari.shape
        y, x = lato.shape
        varo = np.zeros([t,y,x])
        for i in range(t):
            varo[i,:,:] = griddata((np.hstack(lati),np.hstack(loni)),np.hstack(vari[i,:,:]),(lato,lono), method)
    elif ( len(vari.shape) == 4 ):
        t, s, ydum, xdum = vari.shape
        y, x = lato.shape
        varo = np.zeros([t,s,y,x])
        for i in range(t):
            for j in range(s):
                varo[i,j,:,:] = griddata((np.hstack(lati),np.hstack(loni)),np.hstack(vari[i,j,:,:]),(lato,lono), method)
    else:
        print('unsupported number of dims on variable '+str(len(vari.shape)))
        sys.exit()
    return varo


if __name__ == '__main__':
    import xarray as xr
    ds = xr.open_dataset('arome_meps_2_5km_2020010100-2020020412_ext.nc').isel(time=slice(1,3))
    nk800 = xr.open_dataset('/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2012/norkyst800-20121226.nc').isel(time=0, s_rho=0)
    var = hor_interp(ds.lat.values, ds.lon.values, nk800.lat.values, nk800.lon.values, ds.Qair, method='linear')
    print(var)
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1,2)
    
    ax[0].scatter(ds.lon, ds.lat, c=ds.Qair.isel(time=0), vmin=0, vmax=100)
    ax[1].scatter(nk800.lon, nk800.lat, c=var[0,:,:], vmin=0, vmax=100)
    plt.savefig('atm_nk800_lin.png')
