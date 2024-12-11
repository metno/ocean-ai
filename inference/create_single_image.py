# This code is inspired by aifs-support/visualization/animated_gif/create_single_image.py

import os
import sys
import numpy as np
import matplotlib.pylab as mpl
import argparse
#import verif.util
import netCDF4
import matplotlib
import cartopy
import cartopy.crs as ccrs
#import gridpp
import time
import datetime

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('file_era')
    parser.add_argument('file_meps')
    parser.add_argument('-o', help='Output file name', dest='ofilename')
    parser.add_argument('-lt', type=int, help='Leadtime', dest='leadtime', required=True)
    parser.add_argument('-c', help='Colormap', dest='colormap')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    s_time = time.time()

    edata = get(args.file_era, args.leadtime)
    mdata = get(args.file_meps, args.leadtime)
    print(f"{time.time() - s_time}: Done loading data")

    edges = [2, 5, 10, 13, 20, 25]
    edges = np.arange(2, 23, 2)
    edges = [0, 2, 4, 6, 8, 10, 13, 16, 19, 22]
    edges = [0, 3, 5, 7, 10, 13, 16, 19, 22, 25]
    edges = [0, 4, 8, 12, 16, 20, 22, 24, 28]
    edges = [0, 3, 6, 9, 12, 15, 18, 21, 24]
    gray = [0.7, 0.7, 0.7]
    contour_lw = 0.5
    levels = np.arange(950, 1050, 5)
    norm = matplotlib.colors.BoundaryNorm(edges, 256)
    show_coastline = True
    show_colorbar = True

    if args.colormap is None:
        cmap = "RdBu_r"
        cmap = "jet"
        cmap = "gist_ncar"
        # cmap = "gist_rainbow_r"
        # cmap = "BuPu"
        # cmap = "inferno"
        cmap = "turbo"
        # cmap = "cubehelix_r"

        cmap = get_cmap(cmap, minval=0.2, maxval=1) # 0.95)
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("my_cmap", ["#3c78d8", "#00ffff", "#38761d", "#ffff00", "red"])
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("my_cmap", ["white", "#3c78d8", "#00ffff", "#38761d", "#ffff00", "red"])
        cmap = matplotlib.colors.LinearSegmentedColormap.from_list("my_cmap", ["white", "#3c78d8",
            "#00ffff", "#008800", "#ffff00", "red"])
        # cmap = matplotlib.colors.LinearSegmentedColormap.from_list("my_cmap", ["white", "gray", "#38761d", "blue", "purple", "red"])
        # cmap = "BuPu"
        # cmap = "tab20c"
        # cmap = "rainbow"
    else:
        cmap = args.colormap

    regular = False
    # regular = True

    if regular:
        map = mpl.axes(projection=ccrs.PlateCarree())
        trans = None
    else:
        # map = mpl.axes(projection=ccrs.Stereographic(60, 15))
        # map = mpl.axes(projection=ccrs.RotatedPole(15, 60))
        # map = mpl.axes(projection=ccrs.LambertConformal(15, 63.3, standard_parallels=[63.3, 63.3]))
        map = mpl.gcf().add_axes([0, 0, 1, 1], projection=ccrs.LambertConformal(15, 63.3, standard_parallels=[63.3, 63.3]))

        # map = mpl.axes(projection=ccrs.NorthPolarStereo())
        trans = ccrs.PlateCarree()

    if show_coastline:
        map.coastlines(resolution='10m', zorder=20, linewidth=0.5)
        # map.coastlines(resolution='50m', zorder=20, linewidth=0.5)
    print(f"{time.time() - s_time}: Done coastlines")

    pargs = dict(cmap=cmap, norm=norm, transform=trans, alpha=1.0)
    cargs = dict(levels=levels, colors='b', linewidths=contour_lw, transform=trans)

    # Draw the global domain
    edata["air_pressure_at_sea_level"] = gridpp.neighbourhood(edata["air_pressure_at_sea_level"], 1, gridpp.Mean)
    mdata["air_pressure_at_sea_level"] = gridpp.neighbourhood(mdata["air_pressure_at_sea_level"], 1, gridpp.Mean)
    cm = map.pcolormesh(edata["lons"], edata["lats"], edata["wind_speed_10m"], zorder=-10, **pargs)
    # map.pcolormesh(edata["lons"], edata["lats"], edata["wind_speed_10m"], facecolor='none',
    #         edgecolor=gray, lw=0.1, transform=trans)
    map.contour(edata["lons"], edata["lats"], edata["air_pressure_at_sea_level"], zorder=-5, **cargs)

    # Draw a magenta box around the regional domain
    map.pcolormesh(mdata["lons"], mdata["lats"], mdata["wind_speed_10m"], facecolors='none', edgecolor='m', lw=3, transform=trans)

    # Draw the regional domain
    map.pcolormesh(mdata["lons"], mdata["lats"], mdata["wind_speed_10m"], **pargs)
    # print(np.mean(mdata["air_pressure_at_sea_level"]))
    map.contour(mdata["lons"], mdata["lats"], mdata["air_pressure_at_sea_level"], **cargs)
    if regular:
        map.set_extent([-65, 55, 30, 72], ccrs.PlateCarree())
    else:
        # map.set_extent([-65, 55, 30, 50], ccrs.PlateCarree())
        map.set_extent([-45, 55, 40, 70], ccrs.PlateCarree())

    if regular:
        mpl.gca().set_aspect(2)
    leadtime = args.leadtime * 6

    time_string = unixtime_to_string(edata["forecast_reference_time"])
    label = f"{time_string} forecast lead time: {leadtime:d}h"

    time_string = unixtime_to_string(edata["time"][args.leadtime])
    label = f"{time_string}"

    # mpl.text(-43, 75, label, backgroundcolor='white')
    mpl.text(0.01, 0.025, label, fontsize=8, transform=mpl.gca().transAxes, color="w", backgroundcolor='k', zorder=30)

    # mpl.text(0.015, 0.025, "Streched-grid AIFS (1° global, 10km regional)", transform=mpl.gca().transAxes, color="w", backgroundcolor='k', zorder=30)
    print(f"{time.time() - s_time}: Done plotting")

    if show_colorbar:
        cax = map.inset_axes([1.01, 0, 0.02, 1.0])
        cbar = mpl.colorbar(cm, cax, extend="max")
        cbar.set_label(label="10m wind speed (m/s)", fontsize=8) # weight='bold', 

        for t in cbar.ax.get_yticklabels():
             t.set_fontsize(8)


    # This removes the black border of the map
    # map.spines['geo'].set_edgecolor('white')


    if args.ofilename is not None:
        # mpl.gcf().set_size_inches(10, 6)
        # mpl.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
        mpl.savefig(args.ofilename, bbox_inches='tight', dpi=200)
    else:
        mpl.show()
    print(f"{time.time() - s_time}: Done")


