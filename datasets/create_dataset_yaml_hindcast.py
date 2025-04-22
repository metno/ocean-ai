import re
import yaml
import datetime
import os
import xarray as xr


def find_valid_files(start = datetime.datetime(2024,1,1), end = datetime.datetime(2024,10,28), path='/lustre/storeB/project/fou/hi/roms_hindcast/norkyst_v3/sdepth/'):
    delta = (end-start).days
    valid_files = []
    invalid_files = []

    for day in range(delta+1):
        now = start + datetime.timedelta(days=day)
        file = f'norkyst800-{now.year}{now.month:02d}{now.day:02d}.nc'
        if os.path.exists(path+f'{now.year}/{now.month:02d}/'+file):
            valid_files.append(file)
        else:
            invalid_files.append(path+f'{now.year}/{now.month:02d}/'+file)

    return valid_files, invalid_files, path

def create_dataset_yaml_file(start = datetime.datetime(2024,1,1,0), end = datetime.datetime(2024,1,1,18), frequency = '1h', params_list = ['temperature', 'salinity'], outfile = 'norkystv3-hindcast.yaml', path='/lustre/storeB/project/fou/hi/roms_hindcast/norkyst_v3/sdepth/', nan_list=[]):
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
    
    if not os.path.exists(path+'symlinks'):
        os.mkdir(path+'symlinks')
    if not os.path.exists(path+'symlinks/' + 'norkystv3-hindcast'):
        os.mkdir(path+'symlinks/'+'norkystv3-hindcast')
    if not os.path.exists(path+'symlinks/'+'norkystv3-hindcast/'+f'{start.year}'):
        os.mkdir(path+'symlinks/'+'norkystv3-hindcast/'+f'{start.year}')

    delta = (end-start).days
    for day in range(delta+1):
        now = start + datetime.timedelta(days=day)
        p = f'/lustre/storeB/project/fou/hi/roms_hindcast/norkyst_v3/sdepth/{now.year}/{now.month:02d}/'
        file = f'norkyst800-{now.year}{now.month:02d}{now.day:02d}.nc'
        if p+file not in invalid_files:
            try:
                symlink_name = f'norkyst800-{now.year}{now.month:02d}{now.day:02d}.nc'
                os.symlink(p+file, path+f'symlinks/norkystv3-hindcast/{start.year}/' + symlink_name)
            except:
                pass

    invalid_times = []
    date_re = '(?<=)[0-9]*(?=\.nc)'
    for file in invalid_files:
        file = re.findall(date_re, file)[0]
        date = datetime.datetime.strptime(file, '%Y%m%d')
        invalid_times.append(date)
        for t in range(1,24):
            date = date + datetime.timedelta(hours=1)
            invalid_times.append(date)

    input_dict = {
        'dates': {'start': start, 'end': end, 'frequency': frequency},
        'build': {'group_by': 24},
        'resolution': 'o96',
        'statistics': {'allow_nans': list(nan_list)},
        'input': {'join':
                  [{'netcdf':
                   {'path':path+f'symlinks/norkystv3-hindcast/{start.year}/*',
                    'param':list(params_list)}},
                    {'repeated_dates':{
                        'mode': 'constant',
                        'source': {'netcdf': {'path': path+f'symlinks/norkystv3-hindcast/{start.year}/{valid_files[0]}', 'param':['h', 'sea_mask']}}}
                    }]},
        'missing': invalid_times
    }

    with open(outfile, 'w') as f:
        yaml.dump(input_dict, f, sort_keys=False)

if __name__ == '__main__':
    params_list = ['temperature', 'salinity', 'u_eastward', 'v_northward', 'ubar_eastward', 'vbar_northward', 'zeta', 'Uwind_eastward', 'Vwind_northward']
    nan_list = params_list
    create_dataset_yaml_file(start = datetime.datetime(2022,1,1,0), end=datetime.datetime(2022,12,31,23), params_list=params_list, nan_list=nan_list, outfile='yaml_files/norkystv3-hindcast-2022.yaml')