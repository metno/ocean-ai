import fimex
import os
import datetime
import netCDF4
import numpy as np

def interpolate_atm_forcing(atm_file):

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

if __name__ == '__main__':
    interpolate_atm_forcing('arome_meps_2_5km_2020010100-2020020412_ext.nc')