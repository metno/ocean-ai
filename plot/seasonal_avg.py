import xarray as xr 
import numpy as np 
import glob
import sys
import argparse


def seasonal_avg_calc(save_path):
    year = xr.open_mfdataset('/lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot/yearly_means/*.nc')

    #Will try to make seasonal weights based on the xarray - but have to manually do so as the xarray has daily values, I have monthly, so can not use all built in funcs
    month_lengths = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    m = month_lengths
    DJF = m[-1] + m[0] + m[1]
    MAM = m[2] + m[3] + m[4]
    JJA = m[5] + m[6] + m[7]    
    SON = m[8] + m[9] + m[10]  

    weights = []
    for i in month_lengths[0:2]:
        weights.append(i / DJF)
    for j in month_lengths[2:5]:
        weights.append(j/MAM)
    for k in month_lengths[5:8]:
        weights.append(k/JJA)
    for v in month_lengths[8:11]:
        weights.append(v/SON)
    weights.append(month_lengths[-1] / DJF)

    #ensure that the weights are correctly calculated, sum should be 1
    print(weights[0] + weights[1] + weights[-1])
    print(weights[2] + weights[3] + weights[4])
    print(weights[5] + weights[6] + weights[7])
    print(weights[8] + weights[9] + weights[10])

    Weights = xr.DataArray(
    weights,
    dims = ['time'],
    coords = {'time' : year.time})

    ds = (year * Weights).groupby('time.season').sum(dim='time')

    ds.to_netcdf(save_path)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Calculation of seasonal averages of Norkyst dataset with monthly means')
    parser.add_argument('-sp' , '--save_path', help = 'Please enter wished saving path for the new netcdf file')
    args = parser.parse_args()
    save_path = args.save_path

seasonal_avg_calc(save_path)