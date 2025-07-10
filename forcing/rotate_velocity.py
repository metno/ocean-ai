import numpy as np
import scipy as sc

def rotate_vectorfield(U,V,alpha):
    '''rotate wind vectors clockwise. alpha may be a scalar or an array
    alpha is in degrees
    returns u,v '''
    alpha = np.array(alpha)*sp.pi/180
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
    pass
