from netCDF4 import Dataset
import numpy as np
from scipy.interpolate import griddata
from glob import glob
import time
import xarray as xr
import sys
import os
from dens_func import dens
import matplotlib.pyplot as plt 


def transformation(ds):
    ds_name = ds 
    #Define necessary variables used for the transformation from s_layer to depth
    hc = ds_name["hc"] #Critical depth for stretching
    cs_r = ds_name["Cs_r"] #stretching curve at rho points
    zeta = ds_name["zeta"] #.fillna(0) #free-surface 
    H = ds_name["h"] #bathymetry at rho-points (depth)
    #Vtransform = ds_name["Vtransform"] Not in this dataset
    s_rho = ds_name["s_rho"] #range 1,40. 40 is surface layer

    #Transformation process
    Z_0_rho = (hc * s_rho + cs_r * H) / (hc + H)
    z_rho = zeta + (zeta + H) * Z_0_rho

    ds_name.coords["z_rho"] = z_rho.transpose() #Corrects the dimensions
    return z_rho 


def MLD(pot_dens, z):
    '''
    Calculate Mixed Layer Depth (MLD) based on potential density profile and depth.
    MLD is where the potential density exceeds a threshold, here set to be surface
    potential density + 0.03 kgm-3.

    Parameters:
    - pot_dens: 1D numpy array of potential density [kg/m^3]
    - z: 1D numpy array of corresponding depth levels [m] (negative downward)

    Returns:
    - mld: scalar value of MLD [m], or local water depth if no depth exceeds threshold,
    meaning full water column is mixed.
    '''
    # Remove NaNs
    valid = ~np.isnan(pot_dens)
    pot_dens = pot_dens[valid]
    z = z[valid]

    if len(pot_dens) == 0:
        return print(f"Length of potential density input is equal to zero. Retuned value is a nan value: {np.nan}")

    # Surface density
    surface_density = pot_dens[0]
    threshold = surface_density + 0.03  # MLD is where density exceeds surface + 0.03

    # Find where density exceeds threshold
    exceed = np.where(pot_dens >= threshold)[0]

    if exceed.size == 0:
        return print(f"No depth exceeds treshold. First value of z is returned: {z[-1]}")  # no depth exceeds threshold

    # Return the first depth where threshold is exceeded
    return print(f"The first depth where the treshold is exceeded is: {z[exceed[0]]}") 



def interpolate_grid(depth_transf, Temp, Salinity, nz = 40, eta_chunck = 40):

    #create grid sizes
    eta_size = depth_transf.sizes['Y']
    xi_size = depth_transf.sizes['X']

    #initialize array
    out_array = np.full((3, nz, eta_size, xi_size), np.nan) #np.full(shape, fill_val)
    
    print(f'The original shape of depth transformed is: {depth_transf.shape}')
    print(f'The original shape of temp is: {Temp.shape}')
    print(f'The original shape of salnity is: {Salinity.shape}')
    
    #Horizontal slice
    for i_start in range(0,eta_size, eta_chunck):
        i_end = min(i_start+eta_chunck, eta_size) #ends at 1148

        depth_slice = depth_transf[:, i_start:i_end, :].values
        temp_slice = Temp[:, i_start:i_end, :].values
        salinity_slice = Salinity[:, i_start:i_end, :].values

        print(f'Depth slice {depth_slice.shape}')
        print(f'Temp slice {temp_slice.shape}')
        print(f'Salinity slice {salinity_slice.shape}')

        #vectorized interpolation

        for ii in range(depth_slice.shape[1]):  # eta in chunk
            for jj in range(depth_slice.shape[2]):  # xi
                dcol = depth_slice[:, ii, jj]
                tcol = temp_slice[:, ii, jj]
                scol = salinity_slice[:,ii,jj]
                
                mask = np.isfinite(dcol) & np.isfinite(tcol) & np.isfinite(scol)
                if mask.sum() < 2:
                    continue
                
                d = dcol[mask]
                t = tcol[mask]
                s = scol[mask]
                
                # Sort and remove duplicates
                sort_idx = np.argsort(d)
                d, t, s = d[sort_idx], t[sort_idx], s[sort_idx]
                keep = np.ones(len(d), bool)
                for k in range(1, len(d)):
                    if d[k] == d[k-1]:
                        keep[k] = False
                d, t, s = d[keep], t[keep], s[keep]

                
                # Column-specific new depth
                new_depth_col = np.linspace(d.min(), d.max(), nz)
                
                # Vectorized interpolation
                out_array[0, :, i_start+ii, jj] = np.interp(new_depth_col, d, t)
                out_array[1, :, i_start+ii, jj] = np.interp(new_depth_col, d, s)
                out_array[2, :, i_start+ii, jj] = new_depth_col
    
    #debugging
    print(f'Shape of d is: {d.shape}')
    print(f'Shape of t is: {t.shape}')
    print(f'Shape of s is: {s.shape}')

    da = xr.DataArray(out_array,
                      dims=("var", "new_depth", "eta_rho", "xi_rho"),
                      coords={"var": ["temperature", "salinity" ,"depth"]})
    
    return da

