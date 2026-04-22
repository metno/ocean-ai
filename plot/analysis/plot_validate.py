
import matplotlib.pyplot as plt
import validate as v
import xarray as xr
import cmocean
import sys
from dataloader import open_dataset

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

def plot_temporal_mean(ds, output='figures/mean.png'):
    ds = v.temporal_mean(ds)
    vars = ['temperature', 'salinity', 'u_eastward', 'v_northward']

    fig, ax = plt.subplots(3, figsize=(10,20))

    c1 = ax[0].pcolormesh(ds.Y, ds.X, ds.temperature, cmap=cmocean.cm.thermal)
    c2 = ax[1].pcolormesh(ds.Y, ds.X, ds.salinity, cmap=cmocean.cm.haline)

    vel = v.absolute_vel(ds)
    c3 = ax[2].pcolormesh(ds.Y, ds.X, vel, cmap=cmocean.cm.speed)

    c=[c1,c2,c3]
    cb_title=[r'Temp [C$\circ$]', 'Salt', r'Vel [ms$^{-1}$]']
    for i in range(3):
        cax = fig.add_axes([ax[i].get_position().x1+0.01, ax[i].get_position().y0, 0.030, ax[i].get_position().height])
        cbar = fig.colorbar(c[i], ax=ax[i], cax=cax)
        cbar.ax.tick_params(labelsize=12)
        cbar.ax.set_title(cb_title[i], fontsize=12)
    
    plt.savefig(output)
    
if __name__ == '__main__':
    files = '/lustre/storeB/project/fou/hi/foccus/mateuszm/results/may2024/*'
    ds = open_dataset(files).ds
    #plot_temporal_mean(ds)
    files = '/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/norkyst800-202405*'
    ds = open_dataset(files, depth=-1).ds
    plot_temporal_mean(ds, output='figures/mean_nk800.png')