def get(filename, leadtime):
    data = dict()
    with netCDF4.Dataset(filename) as file:
        lats = file.variables["latitude"][:]
        lons = file.variables["longitude"][:]
        if len(lats.shape) == 1:
            lons, lats = np.meshgrid(lons, lats)
            # lons = lons.transpose()
            # lats = lats.transpose()
        data["lats"] = lats
        data["lons"] = lons
        data["forecast_reference_time"] = file.variables["time"][0]
        data["time"] = file.variables["time"][:]
        x = file.variables["x_wind_10m"][leadtime, 0, ...]
        y = file.variables["y_wind_10m"][leadtime, 0, ...]
        data["wind_speed_10m"] = np.sqrt(x**2 + y**2)
        if "air_pressure_at_sea_level" in file.variables:
            data["air_pressure_at_sea_level"] = file.variables["air_pressure_at_sea_level"][leadtime, 0, ...] / 100
        else:
            print("Missing air_pressure_at_sea_level")
            data["air_pressure_at_sea_level"] = np.zeros(x.shape, np.float32)

    return data


def get_cmap(name, minval=0.0, maxval=1.0, n=100):
    # cmap[:,0:3] *= 0.5 + 0.5
    # from matplotlib.colors import ListedColormap
    # cmap = ListedColormap(cmap)

    # cmap = mpl.cm.get_cmap(name, 256)
    cmap = mpl.colormaps[name]
    import matplotlib.colors as colors
    new_cmap = colors.LinearSegmentedColormap.from_list( 'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval), cmap(np.linspace(minval, maxval, n)))
    return new_cmap

    if 0:
        colors = []
        for ind in range(cmap.N):
            c = []
            for x in cmap(ind)[:3]:
                c.append(x*0.5 + 0.5)
            colors.append(tuple(c))
        cmap = matplotlib.colors.ListedColormap(colors, name = 'my_name')

def unixtime_to_string(unixtime):
    """Convert unixtime to YYYYMMDDTHHMMSSZ

    Args:
       unixtime (int): unixtime [s]

    Returns:
       string: timestamp in YYYYMMDDTHHMMSSZ
    """

    if(unixtime is None):
        return None
    else:
        dt = datetime.datetime.utcfromtimestamp(int(unixtime))
        date = dt.year * 10000 + dt.month * 100 + dt.day
        return "%04d/%02d/%02d %02dZ" % (dt.year, dt.month, dt.day, dt.hour)


if __name__ == "__main__":
    main()