#python script for calculating the monthly anomalies of salinity

#Importing necessary packages
import numpy as np 
import xarray as xr
from dataloader import open_dataset
import glob
import os 
import logging 
logging.basicConfig(level = logging.INFO)

def open_files(month):
    """
    Description:
    Opens files per day for calculating salinity anomalies

    Arguments: 
    arg[1] : month (int) - Please provide a number between [1,12]
    """
    filepaths = f'/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/norkyst800-2024{month}*'  
    #Store all files in a dict 
    month_dict = {}
    for filepath in glob.glob(filepaths):
        logging.info(f'Processing file: {filepath}')
        filename = os.path.basename(filepath)
        date = filename.split('-')[-1]
        day = date.split('.')[0] #extract day + month

        #open files 
        ds = open_dataset(filepath, depth = -1).ds 
        month_dict[day] = ds 

    return month_dict


def climatology_calculation():

    """
    Description:
    Calculating the climatology of salinity
    """

    filepath_avg = '/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_averages/anomalies/daily_avg/*.nc'
    ds_year = xr.open_mfdataset(filepath_avg, chunks = {'time' : 12})

    month_lenghts = ds_year.time.dt.days_in_month
    weights = month_lenghts.groupby('time.season') / month_lenghts.groupby('time.season').sum()
    weighed_monthly = ds_year.salinity * weights 
    seasonal_clim = weighed_monthly.groupby('time.season').sum(dim = 'time') 

    return seasonal_clim

def anomaly_calculations(month):

    """
    Description:
    Calculating the anomalies from the daily variations and the seasonal climatologies 

    Arguments: 
    arg[1] : month (int) - Please provide a number between [1,12]

    Output: 
    Stores the monthly anomalies as a new .nc file
    """
    
    anomalies = {}
    #Open norkyst for selected month
    monthly_data = open_files(month)
    climatology = climatology_calculation()

    for day, data in monthly_data.items():
        salinity_norkyst = data.salinity
        anomalies[day] = salinity_norkyst - climatology

    anomalies_total = list(anomalies.values())
    anomaly_ds = xr.concat(anomalies_total, dim = 'time')
    #Store as nc file
    output = f'/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_averages/anomalies/salinity-{month}.nc'
    anomaly_ds.to_netcdf(output)
    return print(f'Calculation of the salinity anomalies is saved as a netcdf file and is complete.')


months = [1,2,3,4,5,6,7,8,9,10,11,12]
for i in months:
    print(f'Processing month: {i}')
    anomaly_calculations(i)


"""
Eller lage en baseline for hele 2012 - 2024? som klimatologi?? 
"""