# Authors: Ina Kullmann (Nov/Dec 2024)

# Script to preprocess data before using anemoi-datasets.
# Find all nans that are not below seafloor or land (i.e. in the ocean) and impute them.
# Save result to .nc

# Required: a seafloor mask for all layers, see code [..] (TODO: add codename here)

# The code will use an interpolation method (nearest neighbor/linear) to impute the nan values in the ocean. 
# These nan values may be dynamic, i.e. move in time. 
# NOTE: the linear interpolation method did not manage to remove all nans, thus it is not recomended. 

# TODO: document better

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
import time as pytime
#import dask.array as da
import sys

# -----------------------------------------------------

def get_test_data(ds, nlon=6, nlat=6, ndepth=2, ntime=48,random=True):
    """
    Creating sample data for testing.
    Using a subset of the lon and lat values from the input dataset ds, 
    but no actual parameter values. Also using a sample sea-land mask.

    Returning a matrix of one parameter, that will contains:
        random=False : constant 1 everywhere but at the second depth layer which is 2
        random=True  : random values between (0,1) everywhere 

    NOTE: two nan values are added inside the ocean domain AND
          wherever the sea-land mask is False to test the imputation method
    """

    # Select the domain as a subset
    lon = ds.lon.values[:nlon,:nlat]
    lat = ds.lat.values[:nlon,:nlat]
    #depth = ds.depth.values[:ndepth]
    #time = np.arange('2024-01-01', '2024-01-03', dtype='datetime64[h]').astype('datetime64[ns]')

    # -----------------------------------------------------
    # Create a mask array which will be True over the ocean
    land_sea_mask = np.zeros([ndepth, nlon, nlat], dtype=bool)
    base_ocean_mask = np.array([
        [0, 0, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1],
        [1, 1, 1, 0, 0, 0],
        [1, 1, 0, 0, 0, 0]
    ], dtype=bool)

    # Check if the base ocean mask needs to be expanded
    if base_ocean_mask.shape[0] < nlon or base_ocean_mask.shape[1] < nlat:
        # Calculate the padding needed in each dimension
        padding = ((0, nlon - base_ocean_mask.shape[0]), (0, nlat - base_ocean_mask.shape[1]))
        base_ocean_mask = np.pad(base_ocean_mask, pad_width=padding, constant_values=False)
    elif base_ocean_mask.shape[0] > nlon or base_ocean_mask.shape[1] > nlat:
        raise ValueError("The values of nlon and nlat must be >=6")

    # Set the mask for the surface layer
    land_sea_mask[0] = base_ocean_mask

    # Create a modified mask for the depth layers
    depth_mask = base_ocean_mask.copy()
    depth_mask[5, 1] = False  # More land at this point

    # Set the mask for the depth layers
    land_sea_mask[1:] = depth_mask

    # -----------------------------------------------------
    # Creating two sample variables
    if random:
        var = np.random.rand(ntime, ndepth, nlat, nlon)
    else:
        var = np.ones([ntime, ndepth, nlat, nlon])  # Constant 1
        var[:,1] = 2*np.ones([nlat, nlon])          # Constant 2 at idept=1

    # Add two nans at some first and 15th time step, 0th and 1st depth layer
    var[0,0,2,2]  = np.nan #pos. in the center, ocean around
    var[0,0,2,2]  = np.nan 
    var[15,1,4,2] = np.nan #pos. in ocean but at edge
    var[15,1,4,2] = np.nan 
    # -----------------------------------------------------
    print("\nShape of var matrix is: \n(Ntime,Ndepth,Nlon,Nlat)=",var.shape,"\n")

    # Set nan also where there is land, as in the actual data
    var = np.where(land_sea_mask,var, np.nan)

    return var, land_sea_mask, lon, lat

