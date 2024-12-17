import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs
import cartopy.feature as cfeature
#import anemoi.datasets as ad

def simple_mesh_plot(lon_grid, lat_grid, var_grid, time,var_name='temperature'):
    # TODO: add options for **kwargs
    kwargs = {}
    kwargs['shading'] = 'auto' #kwargs['vmin'] = vmin; kwargs['vmax'] = vmax #se også på norm
    kwargs['cmap'] = 'viridis'

    fig, ax = plt.subplots(figsize=(8, 6),squeeze=False, subplot_kw={'projection': ccrs.PlateCarree()})
    ax1=ax[0,0]
    ax1.add_feature(cfeature.COASTLINE)
    ax1.add_feature(cfeature.BORDERS, linestyle=':')
    ax1.add_feature(cfeature.LAND, edgecolor='black')
    
    heatmap = ax1.pcolormesh(lon_grid, lat_grid, var_grid, **kwargs)
    # TODO improve this cbar and fig size etc
    #cbar = fig.colorbar(heatmap, ax=ax1, orientation='vertical')
    #cbar.set_label(var_name)
    ax1.set_title(f'Time step: {time}')

    return fig, ax1, heatmap#, cbar

def update_anim(frame,ax,heatmap,var,time):
    heatmap.set_array(var[frame].ravel())
    ax.set_title(f'Time step: {time[frame]}')

def subset_dataset(zda, lon_min, lon_max, lat_min, lat_max, ntime=12, var_name='temperature_1'):
    """
    Subsets the dataset to the specified longitude and latitude range,
    and returns a new dataset containing only the longitude, latitude,
    and temperature_1 variables.
    
    Parameters:
    ds (anemoi.datasets): The input dataset.
    lon_min (float): Minimum longitude.
    lon_max (float): Maximum longitude.
    lat_min (float): Minimum latitude.
    lat_max (float): Maximum latitude.
    var_name (string): Name of the variable to select a subset of. 
    
    Returns:
    ...
    """
    # Extract longitude, latitude, and var
    longitude = zda.longitudes
    latitude = zda.latitudes

    # Create a mask for the bounding box
    lon_mask = (longitude >= lon_min) & (longitude <= lon_max)
    lat_mask = (latitude >= lat_min) & (latitude <= lat_max)
    
    # Combine masks
    combined_mask = lon_mask & lat_mask
    
    # Apply the mask to filter the data
    filtered_longitude = longitude[combined_mask]
    filtered_latitude = latitude[combined_mask]
    
    indx_var = zda.name_to_index[var_name]
    var = zda[:ntime,indx_var,0,:]
    filtered_var = var[:, combined_mask]

    return filtered_var,filtered_latitude,filtered_longitude

def plot_dataset(zda, var_name, indx_time=0): #, cmin=10, cmax=-2):
    # The data are defined in lat/lon coordinate system, so PlateCarree()
    # is the appropriate choice:
    """zda is a zarr file opened with anemoi datasets..."""
    data_crs = ccrs.PlateCarree()

    proj = ccrs.LambertConformal(
            central_longitude=30, 
            central_latitude=67.9
            )

    # Set up projection and plot
    fig = plt.figure(figsize=(20,20))
    ax = plt.axes(projection=proj)
    ax.coastlines()

    # Get the index of the variable and the variable itself
    indx_var = zda.name_to_index[var_name]
    var = zda[indx_time][indx_var,0,:] # we set ensemble=0 and take all grid points (last dimension)
    var_min = zda.statistics['minimum'][indx_var] 
    var_max = zda.statistics['maximum'][indx_var]

    # Scatter plot
    c = ax.scatter(zda.longitudes, zda.latitudes, var, c=var, transform=data_crs, edgecolor=None, vmax=var_max, vmin=var_min)

    # Set up gridlines
    gl = ax.gridlines(data_crs, draw_labels=True,
                      linewidth=2, color='gray', alpha=0.5, linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_right = False

    # Adjust subplot params
    plt.subplots_adjust(left=None, bottom=None, right=0.75, top=0.8, wspace=0.1, hspace=0.3)

    # Create colorbar
    cax,kw = mpl.colorbar.make_axes(ax, location='right', pad=0.05, shrink=0.7)
    plt.colorbar(c, cax=cax, extend='both', extendrect=False, label=(f'{var_name} (Norkyst v3)'), **kw)

    # Show the plot
    plt.show()

    return fig


#----
# Testing

if __name__ == "__main__":

    import anemoi.datasets as ad
    print("hello")

    zda = ad.open_dataset('../data/norkyst_v3_2024_01_01.zarr')

    fig = plot_dataset(zda, 'temperature_1000')
    #plt.show()


