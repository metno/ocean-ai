'''
A class for opening a dataset and doing operations on it. 
Uses xarray.

Author: Mateusz Matuszak
'''
import xarray as xr
import numpy as np
import warnings
warnings.filterwarnings("ignore")

class open_dataset(xr.DataArray):
    def __init__(self, file, time=None, depth=None, region=None, mean_axis=None, *args, **kwargs):
        '''
        A class for opening a dataset.
        Example usage:
            ds = open_dataset(<file>).dataset
        Available operations:
            Select specific variable(s) from str or list
            Cutout a region using one of the predefined regions or custom values
        
        Args:
            file    [str]           :   Filename or path
            time    [See below]     :   Times
            depth   [see below]     :   Depth index
            region  [str]           :   Cutout for predefined region from dict. Available: [lofoten, sulafjorden, oslofjorden]
        '''
        super().__init__(*args, **kwargs)
        if '*' in file:
            self.ds = xr.open_mfdataset(file)
        else:
            self.ds = xr.open_dataset(file)

        self.depth=depth
        self.region=region
        self.time=time

        naming_conventions={
            'longitude': 'lon',
            'latitude': 'lat',
            'salinity_0': 'salinity',
            'temperature_0': 'temperature',
            'u_eastward_0': 'u_eastward',
            'v_northward_0': 'v_northward',
        }

        self.ll = 'lat'
        self.lg = 'lon'

        for var in self.ds.variables:
            if var in naming_conventions.keys():
                self.ds = self.ds.rename({f'{var}': f'{naming_conventions[var]}'})
        
        dims = list(self.ds.dims)
        if 'X' in dims and 'Y' in dims:
            #print(f"dims.index('X') = {dims.index('X')}")
            #print(f"dims.index('Y') = {dims.index('Y')}")
            # Access the values of 'X' and 'Y' coordinates
            x_len = len(self.ds['X'].values)
            y_len = len(self.ds['Y'].values)
            #print(f"X values: {x_len}")
            #print(f"Y values: {y_len}")
            #if dims.index('X') < dims.index('Y'): NOTE: X is always 0 and Y is 1, but still the Havbris is flipped
            if x_len < y_len: # NOTE: Changed to checking the values instead!
                self.ds = self.ds.rename({'Y': 'X', 'X': 'Y'})
        
        if self.time is not None:
            self._select_time
        
        if self.depth is not None:
            self._select_depth
        
        if mean_axis is not None:
            self.ds = self._mean(mean_axis)
        
        if self.region is not None:
            self._select_predefined_region
            self.ds.load()
            if not all(_ == None for _ in self.grid):
                self._cutout_region

    @property
    def _select_predefined_region(self):
        '''
        Select region from predefined list
        '''
        region_dict = {
            'lofoten': [66,71,10,19],
            'sulafjorden': [62,63,4,8],
            'oslofjorden': [58.5,60,9.5,11.5]
        }
        if type(self.region) != str:
            raise TypeError(f'Region must be a str, got type {type(self.region)}')
        if self.region not in region_dict.keys():
            raise ValueError(f'Provided region {self.region} is not in list of predefined regions. Available regions are {list(region_dict.keys())}.')
        
        self.grid = [region_dict[self.region][0], region_dict[self.region][1], region_dict[self.region][2], region_dict[self.region][3]]

    @property
    def _cutout_region(self):
        '''
        Selects a specified region in the dataset
        '''
        self.ds = self.ds.where(
            (self.ds[self.ll] >= self.grid[0]) &
            (self.ds[self.ll] <= self.grid[1]) &
            (self.ds[self.lg] >= self.grid[2]) &
            (self.ds[self.lg] <= self.grid[3]),
            drop=True 
        ) 

    @property
    def _select_variable(self):
        '''
        select specified variable(s)
        '''
        if type(self.var) is not str and type(self.var) is not list:
            raise TypeError(f'Argument "var" must be of type str or a list of str, got {type(self.var)}')
        if type(self.var) is list:
            for var in self.var:
                if type(var) is not str:
                    raise TypeError(f'All elements in the variables list must be str, got {type(var)}')
        if type(self.var) is str:
            self.var = [self.var]
        self.var.extend([self.lg, self.ll])
        self.ds = self.ds[self.var]
    
    @property
    def _select_time(self):
        '''
        Select specified time(s)

        Can be an int, a list of ints, a str or a list of str, a datetime or list of datetimes
        '''
        import datetime
        if type(self.time) is not int and type(self.time) is not list and type(self.time) is not str and type(self.time) is not datetime.datetime:
            raise TypeError(f'Argument "time" must be of type int, list or str, got {type(self.time)}')
        
        if type(self.time) is list:
            for time in self.time:
                if type(time) is not str and type(time) is not int and type(time) is not datetime.datetime:
                    raise TypeError(f'All elements in the time list must be str, int or datetime.datetime, got {type(time)}')
        
        if type(self.time) is int or type(self.time) is list and type(self.time[0]) is int:
            self.ds = self.ds.isel(time=self.time)
        
        elif type(self.time) is str or type(self.time) is datetime.datetime or type(self.time) is list and type(self.time[0]) is str or type(self.time) is list and type(self.time[0]) is datetime.datetime:
            self.ds = self.ds.sel(time=self.time)
    
    @property
    def _select_depth(self):
        '''
        Select specified depth(s)
        '''
        if type(self.depth) is not int and type(self.depth) is not list:
            raise TypeError(f'Argument "depth" must be of type int or a list of ints, got {type(self.depth)}')
        
        if type(self.depth) is list:
            for depth in self.depth:
                if type(depth) is not int:
                    raise TypeError(f'All elements in the depth list must be str or int, got {type(depth)}')
        
        if 's_rho' in self.ds.variables:
            self.ds = self.ds.isel(s_rho=self.depth)
        elif 'depth' in self.ds.variables:
            self.ds = self.ds.isel(depth=self.depth)
    
    def _mean(self, axis):
        return self.ds.mean(dim=axis).compute()

    def __str__(self):
        return str(self.ds)

if __name__ == '__main__':
    ds = open_dataset('/lustre/storeB/project/fou/hi/foccus/mateuszm/results/may2024/2024-05-27_24h_18d28_e011_s050000.nc')
    #print(ds)
    #print('****************\n')
    ds = open_dataset('/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2023/norkyst800-20231221.nc')
    #print(ds)