def plot_nan_at_layers(var,land_sea_mask,lon,lat,idepth,itime=0):
    """
    input:
        var : np.array, 4D variable want to plot nans of
        land_sea_mask : np.array, 3D bool values where True is the ocean 
        lon : np.array, 2D longitude values for var
        lat : np.array, 2D latitude values for var
        idepth : int, index number of depth layer, second dim. of var
        itime : int, index number for time dimension, first dim of var
    
    returns:
        None

    """

    sea_mask = ~land_sea_mask[idepth] # This picks out ocean (True for ocean)
    ocean_slice = var[itime, idepth][sea_mask] # gets a 1D (flat) array e.g. (6371,)

    mask_nan_ocean = np.isnan(ocean_slice)

    plt.title(f"ocean=blue, NaN=red for var at idepth={idepth}")
    plt.scatter(lon[sea_mask],lat[sea_mask],ocean_slice,c='b')
    plt.scatter(lon[sea_mask][mask_nan_ocean],lat[sea_mask][mask_nan_ocean],c='r')
    plt.show() 

    return

def impute_layer(var,land_sea_mask,lon,lat,idepth,itime,method='linear',plot=False):
    """ 
    Impute METHOD 1 & 2
    input:

    

    NOTE: this code does not handle the case where all values in a 2D slice are NaN. 
          You might need to add additional checks or fallbacks for such cases.
    """
    #t0 = pytime.time()

    # Get only values in the ocean for one depth and time step
    sea_mask = ~land_sea_mask[idepth] 
    ocean_slice = var[itime, idepth][sea_mask] # get a 1D (flat) array e.g. (6371,)

    # Get True where nan in ocean domain
    mask_nan_ocean = np.isnan(ocean_slice) # e.g. (6371,)

    # Only do calc. if nan in ocean
    if mask_nan_ocean.any():
        #print(f"itime={itime}, idepth={idepth}, nr.nans={np.sum(mask_nan_ocean)}")

        # Need to reshape grid from 2D to 1D to use scipy interpolate 
        # First, get a grid of ocean values whithout nan (x,y,z)
        x = lon[sea_mask][~mask_nan_ocean] # (6360,)
        y = lat[sea_mask][~mask_nan_ocean]
        z = ocean_slice[~mask_nan_ocean] # Note that sea_mask has been applied already
        # Combine x, y into single array
        points = np.array([x, y]).T # (6360, 2)

        # Initiate interpolator at points where are not nan in ocean
        if method == 'linear':
            interp_func = interpolate.LinearNDInterpolator(points, z) 
        elif method == 'nearest':
            interp_func = interpolate.NearestNDInterpolator(points, z)
        else:
            raise ValueError(f"No method called {method}, use method=\'linear\' or \'nearest\' in function call.")

        # Get the points where we want to interpolate (only nan values)
        x_interp = lon[sea_mask][mask_nan_ocean] # (nr.nan,)
        y_interp = lat[sea_mask][mask_nan_ocean]
        points_interp = np.array([x_interp, y_interp]).T # (nr.nan,2)

        # Need to keep track of the indices
        ind = np.array([(i, j) for i in range(lon.shape[0]) for j in range(lon.shape[1])])
        ind = ind.reshape(lon.shape[0], lon.shape[1], 2)
        # Get array of indices where nan in ocean 
        ind_nan = ind[sea_mask][mask_nan_ocean]

        # Interpolate data
        z_interp = interp_func(points_interp)

        # Put interpolated values back into original array
        i_nan, j_nan = ind_nan.T
        var[itime,idepth,i_nan,j_nan] = z_interp
    
        #print("Impute time: ", pytime.time()-t0)
        
        # Any nan left? Plot if yes
        #m_nan = np.isnan(z_interp)
        #if m_nan.any(): plot=True

        if plot:
            plt.figure(figsize=(8, 6))
            plt.title('Data with NaN values (NaN=red)')
            plt.scatter(lon[sea_mask],lat[sea_mask],c=ocean_slice,s=20)
            plt.scatter(x_interp,y_interp,c='r',marker='x',s=20)
            
            plt.figure(figsize=(8, 6))
            plt.title('Data after Interpolation')
            plt.scatter(lon[sea_mask],lat[sea_mask],c=ocean_slice,s=20)
            plt.scatter(lon[i_nan,j_nan],lat[i_nan,j_nan],c=var[itime,idepth,i_nan,j_nan],s=20,edgecolors='m',linewidths=1)

            m_nan = np.isnan(z_interp)
            if m_nan.any():
                ind_still_nan = ind_nan[m_nan]
                i, j = ind_still_nan.T
                plt.scatter(lon[i,j],lat[i,j],c='r',marker='x')

            plt.colorbar(label='var') # since no norm given all data put in range [0,1]
            plt.show()
    #else: 
    #    print(f"No NaN in layer idepth={idepth}")

    return var

