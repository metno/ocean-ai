'''
A class for opening a dataset and doing operations on it. 
Uses xarray.

Author: Mateusz Matuszak
'''

class open_dataset:
    def __init__(self, file, var=None, lat_min=None, lat_max=None, lon_min=None, lon_max=None, region=None):
        '''
        A class for opening a dataset.
        Example usage:
            ds = open_dataset(<file>).dataset
        Available operations:
            Select specific variable(s) from str or list
            Cutout a region using one of the predefined regions or custom values
        
        Args:
            file    [str]           :   Filename
            var     [str or list]   :   A string or list of strings containing variable names to be extracted
            lat_min [int]           :   Minimum latitude for cutout
            lat_max [int]           :   Maximum latitude for cutout
            lon_min [int]           :   Minimum longitude for cutout
            lon_max [int]           :   Maximum longitude for cutout
            region  [str]           :   Cutout for predefined region from dict. Available: [lofoten, sulafjorden, oslofjorden]
        
        If not all of [lat_min, lat_max, lon_min, lon_max] are defined, will select min/max values for undefined arguments based on min/max values in dataset. 
        '''
        import xarray as xr
        import numpy as np
        self.dataset = xr.open_dataset(file)
        self.var = var
        self.grid = np.array([lat_min, lat_max, lon_min, lon_max])
        self.region = region
        full_grid = np.array([np.min(self.dataset.latitude), np.max(self.dataset.latitude), np.min(self.dataset.longitude), np.max(self.dataset.longitude)])

        if self.var is not None:
            self._select_variable

        if self.region is not None:
            self._select_predefined_region
        elif self.region is None and not all(_ == None for _ in self.grid):
            if None in self.grid:
                locs = np.where(self.grid == None)
                for loc in locs[0]:
                    self.grid[loc] = float(full_grid[loc])

        if not all(_ == None for _ in self.grid) and not (self.grid == full_grid).all():
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
        self.dataset = self.dataset.where(
            (self.dataset.latitude >= self.grid[0]) &
            (self.dataset.latitude <= self.grid[1]) &
            (self.dataset.longitude >= self.grid[2]) &
            (self.dataset.longitude <= self.grid[3]),
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
        self.var.extend(['longitude', 'latitude'])
        self.dataset = self.dataset[self.var]
        