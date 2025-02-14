import re
import yaml
import datetime
import os
import xarray as xr


def find_valid_files(start = datetime.datetime(2024,1,1), end = datetime.datetime(2024,10,28), path='/lustre/storeB/project/fou/hi/foccus/datasets/prepro_norkyst/'):
    delta = (end-start).days
    valid_files = []
    invalid_files = []

    for day in range(delta+1):
        now = start + datetime.timedelta(days=day)
        file = f'norkyst800_his_zdepth_{now.year}{now.month:02d}{now.day:02d}T00Z_m00_AN_ml.nc'
        if os.path.exists(path+file):
            valid_files.append(path+file)
        else:
            invalid_files.append(path+file)

    return valid_files, invalid_files, path

def create_dataset_yaml_file(start = datetime.datetime(2024,1,1,0), end = datetime.datetime(2024,1,1,18), frequency = '1h', params_list = ['temperature', 'salinity'], outfile = 'norkystv3.yaml', path='/lustre/storeB/project/fou/hi/foccus/datasets/prepro_norkyst/'):
    '''
        A function for creating yaml file for anemoi dataset. Creates a directory with symlinks to input files.
    Args:
        start       [datetime]  :   start time for dataset creation.
        end         [datetime]  :   end time for dataset creation.
        frequency   [str]   :   string of dataset frequency in hours.
        params_list [list]  :   list of strings of variable names.
        outfile     [str]   :   name of output yaml file. The symlink directory created will be named after this as well. 
    '''
    valid_files, invalid_files, path = find_valid_files(start, end, path)
    path = '/lustre/storeB/project/fou/hi/foccus/datasets/'
    

    invalid_times = []
    date_re = '(?<=_)[0-9]*(?=T)'
    for file in invalid_files:
        file = re.findall(date_re, file)[0]
        date = datetime.datetime.strptime(file, '%Y%m%d')
        invalid_times.append(date)
        for t in range(1,24):
            date = date + datetime.timedelta(hours=1)
            invalid_times.append(date)

    input_dict = {
        'dates': {'start': start, 'end': end, 'frequency': frequency},
        'resolution': 'o96',
        'statistics': {'allow_nans': list(params_list)},
        'input': {'netcdf': {'path': path+'*', 'param': list(params_list)}},
        'missing': invalid_times
    }

    with open(outfile, 'w') as f:
        yaml.dump(input_dict, f, sort_keys=False)

if __name__ == '__main__':
    create_dataset_yaml_file(start = datetime.datetime(2024,1,1,0), end=datetime.datetime(2024,12,2,20), params_list=['temperature', 'salinity', 'u_eastward', 'v_northward', 'w', 'zeta', 'Uwind_eastward', 'Vwind_northward'])