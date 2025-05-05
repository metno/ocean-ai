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
            print(f'{i+1} : {t}')
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

def run_hor_interp(file):
    import xarray as xr

    ds = xr.open_dataset(file)
    nk800 = xr.open_dataset('/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2012/norkyst800-20121226.nc').isel(time=0, s_rho=0)
    
    vars = ['Pair', 'Uwind', 'Vwind', 'Tair', 'Qair', 'cloud', 'rain']
    
    reference_date = np.datetime64('1970-01-01T00:00:00', 's')
    times = np.zeros_like(ds.time.values, dtype='int')

    for time in range(len(times)):
        difference_in_seconds = (ds.isel(time=time).time.values - reference_date).astype('timedelta64[s]')
        difference_in_hours = difference_in_seconds / np.timedelta64(1, 'h')
        times[time] = difference_in_hours

    atm_ds = xr.Dataset(
        coords = dict(
            X=(['X'], np.array(nk800.X.values), {'units':'meter','standard_name':'projection_x_coordinate'}),
            Y=(['Y'], np.array(nk800.Y.values), {'units':'meters', 'standard_name':'projection_y_coordinate'}),
            time=(['time'], times, {'long_name':'time since initialization', 'units':f'seconds since 1970-01-01 00:00:00', 'standard_name':'time', 'calendar':'gregorian'}),
        ),
        data_vars = dict(
            lon=(['Y', 'X'], np.array(nk800.lon.values), {'grid_mapping': 'projection_stere','units':'degree_east', 'standard_name':'longitude','long_name':'longitude'}),
            lat=(['Y', 'X'], np.array(nk800.lat.values), {'grid_mapping': 'projection_stere','units':'degree_north', 'standard_name':'latitude', 'long_name': 'latitude'})
        ))
    for var in vars:
        print(var)
        varo = hor_interp(ds.lat.values, ds.lon.values, nk800.lat.values, nk800.lon.values, ds[var], method='linear')

        # A little rough coding because atm_ds = atm_ds.assign(var=(['time', 'Y', 'X'], varo)) set the variable name to 'var' and overwrote the previous. 
        # This can probably be changed to something cleaner, but as long as it works its fine for now. 
        if var == 'Pair':
            atm_ds = atm_ds.assign(Pair=(['time', 'Y', 'X'], varo, {'grid_mapping': 'projection_stere', 'units':'Pa', 'standard_name':'surface_air_pressure'}))
        elif var == 'Uwind':
            atm_ds = atm_ds.assign(Uwind=(['time', 'Y', 'X'], varo, {'grid_mapping': 'projection_stere', 'units':'meter second-1', 'standard_name':'eastward_wind'}))
        elif var == 'Vwind':
            atm_ds = atm_ds.assign(Vwind=(['time', 'Y', 'X'], varo, {'grid_mapping': 'projection_stere', 'units':'meter second-1', 'standard_name':'northward_wind'}))
        elif var == 'Tair':
            atm_ds = atm_ds.assign(Tair=(['time', 'Y', 'X'], varo, {'grid_mapping': 'projection_stere', 'units':'K', 'standard_name':'air_potential_temperature'}))
        elif var == 'Qair':
            atm_ds = atm_ds.assign(Qair=(['time', 'Y', 'X'], varo, {'grid_mapping': 'projection_stere', 'units':'1', 'standard_name':'relative_humidity'}))
        elif var == 'cloud':
            atm_ds = atm_ds.assign(cloud=(['time', 'Y', 'X'], varo, {'grid_mapping': 'projection_stere', 'units':'1', 'standard_name':'cloud_area_fraction'}))
        elif var == 'rain':
            atm_ds = atm_ds.assign(rain=(['time', 'Y', 'X'], varo, {'grid_mapping': 'projection_stere', 'units':'kg m-2 s-1', 'standard_name':'precipitation_flux'}))
    atm_ds.to_netcdf(file.replace('.nc', '_NF800.nc'))

if __name__ == '__main__':
    import sys
    file = sys.argv[1]
    #file = 'arome_meps_2_5km_2020010100-2020020412_ext.nc'
    run_hor_interp(file)