def impute_variable(var,land_sea_mask,lon,lat,method='linear',plot=False):


    for itime in range(var.shape[0]):
        #t2 = pytime.time()
        for idepth in range(var.shape[1]):
            # Remove dynamic NaNs in the ocean (where land_sea_mask is True) 
            # TODO: test both methods ('linear', 'nearest'), 
            # assume nearest is much faster (and fixes more nans) but linear better quality?
            var = impute_layer(var,land_sea_mask,lon,lat,idepth,itime,method,plot)

            # TODO: old version, still works or not?
            #impute_using_griddata(data_matrix,land_sea_mask) # time 
        
        #print(f"\n------\nCalculation time (1h): {pytime.time()-t2}s \n------\n")

    return var

def impute_using_griddata(var_matrix,land_sea_mask):
    """ Impute METHOD 2 """
    # TODO remove later?

    # Creating a mask of valid ocean values (non-NaN and non-land)
    # same shape as var_matrix
    valid_mask = np.logical_and(~np.isnan(var_matrix), land_sea_mask)

    # Preparing the points and values for griddata
    # scipy.interpolate.griddata() only works with 1D array, 
    # need to flatten the arrays and afterwards reshape them back to the original shape.
    points = np.array(np.nonzero(valid_mask)).T # shape og (4894,5) which are total number of valid data points np.sum(valid_mask) and ndims=5 of data_matrix
    values = var_matrix[valid_mask] # (4894,) contains valid data points from var_matrix

    t0 = pytime.time()

    # Interpolating missing values
    ntime=var_matrix.shape[0]; ndepth=var_matrix.shape[1]
    nlon =var_matrix.shape[2]; nlat =var_matrix.shape[3]
    for j in range(ndepth):
        for k in range(nlon):
            for l in range(nlat):
                for m in range(ntime):
                    if np.isnan(var_matrix[m, j, k, l]) and land_sea_mask[j, k, l]:
                        grid_z = np.array([m, j, k, l])
                        var_matrix[m, j, k, l] = interpolate.griddata(points, values, grid_z, method='nearest')[0]

    print("Impute calculation time: ", pytime.time()-t0)

    return var_matrix

def get_data_matrix_from_ds(ds, variable_list=['temperature', 'salinity']):
    """
    Get all relevant variables and store them in a numpy matrix.
    """
    # TODO remove this when done cleaning up
    
    nlon = ds['lon'].shape[-2]
    nlat = ds['lat'].shape[-1]
    ntime = ds['time'].shape[0]
    ndepth = ds['depth'].shape[0]

    data_matrix = np.empty((len(variable_list),ntime,ndepth,nlon,nlat))
    for n,variable in enumerate(variable_list):
        data_matrix[n] = ds[variable].values

    return data_matrix

def init_dataset(ds,lon,lat,X,Y):
    # Define a dataset to store the results in
    ds_new = xr.Dataset(
        coords = dict(
                X=(['X'], X, ds.X.attrs),
                Y=(['Y'], Y, ds.Y.attrs),
                depth=(['depth'], ds.depth.values, ds.depth.attrs),
                time=(['time'], ds.time.values,ds.time.attrs)
        ),
        data_vars = dict(
            lon=(['Y', 'X'], lon, ds.lon.attrs),
            lat=(['Y', 'X'], lat, ds.lon.attrs)
        ),
        attrs=ds.attrs # to include global attributes from original file
    )
    ds_new['projection_stere'] = ds.projection_stere
    ds_new['h'] = (['Y', 'X'], ds.h.values, ds.h.attrs)

    return ds_new

