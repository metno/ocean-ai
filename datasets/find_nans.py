# Does dataset have any nans inside ocean domain?
# 
# TODO: check 2012 dataset
# 
# Checking 2013-2024

import numpy as np
from anemoi.datasets import open_dataset
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

# Loop over variables and time to save memory
for ivar in range(ds.shape[1]):
    found_nans = False
    print('-----\nChecking variable:', variable_names[ivar])
    for itime in range(ds.shape[0]):
        if ivar == ds.name_to_index['sea_mask']:
            # skip sea_mask
            continue

        # get one variable
        var = ds[itime,ivar,:,:]  # Request enough memory!! About 103 GiB for shape (8784, 1, 3153556) and data type float32
        var_ocean = var[sea_mask] # get a 1D (flat) array (1822664,)
        
        if itime % 500 == 0:
            # print itime every 500
            print('itime:', itime)

        if np.isnan(var_ocean).any():
            found_nans = True
    if found_nans:
        print('!! Nans in ocean for variable:', variable_names[ivar]) 
        # You could loop over time to see where there are nans


f. close()

#---------------------------------------------------------------------------
# About the dataset
#---------------------------------------------------------------------------
# $ anemoi-datasets inspect ../datasets/norkystv3_hindcast_2024_surface.zarr
# 📦 Path          : ../datasets/norkystv3_hindcast_2024_surface.zarr
# 🔢 Format version: 0.30.0
# 
# 📅 Start      : 2024-01-01 00:00
# 📅 End        : 2024-12-31 23:00
# ⏰ Frequency  : 1h
# 🚫 Missing    : 0
# 🌎 Resolution : None
# 🌎 Field shape: [1148, 2747]
# 
# 📐 Shape      : 8,784 × 11 × 1 × 3,153,556 (1.1 TiB)
# 💽 Size       : 418.6 GiB (418.6 GiB)
# 📁 Files      : 8,890
# 
#    Index │ Variable                          │       Min │     Max │      Mean │    Stdev
#    ──────┼───────────────────────────────────┼───────────┼─────────┼───────────┼─────────
#        0 │ Uwind_eastward                    │    -28.02 │   34.87 │  0.312835 │  6.23567
#        1 │ Vwind_northward                   │    -29.44 │   28.97 │   1.31028 │  6.19878
#        2 │ h                                 │        10 │ 3259.61 │    399.75 │  745.999
#        3 │ salinity_-0.004903846153846154    │ -0.338001 │   36.23 │    34.159 │  2.07608
#        4 │ sea_mask                          │         0 │       1 │  0.577971 │ 0.493883
#        5 │ temperature_-0.004903846153846154 │    -3.565 │  21.845 │   8.75577 │  3.65528
#        6 │ u_eastward_-0.004903846153846154  │    -6.043 │   5.664 │ 0.0200142 │ 0.151678
#        7 │ ubar_eastward                     │    -5.548 │   5.205 │ 0.0148608 │ 0.126217
#        8 │ v_northward_-0.004903846153846154 │    -4.319 │   6.173 │ 0.0211188 │ 0.154488
#        9 │ vbar_northward                    │    -3.991 │   5.792 │ 0.0131414 │ 0.131907
#       10 │ zeta                              │     -3.85 │    2.41 │  -0.38284 │ 0.472634
#    ──────┴───────────────────────────────────┴───────────┴─────────┴───────────┴─────────
# 🔋 Dataset ready, last update the 2nd of this month.
# 📊 Statistics ready.
#---------------------------------------------------------------------------