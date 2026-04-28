import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy.stats as stats
from scipy import fftpack
import matplotlib.colors as colors

def _weights(alpha_k, alpha_kp1, alpha_mn):
    """ From Ricard et al. (2013)"""
    
    a = (alpha_mn - alpha_k)/(alpha_kp1 - alpha_k)
    b = (alpha_kp1 - alpha_mn)/(alpha_kp1 - alpha_k)

    return a, b

def power_spectra(ds, vars = ['temperature', 'salinity', 'u_eastward', 'v_northward']):
    # it's a little slow, there are too many loops!
    ds_s = ds.isel(X=slice(700,1100), Y=slice(1000,1400))
    P = np.zeros([400, len(vars), len(ds_s.time)])
    K = np.zeros_like(P)


    for i, var in enumerate(vars):
        print(var)
        #for t in range(len(ds_s.time)):
        for t in range(len(ds_s.time)):
            tmp = ds_s[var].isel(time=t)
            fourier_image = fftpack.dct(fftpack.dct(np.array(tmp), axis=0, type=2, norm='ortho'), axis=1, type=2, norm='ortho')
            fourier_amplitudes = np.abs(fourier_image)**2
            dx = 0.8
            Ni = np.shape(fourier_image)[1]
            Nj = np.shape(fourier_image)[0]
            Ni_inds, Nj_inds = np.meshgrid(np.arange(Ni), np.arange(Nj))
            vararr = np.zeros(min([Ni, Nj]))
            wavelengtharrmin = np.zeros(min([Ni, Nj]))
            wavelengtharrmax = np.zeros(min([Ni, Nj]))
            alphamaxarr = np.zeros(min([Ni, Nj]))
            for k in range(1, min([Ni, Nj])):
                # For a given k, determine the limits of the contributing band defined by alpha(k) and alpha(k) + delta(alpha(k)):
                alphamin = k/min([Ni, Nj])
                alphamax = (k+1)/min([Ni, Nj])
                alphamaxarr[k-1] = alphamax

                wavelengtharrmax[k-1] = 2*dx/alphamin
                wavelengtharrmin[k-1] = 2*dx/alphamax
                
                alpha_m = np.sqrt((Ni_inds**2/Ni**2) + (Nj_inds**2/Nj**2))
                
                a, b = _weights(alphamin, alphamax, alpha_m)
                
                vararr[k-1] += np.sum(a*fourier_amplitudes,  where = (alpha_m >= alphamin) & (alpha_m < alphamax))
                
                vararr[k] += np.sum(b*fourier_amplitudes,  where = (alpha_m >= alphamin) & (alpha_m < alphamax))


                for x in np.where((alpha_m >= alphamin) & (alpha_m < alphamax), a*fourier_amplitudes, 0):
                    if np.any(x < 0):
                        print('Negative values used.')
                        sys.exit()
                
                for x in np.where((alpha_m >= alphamin) & (alpha_m < alphamax), b*fourier_amplitudes, 0):
                    if np.any(x < 0):
                        print('Negative values used.')
                        sys.exit()

                #if np.any(x < 0 for x in np.where((alpha_m >= alphamin) & (alpha_m < alphamax), a*fourier_amplitudes, 0)) == True:
                #    print('Negative values used, stop1!')
                #    sys.exit()
                #if np.any(x < 0 for x in np.where((alpha_m >= alphamin) & (alpha_m < alphamax), b*fourier_amplitudes, 0)) == True:
                #    print('Negative values used, stop2!')
                #    sys.exit()
            P[:,i,t] = wavelengtharrmax
            K[:,i,t] = vararr

    return P, K

def temporal_mean(ds):
    #This function feels a little redundant
    return ds.mean('time').compute()

def absolute_vel(ds):
    return np.sqrt(ds.u_eastward**2 + ds.v_northward**2)


if __name__ == '__main__':
    pass