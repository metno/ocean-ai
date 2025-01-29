import dask.array as darray
import anemoi.datasets as ad
#import xarray as xr
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs

z = ad.open_dataset('norkystv3_2024010100-2024010220.zarr')
indx_temp1 = z.name_to_index['temperature_1']
temp_1 = z[0,indx_temp1,0,:]
mask = np.isfinite(temp_1)

# Use the mask to get a new array without NaN values
temp_n = temp_1[mask]
lat_n = z.latitudes[mask]
lon_n = z.longitudes[mask]

lat_n = np.array(lat_n)
lon_n = np.array(lon_n)

np.savez('grid-o96.npz', longitudes=lon_n, latitudes=lat_n)
