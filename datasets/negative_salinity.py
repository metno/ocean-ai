# Where and when is the salinity negative?

import xarray as xr
from anemoi.datasets import open_dataset
from anemoi.datasets import MissingDateError
#import matplotlib.pyplot as plt
import numpy as np
import sys

if len(sys.argv) > 1:
    year = sys.argv[1]
else:
    raise ValueError('Please provide year as command line argument')

# Years with neg salinity: 2024, 2022, 2020, 2019, 2017, 2015, 2013, 2012
# (from anemoi-datasets inspect ../datasets/norkystv3_hindcast_2024_surface.zarr)
filename = f'/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_hindcast_{year}_surface.zarr'
outfile= f'/lustre/storeB/project/fou/hi/foccus/datasets/negative_salinity_{year}.txt'

ds_sal = open_dataset(filename, select = "salinity_0")

# Get the index of the missing dates, if any (relevant 2012)
ind_missing = np.array(list(ds_sal.missing))
ind_all = np.arange(ds_sal.shape[0])
ind_not_missing = np.setdiff1d(ind_all, ind_missing)

# Find all points in ds_sal where salinity is below zero in steps of istep=100 (time index).
# This takes a while...
f = open(outfile, 'w')
f.write(f"# Negative salinity for {year}\n")
f.write(f"# filename = '{filename}'\n")
f.write( "# Format: ds_sal[ itime, 0, 0, igrid ] = value\n")
f.write( "# where ds_sal = open_dataset(filename, select = \"salinity_0\") using anemoi-datasets\n")
print(f"Processing file: {filename}")
istep = 100  # step size for time index
for i in range(0, ds_sal.shape[0], istep):
    print(f"i= {i}") 

    try:
        ind_time,ind_grid = np.where(ds_sal[i:i+istep,0,0,:] < 0)
        print(f"ind_time={ind_time}, ind_grid={ind_grid}") 
    except MissingDateError as e:
        print(f"MissingDateError:",e)
        i_not_missing = np.intersect1d(ind_not_missing, np.arange(i, i+istep))
        print(f"i_not_missing={i_not_missing}")
        if i_not_missing.size != 0:
            ind_time,ind_grid = np.where(ds_sal[i_not_missing[0]:i_not_missing[-1]+1,0,0,:] < 0)
            print(f"ind_time={ind_time}, ind_grid={ind_grid}")
        else:
            ind_time = np.array([])  
    
    if len(ind_time) > 0:
        for n in range(len(ind_time)):
            it=int(ind_time[n])
            ig=int(ind_grid[n])
            f.write(f"ds_sal[ {i+it}, 0, 0, {ig} ] = {ds_sal[i+it,0,0,ig]}\n")

f.close()

"""
# Plotting
lon = ds_sal.longitudes
lat = ds_sal.latitudes

# Plot where saltinity is negative
fig, ax = plt.subplots(1, 1, figsize=(12, 6))

im = ax.scatter(lon,lat, c=sal_neg_range[28,:],s=0.1, vmax=0.1)#,cmap='Set1')
plt.colorbar(im, ax=ax)

# its only one point in each time step???
arg = np.argwhere(sal_neg_range[29, :] < 0).flatten()[0]
print(f"Negative salinity found at indices {arg}")

lon_neg = np.where(sal_neg_range[28, :] < 0, lon, np.nan)
lat_neg = np.where(sal_neg_range[28, :] < 0, lat, np.nan)
sal_neg2 = np.where(sal_neg_range[28, :] < 0, sal_neg_range[28, :], np.nan)


# Plot where saltinity is negative
fig2, ax2 = plt.subplots(1, 1, figsize=(12, 6))

im = ax2.scatter(lon_neg, lat_neg, c=sal_neg2)#, s=0.1)
plt.colorbar(im, ax=ax2)
"""



# For 2024, these are the indices where negative salinity was found
#i= 3400
#Negative salinity found 
#i= 3500
#Negative salinity found 
#...
#i= 3800
#Negative salinity found 
#i= 3900
#Negative salinity found 
# ---> indices 3400-3600, 3800-4000
