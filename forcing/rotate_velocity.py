import numpy as np
import scipy as sp

def rotate_vectorfield(U,V,alpha):
    '''rotate wind vectors clockwise. alpha may be a scalar or an array
    alpha is in degrees
    returns u,v '''
    alpha = np.array(alpha)*np.pi/180
    alpha = alpha.flatten()
    R = np.array([[np.cos(alpha), -np.sin(alpha)], [np.sin(alpha), np.cos(alpha)] ])
    shpe = U.shape
    origwind = np.array((U.flatten(), V.flatten()))
    if len(R.shape)==2:
        rotwind = dot(R, origwind) # for constant rotation angle
    else:
        # for rotation angle given as array with same dimensions as U and V:
        # k-loop with rotwind(k) = dot(R(i,j,k), origwind(j,k)) (einstein summation indices)
        rotwind = np.einsum("ijk,ik -> jk", R, origwind)  # einstein summation indices
    Urot, Vrot = rotwind[0,:], rotwind[1,:]
    Urot = Urot.reshape(shpe)
    Vrot = Vrot.reshape(shpe)
    return Urot, Vrot

if __name__ == '__main__':
    import xarray as xr
    import matplotlib.pyplot as plt
    path = '/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_hindcast_atm_forcing/interpolated/'
    fileu = 'arome_meps_2_5km_2017010100-2017090606_ext_NK800_Uwind.nc'
    filev = 'arome_meps_2_5km_2017010100-2017090606_ext_NK800_Vwind.nc'
    dsu = xr.open_dataset(path+fileu).isel(time=0)
    dsv = xr.open_dataset(path+filev).isel(time=0)
    urot, vrot = rotate_vectorfield(dsu.Uwind.values, dsv.Vwind.values, dsu.lat.values)
    print(urot, vrot)
    s = 50
    fig, ax = plt.subplots(1,2)
    ax[0].quiver(dsu.lon.values[::s,::s], dsu.lat.values[::s,::s], dsu.Uwind.values[::s,::s], dsv.Vwind.values[::s,::s])
    ax[1].quiver(dsu.lon.values[::s, ::s], dsu.lat.values[::s,::s], urot[::s,::s], vrot[::s,::s])
    plt.savefig('t.png')