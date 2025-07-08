# TODO: use functions from ocean-ai/plot to make better plots

import xarray as xr
import matplotlib.pyplot as plt
import matplotlib as mpl

dir = '/lustre/storeB/project/fou/hi/foccus/experiments/lam-nothin-res10-2024-cloud/inference/'
#file = dir + 'lam48.nc'
file = 'lam48.nc'
ds = xr.open_dataset(file)

print(ds.longitude)

fig = plt.figure(figsize=(20,20))
ax = plt.axes()

c = ax.scatter(ds.longitude,ds.latitude,c=ds.isel(time=0)['temperature_0'],s=5)

plt.show()