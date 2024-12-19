
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib as mpl

dir = '/lustre/storeB/project/fou/hi/foccus/ina/OceanAI/training/outputs/experiment1/'
file = dir + '7e296243.nc'
ds = xr.open_dataset(file)

print(ds.longitude)

fig = plt.figure(figsize=(20,20))
ax = plt.axes()

c = ax.scatter(ds.longitude,ds.latitude,c=ds.isel(time=0)['temperature_1'],s=5)

plt.show()