def get_subset(ds,land_sea_mask,varname='temperature',time_steps=[0,1,2],imax_depth=16,index_range=[1850,2000,600,700]):
    """
    Get a subset of the data that easily fits into memory.
    
    time_steps : list of time steps to retrieve

    """
    ndepth = ds[varname].shape[1]
    if ndepth < imax_depth: 
        imax_depth = ndepth #TODO: remove when norkyst files dont change anymore
    
    if imax_depth < ndepth:
        # select depth range
        idepths = [i for i in range(imax_depth)]
        var = ds.isel(time=time_steps,depth=idepths)[varname].values
    else:
        var = ds.isel(time=time_steps)[varname].values

    # Get the subset
    ilon_min = index_range[0]; ilon_max = index_range[1]
    ilat_min = index_range[2]; ilat_max = index_range[3]
    var = var[:,:,ilat_min:ilat_max,ilon_min:ilon_max]
    lon = ds.lon[ilat_min:ilat_max,ilon_min:ilon_max].values
    lat = ds.lat[ilat_min:ilat_max,ilon_min:ilon_max].values
    #X = ds.X[ilat_min:ilat_max].values
    #Y = ds.Y[ilon_min:ilon_max].values
    X = ds.X[ilon_min:ilon_max].values
    Y = ds.Y[ilat_min:ilat_min].values

    land_sea_mask = land_sea_mask[:imax_depth,ilat_min:ilat_max,ilon_min:ilon_max]

    return var, lat, lon, X, Y, land_sea_mask

# -----------------------------------------------------
def run(file,maskfile,dir_out,outfile_ending='_ml',varname_list=['salinity','temperature'],method='nearest',subsetting=False,testing=False):
    t0 = pytime.time()
    # -----------------------------------------------------
    # Get the land sea mask (3D DataArray)
    ds_mask = xr.open_dataset(maskfile)
    # Create a np bool array with True for ocean (==0)
    try:
        land_sea_mask_org = (ds_mask.isel(time=0)['land_binary_mask'].values == 0) # shape: (15, 1148, 2747)
    except ValueError:
        print("ERROR: there is something wrong with the mask file!")

    # Open the full dataset:
    ds = xr.open_dataset(file)

    if subsetting:
        # Get only a small portion of the data that easily fits into memory
        var, lat, lon, X, Y, land_sea_mask = get_subset(ds,land_sea_mask_org,varname)
        varname_list = ['temperature']
    elif testing:
        # Use test data
        var, land_sea_mask, lon, lat = get_test_data(ds,random=True)
        varname_list = ['temperature']
    else:
        # Get whole grid
        lon = ds.lon.values
        lat = ds.lat.values
        X = ds.X.values
        Y = ds.Y.values
        land_sea_mask = land_sea_mask_org
    
    print(f"Time fetching data: {pytime.time()-t0}s\n")
    
    # -----------------------------------------------------
    for varname in varname_list:
        t1 = pytime.time()
        if not subsetting and not testing:
            if varname not in ['zeta','Uwind_eastward','Vwind_northward']:
                var = ds[varname].values
            else: 
                # zeta++ has only surface values, so add depth axis
                var = ds[varname].values[:, np.newaxis, :, :]
        #else: use one variable and do one loop when testing and using subset

        # -----------------------------------------------------
        # Calc nans (over land) for all time steps
        if varname not in ['zeta','Uwind_eastward','Vwind_northward']:
            nland = np.sum(land_sea_mask)*var.shape[0]
        else: 
            nland = np.sum(land_sea_mask[0])*var.shape[0]
        nr_nans_to_remove = np.sum(np.isnan(var)) - nland

        if nr_nans_to_remove > 0:
            t2 = pytime.time()
            print(f"Total nr. of nans to remove for {varname}: {nr_nans_to_remove}")
            var = impute_variable(var,land_sea_mask,lon,lat,method,plot=False)
            print(f"Impute calculation time: {pytime.time()-t2}s")

            nr_nans = np.sum(np.isnan(var))
            if nr_nans > nland:
                print(f"WARNING! There are still {nr_nans - nland} NaNs remaining in the ocean!! (variable={varname}, method={method})")
        else:
            print(f"No NaNs to remove for {varname}, continuing...")

        # Store the results in a xarray dataset
        if varname == varname_list[0]:
            ds_new = init_dataset(ds,lon,lat,X,Y)
            
        # Add the variable to the new Dataset
        if varname not in ['zeta','Uwind_eastward','Vwind_northward']:
            ds_new[varname] = (['time', 'depth', 'Y', 'X'], var, ds[varname].attrs)
        else:
            ds_new[varname] = (['time', 'Y', 'X'], var[:,0,:,:], ds[varname].attrs)

        print(f"Time used for {varname}: {pytime.time()-t1}s \n")

    # -----------------------------------------------------
    # Save the new Dataset to a NetCDF file
    basename = file.split('/')[-1].split('.')[0]
    outfile = dir_out + basename + outfile_ending + '.nc'

    # Use a specific encoding incl. complevel
    time_encoding = {'time': {'units': 'seconds since 1970-01-01 00:00:00', 'calendar': 'gregorian', 'dtype': 'double', 'zlib': True, 'complevel': 4, '_FillValue': '-32767'}}
    other_encoding = {}
    for varname in list(ds_new.data_vars) + ['depth','X','Y']:
        if varname in varname_list: # dtype short
            other_encoding[varname] = {'zlib': True, 'complevel': 4, 'dtype': 'float32', '_FillValue': '-32767'}#, 'add_offset': '0.', 'scale_factor': '0.001'}
        elif varname in ['projection_stere','X','Y']: # dtype int
            other_encoding[varname] = {'zlib': True, 'complevel': 4}
        else: # dtype double
            other_encoding[varname] = {'zlib': True, 'complevel': 4, 'dtype': 'double', '_FillValue': '-32767'}
    # Combine the two encoding dictionaries
    encoding = {**time_encoding, **other_encoding}
    ds_new.to_netcdf(outfile,encoding=encoding)
    print(f"Saved to file successfully.\n{outfile}") 

    # -----------------------------------------------------
    tend = pytime.time() - t0
    hours, remainder_seconds = np.divmod(tend, 3600)
    minutes, seconds = np.divmod(remainder_seconds, 60)
    print(f"TOTAL TIME={int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")

