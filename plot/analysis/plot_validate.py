
import matplotlib.pyplot as plt
import validate as v
import xarray as xr
import cmocean
import sys
from dataloader import open_dataset
import numpy as np

def plot_spectra(ds, output='figures/spectra.png'):
    vars = ['temperature', 'salinity', 'u_eastward', 'v_northward']
    P, K = v.power_spectra(ds, vars)

    fig, ax = plt.subplots(1,4, figsize=(20,7))
    for i in range(4):
        for j in range(len(ds.time)):
            ax[i].loglog(P[:-1, i, j], K[:-1, i, j], label=f't={j}', alpha=0.8)
            ax[i].set_title(vars[i])
            ax[i].legend(loc='lower left')
            ax[i].set_ylabel('P(k)', fontsize=14)
            ax[i].set_xlabel(r'$\lambda$ [km]', fontsize=14)
            ax[i].invert_xaxis()
    plt.savefig(output)

def plot_fields(ds, output='figures/mean.png'):

    fig, ax = plt.subplots(3, figsize=(10,20))
 
    c1 = ax[0].pcolormesh(ds.X, ds.Y, ds.temperature, cmap=cmocean.cm.thermal)
    c2 = ax[1].pcolormesh(ds.X, ds.Y, ds.salinity, cmap=cmocean.cm.haline )

    vel = v.absolute_vel(ds)
    c3 = ax[2].pcolormesh(ds.X, ds.Y, vel, cmap=cmocean.cm.speed)

    c=[c1,c2,c3]
    cb_title=[r'Temp [C$\circ$]', 'Salt', r'Vel [ms$^{-1}$]']
    for i in range(3):
        cax = fig.add_axes([ax[i].get_position().x1+0.01, ax[i].get_position().y0, 0.030, ax[i].get_position().height])
        cbar = fig.colorbar(c[i], ax=ax[i], cax=cax)
        cbar.ax.tick_params(labelsize=12)
        cbar.ax.set_title(cb_title[i], fontsize=12)
    
    plt.savefig(output)

def plot_difference(ds1, ds2, output='figures/diff.png'):
    fig, ax = plt.subplots(3, figsize=(10,20))

    c1 = ax[0].pcolormesh(ds1.X, ds1.Y, ds1.temperature-ds2.temperature, cmap='seismic', vmin=-1, vmax=1)
    c2 = ax[1].pcolormesh(ds1.X, ds1.Y, ds1.salinity-ds2.salinity, cmap='seismic', vmin=-3, vmax=3)

    vel1 = v.absolute_vel(ds1)
    vel2 = v.absolute_vel(ds2)
    c3 = ax[2].pcolormesh(ds1.X, ds1.Y, vel1-vel2, cmap='seismic', vmin=-0.1, vmax=0.1)

    c=[c1,c2,c3]
    cb_title=[r'Temp [C$\circ$]', 'Salt', r'Vel [ms$^{-1}$]']
    for i in range(3):
        cax = fig.add_axes([ax[i].get_position().x1+0.01, ax[i].get_position().y0, 0.030, ax[i].get_position().height])
        cbar = fig.colorbar(c[i], ax=ax[i], cax=cax)
        cbar.ax.tick_params(labelsize=12)
        cbar.ax.set_title(cb_title[i], fontsize=12)
    
    plt.savefig(output)


def plot_quiver(ds, output='figures/quiver.png'):
    import cartopy
    import cartopy.crs as ccrs
    fix, ax = plt.subplots(figsize=(10,10), dpi=200, subplot_kw={'projection': ccrs.PlateCarree()})
    s=10
    q = ax.quiver(ds.lon[::s, ::s], ds.lat[::s, ::s], ds.u_eastward[::s, ::s], ds.v_northward[::s, ::s], transform=ccrs.PlateCarree())
    ax.quiverkey(q, X=0.3, Y=1.05, U=0.5, label='Quiver key, length = 0.5', labelpos='E')
    ax.add_feature(cartopy.feature.LAND, edgecolor='black', zorder=1)
    plt.savefig(output)

def stream_plot(ds, output='figures/stream.png'):
    # Doesn't work
    import cartopy
    import cartopy.crs as ccrs
    fix, ax = plt.subplots(figsize=(10,10), dpi=200, subplot_kw={'projection': ccrs.PlateCarree()})
    s=10
    U = np.array(ds.u_eastward)
    V = np.array(ds.v_northward)
    U = np.ma.masked_invalid(U)
    V = np.ma.masked_invalid(V)
    lon = np.array(ds.lon)
    lat = np.array(ds.lat)
    lon = np.ma.masked_invalid(lon)
    lat = np.ma.masked_invalid(lat)
    ax.streamplot(lon, lat, U, V, transform=ccrs.PlateCarree())
    ax.add_feature(cartopy.feature.LAND, edgecolor='black', zorder=1)
    plt.savefig(output)
    
if __name__ == '__main__':
    #files = '/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_averages/norkyst800-202405_avg.nc'
    #ds = open_dataset(files).ds
    #plot_fields(ds, output='figures/mean_nk800.png')
#
    #ds = open_dataset(files, region='lofoten').ds
    #plot_fields(ds, output='figures/mean_nk800_lofoten.png')
    #plot_quiver(ds, output='figures/quiver_nk800_logoten.png')
    #
    #files = '/lustre/storeB/project/fou/hi/foccus/mateuszm/results/may2024/*'
    #ds = open_dataset(files, mean_axis='time').ds
    #plot_fields(ds, output='figures/havbris.png')
#
    #ds = open_dataset(files, mean_axis='time', region='lofoten').ds
    #plot_fields(ds, output='figures/mean_havbris_lofoten.png')
    #plot_quiver(ds, output='figures/quiver_havbris_logoten.png')
    #files = '/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_averages/norkyst800-202405_avg.nc'
    #ds1 = open_dataset(files).ds
    #files = '/lustre/storeB/project/fou/hi/foccus/mateuszm/results/may2024/*'
    #ds2 = open_dataset(files, mean_axis='time').ds
    #plot_difference(ds1, ds2)
    

    files = '/lustre/storeB/project/fou/hi/foccus/mateuszm/results/2024-05-01_744h_18d28_e011_s050000.nc'
    ds = open_dataset(files, mean_axis='time').ds
    plot_fields(ds, output='figures/mean_havbris_cont.png')
    files = '/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_averages/norkyst800-202405_avg.nc'
    ds1 = open_dataset(files).ds
    plot_difference(ds1, ds, output='figures/diff_cont.png')



