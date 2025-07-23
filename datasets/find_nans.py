# Does dataset have any nans inside ocean domain?
# 
# TODO: check 2012 dataset
# 
# Checking 2013-2024

import numpy as np
from anemoi.datasets import open_dataset
from anemoi.datasets import MissingDateError
import sys

if len(sys.argv) > 1:
    year = sys.argv[1]
else:
    raise ValueError('Please provide year as command line argument')

#----------------------------------------------------------------------------
# Load dataset and print some information to output file
#----------------------------------------------------------------------------
file = f'/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_hindcast_{year}_surface.zarr'
outfile = f'/lustre/storeB/project/fou/hi/foccus/datasets/nan_in_vars_{year}.txt'

# e.g. dropping ubar and vbar
variable_names = ['Uwind_eastward','Vwind_northward','h','salinity_0','sea_mask','temperature_0','u_eastward_0','v_northward_0','zeta']
ds = open_dataset(file, select=variable_names)

f = open(outfile, 'w')
f.write(f"# Dataset: {file}\n")
f.write(f"# Year: {year}\n")
f.write(f"# Shape of dataset: {ds.shape}\n")
f.write(f"# Variable names: {variable_names}\n")
f.write(f"# \n")

#----------------------------------------------------------------------------
# Check for nans in ocean domain
#----------------------------------------------------------------------------

# Some datasets have missing dates, e.g. 2012 which we hav to handle. 
# get the index of the missing dates
ind_missing = np.array(list(ds.missing))
ind_all = np.arange(ds.shape[0])
ind_not_missing = np.setdiff1d(ind_all, ind_missing)

# sea mask is constant in time, so just need to use a valid time index
sea_mask = np.bool(ds[int(ind_not_missing[0]),ds.name_to_index['sea_mask'],0,:])

#----------------------------------------------------------------------------
# Loop over variables and istep time indices at the time to save memory
istep = 100  # step size for time index
var_dict = ds.name_to_index 
for var in var_dict:
    ivar = var_dict[var]
    if var == 'sea_mask':
        # skip sea_mask var
        continue
    
    print(f'# Checking variable: {var} (ivar={ivar})\n')
    
    for i in range(0, ds.shape[0], istep):
        print(f"i= {i}, var= {var}, ivar= {ivar}")

        try:
            ds_var = ds[i:i+istep,ivar,0,:]
            ind_time,ind_grid = np.where(np.isnan(ds_var))
            print(f"ind_time={ind_time}, ind_grid={ind_grid}") 
        except MissingDateError as e:
            print(f"MissingDateError:",e)
            i_not_missing = np.intersect1d(ind_not_missing, np.arange(i, i+istep))
            print(f"i_not_missing={i_not_missing}")
            if i_not_missing.size != 0:
                ind_time,ind_grid = np.where(np.isnan(ds[i_not_missing[0]:i_not_missing[-1]+1,ivar,0,:]))
                ind_time += i_not_missing[0]  # adjust index to the current step
            else:
                ind_time = np.array([])  

        if var not in ['Uwind_eastward','Vwind_northward','u_eastward_0','v_northward_0']:
            # The above variables has values over land. 
            # For those that dont, we will only write to file when nans found in the sea
            intersect_nan_sea = np.intersect1d(ind_grid, np.where(sea_mask)[0], return_indices=True)[0]
            ind_grid = ind_grid[intersect_nan_sea]
            ind_time = ind_time[intersect_nan_sea]
            # this ofthen returns empty arrays
        if ind_time.size > 0 and ind_grid.size > 0:
            for n in range(len(ind_time)):
                it=int(ind_time[n])
                ig=int(ind_grid[n])
                f.write(f"{var}: ds[ {i+it}, {ivar}, 0, {ig} ] = {ds[i+it,ivar,0,ig]}\n")
                # print(f"{var}: ds[ {i+it}, {ivar}, 0, {ig} ] = {ds[i+it,ivar,0,ig]}\n")

f. close()

