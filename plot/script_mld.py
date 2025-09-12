from dens_func import dens
import matplotlib.pyplot as plt 
import xarray as xr
import numpy as np

def transformation(ds_name):
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
    surface_density = pot_dens[-1]
    threshold = surface_density + 0.003  # MLD is where density exceeds surface + 0.03

    # Find where density exceeds threshold
    exceed = np.where(pot_dens >= threshold)[0]

    if exceed.size == 0:
        return print(f"No depth exceeds treshold. First value of z is returned: {z[-1]}")  # no depth exceeds threshold

    # Return the first depth where threshold is exceeded
    return print(f"The first depth where the treshold is exceeded is: {z[exceed[0]]}") 

#still in work - will be changed with the correct interpolated z values. 
def arrays(file_str):

    ds_name = xr.open_dataset(file_str)
    ds_name = ds_name.resample(time = "D").mean()
    
    #z_rho using the transformation function
    transformation(ds_name=ds_name)
    z_rho = ds_name["z_rho"].transpose("time", "s_rho", "Y", "X")
    print(z_rho.shape)    
    #variables 
    time = ds_name["time"]
    salt = ds_name["salinity"]
    temp = ds_name["temperature"]
    mask = ds_name["sea_mask"]
    print(salt.shape)
    print(mask.shape)


    #temporary arrays
    tmpd = np.full((salt.shape[0], z_rho.shape[1], salt.shape[2], salt.shape[3]), np.nan) #potential density, time, s_rho, x and y 
    tmmld = np.full((salt.shape[0], salt.shape[2], salt.shape[3]), np.nan) #mixed layer - time, x and y 
    print(tmpd.shape)
    print(tmmld.shape)

    # Looping through grid points
    for y in range(0, salt.shape[2]):
        for x in range(0, salt.shape[3]): 
            if not mask[y, x]:  # skipping land points
               continue

            t = -1
            z_rho_v = z_rho[t,:,y,x]
            salt_v = salt[t,:,y,x]
            temp_v = temp[t,:,y,x]

            dens_profile = dens(salt_v, temp_v, np.zeros_like(z_rho_v))
            tmpd[t,:,y,x] = dens_profile

            tmmld[t,y,x] = MLD(dens_profile, z_rho_v) 
            

    ds_mld = xr.Dataset(
        data_vars=dict( 
        pd = (["time", "z_rho", "Y", "X"], tmpd, {"units":"kg m^{-3}", "Name" : "Potential Density"}),
        mld = (["time", "Y", "X"], tmmld, {"units":"meter", "Name":"Mixed Layer Depth"})
        ),
        coords=dict(
            time = time,
            z_rho = ds_name["z_rho"].values,
            Y = ds_name["Y"].values, 
            X = ds_name["X"].values)
            )

    return ds_mld