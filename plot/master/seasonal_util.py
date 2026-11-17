import xarray as xr
import numpy as np

#making seasonal means - util function
def seasons(ds):
    #Then we make weights based on the number of days in the respective months
    month_length = ds.time.dt.days_in_month
    #Preview
    print(month_length)
    #Weights - tid per måned / summen av alle tider  
    weights = month_length.groupby('time.season') / month_length.groupby('time.season').sum(skipna = False)
    #testing to make sure the weights are correctly defined
    #weight_summed = np.testing.assert_allclose(weights.groupby('time.season').sum().values, np.ones(4)) 
    #if weight_summed != 1:
    #    raise ValueError(f'Weights are not properly defined - please ensure that the sum of weights for the seasons equal 1.0. Current sum is: {weight_summed}')
    #apply weights to dataset
    ds_weighted = (ds*weights).groupby('time.season').sum(dim = 'time', skipna = False)
    return ds_weighted 
