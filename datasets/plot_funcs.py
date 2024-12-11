import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs

def plot_dataset(zda, var_name, indx_time=0): #, cmin=10, cmax=-2):
    # The data are defined in lat/lon coordinate system, so PlateCarree()
    # is the appropriate choice:
    data_crs = ccrs.PlateCarree()

    proj = ccrs.LambertConformal(
            central_longitude=30, 
            central_latitude=67.9
            )

    # Set up projection and plot
    fig = plt.figure(figsize=(20,20))
    ax = plt.axes(projection=proj)
    ax.coastlines()
    print("hello2")


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