def prepare_dataset(ds):

    #Assumes that the dataset is already preprocessed based on the information you want, but I will need to add some type of mean I think for memory
    #Eg seasonal averages or yearly means in my case
    #Perform transformation and add them to the dataset
    transformation(ds)

    #select out the new variable
    z = ds['z_rho']

    #then we interpolate
    #Gather the needed variables
    temp = ds['temperature']
    salinity = ds['salinity']
    #transpose depth to ensure the dimensions match
    depth_transposed = z.transpose(*temp.dims)
    da = interpolate_grid(depth_transposed, temp, salinity, nz = 40)

    return da 


def calculate_store_mld(ds, filename):
    #DS is the one thats been run through prepare_dataset
    #select variables
    temp_interpolated = ds[0].values
    salinity_interpolated = ds[1].values
    depth_interpolated = ds[2].values

    #Initialize empty arrays
    tmpd = np.full((temp_interpolated.shape), np.nan)
    tmmld = np.full((temp_interpolated.shape[1], temp_interpolated.shape[2]), np.nan)

    for ii in range(temp_interpolated.shape[1]):
        for jj in range(temp_interpolated.shape[2]):
            #Collect all vertical depths
            temp_profile = temp_interpolated[:, ii, jj]
            salinity_profile = salinity_interpolated[:, ii, jj] 

            #make sure no infinite values are included 
            mask = np.isfinite(temp_profile) & np.isfinite(salinity_profile) & np.isfinite(depth_interpolated)
            temp = temp_profile[mask]
            salinity = salinity_profile[mask]
            depth = depth_interpolated[mask]

            if len(temp) < 2:
                continue

            potential_dens = dens(salinity, temp)
            tmpd[:, ii, jj] = potential_dens

            mixed_layer = MLD(potential_dens, depth)
            tmmld[ii, jj] = mixed_layer

    ds_mld = xr.Dataset(
        data_vars=dict(
            pd = (['new_depth', 'Y', 'X'], tmpd, {'Units' : 'kg m^{-3}', 'Name' : 'Potential Density', 'Description' : 'Potential density'}),
            Mixed_layer = (['X', 'Y'], tmmld, {'Units' : 'm', 'Name' : 'Mixed Layer depth', 'Description' : 'Mixed layer depth calculated from surface density and 0.03 kgm-3 treshold'})
        ),
        coords=dict(
            Depth = ds.coords['new_depth'].values,
            eta_rho = ds.coords['eta_rho'].values, #X
            xi_rho = ds.coords['xi_rho'].values,   #Y         
        )
    )

    #Convert to netcdf file for easy access to plot and use values
    ds_mld.to_netcdf(f'potential_dens_mld_{filename}.nc')