if __name__ == "__main__":
    #/lustre/storeB/project/fou/hi/oper/norkyst_v3/forecast/his_zdepths/2024/01/01/

    #dir = '/lustre/storeB/project/fou/hi/foccus/ina/norkyst-data/postpro_changes/' #+ 'postpro_changes/' 
    #dir = '/home/inkul7832/Projects/aifs-mono-ocean/datasets/' #NOTE landseamask here might be outdated
    #file     = dir + 'norkyst800_his_zdepth_20240102T00Z_m00_AN.nc'
    #maskfile = dir + 'landsea_mask.nc'
    dir_out = '/lustre/storeB/project/fou/hi/foccus/datasets/prepro_norkyst/' 
    file = sys.argv[1]
    maskfile = sys.argv[2]
    
    # Using all 8 variables
    varname_list=['salinity','temperature','u_eastward','v_northward','w','zeta','Uwind_eastward','Vwind_northward']
    #varname_list=['Uwind_eastward']
    #varname_list=['salinity','temperature']
    print(f"Starting calculation for input file:\n{file}")
    run(file,maskfile,dir_out,outfile_ending='_ml',varname_list=varname_list,method='nearest',subsetting=False,testing=False)


"""
v1 (1 parameter): 8919738 
    ncfile: 4.3GB
    ru_wallclock 446s
    maxvmem      10.123GB


v2 (2 parameter): 8920158
    ncfile: 8.6GB
    ru_wallclock 889s
    maxvmem      13.587GB

---> 3.6GM more RAM for each additional parameter?
Use 40GB RAM? Seems like I'm using about 30GB

v22 for mateusz: 8923306
done, renamed output file to v2 for 20240102

-------------------------------------------------------------
Testing all variables: 8925363




qacct -j 8922082 -q research-r8.q

-------------------------------------------------------------
Test on PPI 'new' dataset, 24h & whole domain (one variable):
Impute calculation time: 404.0516827106476 s
which is 6.5 minutes

Test on laptop using 'old' dataset, 24h & whole domain:
Impute calculation time: 723.6508049964905 s
Nr. of nans remaining: 0

which is 12 minutes :D

-----
Tested using subset, then linear uses time=1s and nearest time=0.25s, and nans remains for linear
method=nearest:
-----

Time fetching data: 2.404872179031372 s
Nr. of nans to remove: 682
No NaN in layer idepth=0
No NaN in layer idepth=1
No NaN in layer idepth=2
itime=0, idepth=3, nr.nans=11
itime=0, idepth=4, nr.nans=11
itime=0, idepth=5, nr.nans=31
itime=0, idepth=6, nr.nans=47
itime=0, idepth=7, nr.nans=31
itime=0, idepth=8, nr.nans=23
itime=0, idepth=9, nr.nans=22
itime=0, idepth=10, nr.nans=26
itime=0, idepth=11, nr.nans=11
itime=0, idepth=12, nr.nans=13
No NaN in layer idepth=13
No NaN in layer idepth=14
No NaN in layer idepth=15
No NaN in layer idepth=0
No NaN in layer idepth=1
No NaN in layer idepth=2
itime=1, idepth=3, nr.nans=12
itime=1, idepth=4, nr.nans=11
itime=1, idepth=5, nr.nans=31
itime=1, idepth=6, nr.nans=48
itime=1, idepth=7, nr.nans=31
itime=1, idepth=8, nr.nans=23
itime=1, idepth=9, nr.nans=22
itime=1, idepth=10, nr.nans=26
itime=1, idepth=11, nr.nans=11
itime=1, idepth=12, nr.nans=13
No NaN in layer idepth=13
No NaN in layer idepth=14
No NaN in layer idepth=15
No NaN in layer idepth=0
No NaN in layer idepth=1
No NaN in layer idepth=2
itime=2, idepth=3, nr.nans=12
itime=2, idepth=4, nr.nans=11
itime=2, idepth=5, nr.nans=31
itime=2, idepth=6, nr.nans=48
itime=2, idepth=7, nr.nans=31
itime=2, idepth=8, nr.nans=23
itime=2, idepth=9, nr.nans=22
itime=2, idepth=10, nr.nans=26
itime=2, idepth=11, nr.nans=11
itime=2, idepth=12, nr.nans=13
No NaN in layer idepth=13
No NaN in layer idepth=14
No NaN in layer idepth=15
Impute calculation time: 0.25438547134399414
Nr. of nans remaining: 0

-----
method=linear:
-----

Time fetching data: 1.9501371383666992 s
Nr. of nans to remove: 682
No NaN in layer idepth=0
No NaN in layer idepth=1
No NaN in layer idepth=2
itime=0, idepth=3, nr.nans=11
itime=0, idepth=4, nr.nans=11
itime=0, idepth=5, nr.nans=31
itime=0, idepth=6, nr.nans=47
itime=0, idepth=7, nr.nans=31
itime=0, idepth=8, nr.nans=23
itime=0, idepth=9, nr.nans=22
itime=0, idepth=10, nr.nans=26
itime=0, idepth=11, nr.nans=11
itime=0, idepth=12, nr.nans=13
No NaN in layer idepth=13
No NaN in layer idepth=14
No NaN in layer idepth=15
No NaN in layer idepth=0
No NaN in layer idepth=1
No NaN in layer idepth=2
itime=1, idepth=3, nr.nans=12
itime=1, idepth=4, nr.nans=11
itime=1, idepth=5, nr.nans=31
itime=1, idepth=6, nr.nans=48
itime=1, idepth=7, nr.nans=31
itime=1, idepth=8, nr.nans=23
itime=1, idepth=9, nr.nans=22
itime=1, idepth=10, nr.nans=26
itime=1, idepth=11, nr.nans=11
itime=1, idepth=12, nr.nans=13
No NaN in layer idepth=13
No NaN in layer idepth=14
No NaN in layer idepth=15
No NaN in layer idepth=0
No NaN in layer idepth=1
No NaN in layer idepth=2
itime=2, idepth=3, nr.nans=12
itime=2, idepth=4, nr.nans=11
itime=2, idepth=5, nr.nans=31
itime=2, idepth=6, nr.nans=48
itime=2, idepth=7, nr.nans=31
itime=2, idepth=8, nr.nans=23
itime=2, idepth=9, nr.nans=22
itime=2, idepth=10, nr.nans=26
itime=2, idepth=11, nr.nans=11
itime=2, idepth=12, nr.nans=13
No NaN in layer idepth=13
No NaN in layer idepth=14
No NaN in layer idepth=15
Impute calculation time: 1.028571605682373 s
Nr. of nans remaining: 57
Traceback (most recent call last):
  File "/home/inkul7832/Projects/aifs-mono-ocean/dev-ina/preprocess-data/impute_nans.py", line 344, in <module>
    raise ValueError("There are still nans remaining in the ocean!! Stopping...")
ValueError: There are still nans remaining in the ocean!! Stopping...


"""

