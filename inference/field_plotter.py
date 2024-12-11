# This code is inspired by anemoi-utils/anemoi-utils/field_plotter.py

import cartopy.crs as ccrs
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from data import get_data, get_era5_data, read_era5
from utils import mesh, panel_config_auto, interpolate, plot
from map_keys import map_keys

plt.rcParams["font.family"] = "serif"


def field_plotter(
        time: str or pd.Timestamp,
        fields: list[str] or str,
        path: str,
        file_era: str = None, 
        lead_times: list[int] or int = 0,
        ens_size: int = None,
        plot_ens_mean: bool = False,
        norm: bool = False,
        xlim: tuple[float] = None,
        ylim: tuple[float] = None,
        resolution: float = None,
        freq: str ='6h',
        **kwargs,
    ) -> None:
    """Plot ensemble field and potentially compare to ERA5.

    Args:
        time: str or pd.Timestamp
            Specify a time stamps to be plotted
        fields: list[str] or str
            Specify one or multiple fields to be verified. Currently supports
            air_temperature_2m, wind_speed_10m, precipitation_amount_acc6, air_sea_level_pressure
        path: str
            Path to directory where files to be analysed are found. 
            (maybe add information about NetCDF format and folder structure?)
        file_era: str
            ERA5 analysis file to be compared to. Not included by default.
        lead_times: list[int] or int
            One or multiple lead times to be plotted
        ens_size: int
            Number of ensemble members to include
        plot_ens_mean: bool
            Whether or not to plot ensemble mean.
        norm: bool
            Whether or not to normalize plots. In particular used with precipitation.
        xlim: tuple[float]
            xlim used in panels. No limit by default
        ylim: tuple[float]
            ylim used in panels. No limit by default
        resolution: float
            Resolution in degrees used in interpolation. Using 1 for o96 and 0.25 for n320 by default.
        freq: str
            Frequency of lead times. Supports pandas offset alias: 
            https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases
    """
    fields = np.atleast_1d(fields)
    lead_times = np.atleast_1d(lead_times)

    if isinstance(time, str):
        time = pd.Timestamp(time)

    # get (ensemble) data
    ds = get_data(path, time, ens_size)
    if resolution is None:
        resolution = 0.25 if ds[fields[0]].shape[-1] == 542080 else 1
    lat_grid, lon_grid = mesh(ds.latitude, ds.longitude, resolution) 

    # ERA5
    include_era = False if file_era is None else True
    if include_era:
        ds_era5 = read_era5(fields, file_era, [time], max(lead_times)+1, freq=freq)
        data_era5 = get_era5_data(ds_era5, 0, fields, max(lead_times)+1)
        lat_grid_era, lon_grid_era = mesh(ds_era5.latitudes, ds_era5.longitudes, resolution)

    n, ens_size = panel_config_auto(ens_size, include_era + plot_ens_mean)
    
    for field in fields:
        units = map_keys[field]['units']
        for lead_idx, lead_time in enumerate(lead_times):
            # find vmin and vmax
            vmin = ds[field][:,lead_idx].min()
            vmax = ds[field][:,lead_idx].max()
            if include_era:
                vmin = min(vmin, data_era5[field][lead_time].min())
                vmax = max(vmax, data_era5[field][lead_time].max())
            cen = (vmax-vmin)/10.
            vmin += cen
            vmax -= cen
            if norm:
                boundaries = np.logspace(0.001, np.log(0.03*vmax), cmap.N-1)
                boundaries = [0.0, 0.5, 1, 2, 4, 8, 16, 32]
                norm = matplotlib.colors.BoundaryNorm(boundaries, cmap.N, extend='both')
                kwargs['norm'] = norm
            else:
                kwargs['vmin'] = vmin
                kwargs['vmax'] = vmax
            kwargs['shading'] = 'auto'

            fig, axs = plt.subplots(*n, figsize=(8,6), squeeze=False, subplot_kw={'projection': ccrs.PlateCarree()})
            
            # member panel(s)
            k = 0
            for i in range(n[0]):
                for j in range(n[1]):
                    data = ds[field][k, lead_idx]
                    if data.ndim == 1:
                        data = interpolate(data, ds.latitude, ds.longitude, resolution)

                    # plot
                    im = plot(axs[i,j], data, lat_grid, lon_grid, **kwargs)
                    axs[i,j].set_title(f"Member {k}")
                    axs[i,j].set_xlim(xlim)
                    axs[i,j].set_ylim(ylim)
                    k += 1
                    if k >= ens_size:
                        break
                else:
                    continue
                break

            # extra panels
            if plot_ens_mean:
                data = ds[field][:,lead_idx].mean(axis=0)
                if data.ndim == 1:
                    data = interpolate(data, ds.latitude, ds.longitude, resolution)
                sec_last_ax = axs[n[0]-1, n[1]-2]
                im = plot(sec_last_ax, data, lat_grid, lon_grid, **kwargs)
                sec_last_ax.set_title("Ensemble mean")
                sec_last_ax.set_xlim(xlim)
                sec_last_ax.set_ylim(ylim)

            if include_era:
                data = data_era5[field][lead_time]
                data = interpolate(data, ds_era5.latitudes, ds_era5.longitudes, resolution)
                last_ax = axs[n[0]-1, n[1]-1]
                im = plot(last_ax, data, lat_grid_era, lon_grid_era, **kwargs)
                last_ax.set_title("ERA5")
                last_ax.set_xlim(xlim)
                last_ax.set_ylim(ylim)

            # show plot
            lead_time_hours = int(freq[:-1]) * lead_time
            fig.suptitle(field + f" + {lead_time_hours}h")
            plt.tight_layout()
            cbax = fig.colorbar(im, ax=axs.ravel().tolist())
            cbax.set_label(f"{field} ({units})")
            plt.show()

if __name__ == "__main__":
    import matplotlib

    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("my_cmap", ["white", "white", "#3c78d8", "#00ffff", "#008800", "#ffff00", "red"])

    field_plotter(
        time="2022-01-13T00", 
        fields='wind_speed_10m', 
        path="/pfs/lustrep3/scratch/project_465000454/anemoi/experiments/ni1_b_new/inference/epoch_010/predictions/", 
        file_era="/pfs/lustrep3/scratch/project_465000454/anemoi/datasets/ERA5/aifs-ea-an-oper-0001-mars-n320-1979-2022-6h-v6.zarr", 
        lead_times=[10,40], 
        ens_size=2,
        plot_ens_mean=True,
        cmap='turbo',
        norm=False,
        xlim=(-65,30),
        ylim=(20,75),
    )
