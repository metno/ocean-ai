import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def subset_dataset(ds, lon_min, lon_max, lat_min, lat_max, var_name='temperature_1'):
    """
    Subsets the dataset to the specified longitude and latitude range,
    and returns a new dataset containing only the longitude, latitude,
    and temperature_1 variables.
    
    Parameters:
    ds (xarray.Dataset): The input dataset.
    lon_min (float): Minimum longitude.
    lon_max (float): Maximum longitude.
    lat_min (float): Minimum latitude.
    lat_max (float): Maximum latitude.
    var_name (string): Name of the variable to select a subset of. 
    
    Returns:
    xarray.Dataset: The subsetted dataset.
    """
    # Extract longitude, latitude, and temperature_1 variables
    longitude = ds['longitude'].values
    latitude = ds['latitude'].values
    var = ds[var_name].values

    # Create a mask for the bounding box
    lon_mask = (longitude >= lon_min) & (longitude <= lon_max)
    lat_mask = (latitude >= lat_min) & (latitude <= lat_max)
    
    # Combine masks
    combined_mask = lon_mask & lat_mask
    
    # Apply the mask to filter the data
    filtered_longitude = longitude[combined_mask]
    filtered_latitude = latitude[combined_mask]
    filtered_var = var[:, combined_mask]

    # Create a new dataset with the filtered data
    subset_ds = xr.Dataset({
        'longitude': (['values'], filtered_longitude),
        'latitude': (['values'], filtered_latitude),
        'temperature_1': (['time', 'values'], filtered_var)
    }, coords={
        'time': ds['time'].values
    })

    return subset_ds

# Load the dataset
dir = '/lustre/storeB/project/fou/hi/foccus/experiments/temp-jan/'
file = dir + '62677636-infer.nc'
ds_org = xr.open_dataset(file)

var_name = 'temperature_1'

# Get the subsetted dataset (Northern Norway here)
lon_min, lon_max = 11.83083, 15.59072
lat_min, lat_max = 67.41791, 69.20699
ds = subset_dataset(ds_org, lon_min, lon_max, lat_min, lat_max,var_name)

# Create a figure and axis with coastlines
fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
ax.coastlines()
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.LAND, edgecolor='black')
ax.add_feature(cfeature.LAKES, edgecolor='black')
ax.add_feature(cfeature.RIVERS)

# Initialize the scatter plot
sc = ax.scatter(ds.longitude, ds.latitude, c=ds.isel(time=0)['temperature_1'], s=5, cmap='viridis')

# Add a colorbar
cbar = plt.colorbar(sc, ax=ax, orientation='vertical', label='Temperature')

# Update function for animation
def update(frame):
    sc.set_array(ds.isel(time=frame)['temperature_1'].values)
    ax.set_title(f'Time step: {frame}')
    return sc,

# Create animation
ani = FuncAnimation(fig, update, frames=range(48), blit=True, interval=200)

# Save the animation as a GIF (optional)
#ani.save('temperature_animation.gif', writer='imagemagick')

# Show the plot
plt.show()