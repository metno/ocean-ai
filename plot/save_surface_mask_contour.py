# Make a file which contains the the land-sea mask as contour 
# lines ready to be plotted (faster than loading surface_mask.nc for each plot).

# Author: Ina B. Kullmann, 2024

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

# Load the input file
file='/lustre/storeB/project/fou/hi/foccus/datasets/surface_mask.nc'
ds = xr.open_dataset(file)
lat_norway = ds.lat.values
lon_norway = ds.lon.values
mask_norway = ds.isel(time=0).land_binary_mask.values

# Get the contour lines
# levels=[0] sets the contour path exactly at the outermost land points. 
# Use levels=[0.5] to set the line exactly between the land and sea points
contour = plt.contour(lon_norway, lat_norway, mask_norway, levels=[0])

# Extract contour paths
contour_paths = []
for segs in contour.allsegs:
    for seg in segs:
        contour_paths.append(seg)

# Save the contour paths to a .npy file
dir_save = '/lustre/storeB/project/fou/hi/foccus/ina/ocean-ai/plot/'
np.save(dir_save + 'surface_mask_contour_paths.npy', np.array(contour_paths, dtype=object), allow_pickle=True)

"""
The contour lines can now be loaded and used like this:

#######################################
# Load contour paths from the .npy file

contour_loaded = np.load(dir_save + 'surface_mask_contour_paths.npy', allow_pickle=True)

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(lon_norway, lat_norway, c=mask_norway)

# Plot each contour path
for vertices in contour_loaded:
    ax.plot(vertices[:, 0], vertices[:, 1], color='red',linewidth=0.5,linestyle=':'

# Add labels and a title
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Land-Sea Border')
plt.show()
"""