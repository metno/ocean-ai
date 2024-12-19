import xarray as xr
import plotly.express as px
import plotly.io as pio

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

dir = '/lustre/storeB/project/fou/hi/foccus/experiments/temp-jan/'
file = dir + '62677636-infer.nc'
ds_org = xr.open_dataset(file)

var_name = 'temperature_1'

# Get the subsetted dataset (Northern Norway here)
lon_min, lon_max = 11.83083, 15.59072
lat_min, lat_max = 67.41791, 69.20699
ds = subset_dataset(ds_org, lon_min, lon_max, lat_min, lat_max,var_name)
del ds_org

# Convert the dataset to a pandas DataFrame for easier handling with plotly
df = ds.to_dataframe().reset_index()

# Create the animated scatter plot
fig = px.scatter(
    df,
    x='longitude',
    y='latitude',
    animation_frame='time',
    animation_group='temperature_1',
    color='temperature_1',
    size_max=5,
    range_color=[df['temperature_1'].min(), df['temperature_1'].max()],
    title='Temperature Animation',
    labels={'temperature_1': 'Temperature'},
    color_continuous_scale='Viridis',
    width=800,
    height=600
)

# Update layout to include coastlines and geo projection
fig.update_geos(
    coastlinecolor="Black",
    showcoastlines=True,
    projection_type="equirectangular"
)
fig.update_layout(
    geo=dict(
        showcountries=True,
        showland=True,
        landcolor="lightgray"
    ),
    coloraxis_colorbar=dict(title='Temperature')
)

# Save the plot as an HTML file
pio.write_html(fig, file='temperature_animation.html')#, auto_open=True)

# Save the plot as a static image (requires orca or kaleido)
# pio.write_image(fig, file='temperature_animation.png')

# Show the plot
fig.show()