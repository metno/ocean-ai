import re
import yaml
import datetime
import os
import xarray as xr


def find_valid_files(start = datetime.datetime(2024,1,1), end = datetime.datetime(2024,10,28), path='/lustre/storeB/project/fou/hi/oper/norkyst_v3/forecast/his_zdepths/'):
    delta = (end-start).days
    valid_files = []
    invalid_files = []

    for day in range(delta+1):
        correct_mapping = True
        now = start + datetime.timedelta(days=day)
        #add option to change this filename
        file = f'{now.year}/{now.month:02d}/{now.day:02d}/norkyst800_his_zdepth_{now.year}{now.month:02d}{now.day:02d}T00Z_m00_AN.nc'
        if os.path.exists(path+file):
            ds = xr.open_dataset(path+file)
            for var in ds.variables:
                if 'grid_mapping' in ds[var].attrs:
                    if ds[var].grid_mapping == 'projection_1':
                        correct_mapping = False
            if correct_mapping == False:
                invalid_files.append(path+file)
            elif correct_mapping == True:
                valid_files.append(path+file)

        else:
            invalid_files.append(path+file)

    return valid_files, invalid_files, path

def create_dataset_yaml_file(start = datetime.datetime(2024,1,1,0), end = datetime.datetime(2024,1,1,18), frequency = '1h', params_list = ['temperature', 'salinity'], outfile = 'norkystv3.yaml'):
    '''
        A function for creating yaml file for anemoi dataset. Creates a directory with symlinks to input files.
    Args:
        start       [datetime]  :   start time for dataset creation.
        end         [datetime]  :   end time for dataset creation.
        frequency   [str]   :   string of dataset frequency in hours.
        params_list [list]  :   list of strings of variable names.
        outfile     [str]   :   name of output yaml file. The symlink directory created will be named after this as well. 
    '''
    valid_files, invalid_files, path = find_valid_files(start, end)
    path = '/lustre/storeB/project/fou/hi/foccus/datasets/'
    symlink_folder = f'symlinks_{outfile[0:-5]}/'
    if not os.path.exists(path+'symlink_folder'):
        os.mkdir(path+'symlink_folder')
    if not os.path.exists(f'{path}symlink_folder/{symlink_folder}'):
        os.mkdir(f'{path}symlink_folder/{symlink_folder}')

    for file in valid_files:
        symlink_file = re.sub('.*/', '', file)
        symlink_name = path+'symlink_folder/'+symlink_folder+symlink_file
        os.symlink(file, symlink_name)

    invalid_times = []
    date_re = '(?<=_)[0-9]*(?=T)'
    for file in invalid_files:
        file = re.findall(date_re, file)[0]
        date = datetime.datetime.strptime(file, '%Y%m%d')
        invalid_times.append(date)

    input_dict = {
        'dates': {'start': start, 'end': end, 'frequency': frequency},
        'resolution': 'o96',
        'statistics': {'allow_nans': list(params_list)},
        'input': {'netcdf': {'path': path+f'symlink_folder/{symlink_folder}'+'*', 'param': list(params_list)}},
        'missing': invalid_times
    }

    with open(outfile, 'w') as f:
        yaml.dump(input_dict, f, sort_keys=False)

if __name__ == '__main__':
    create_dataset_yaml_file(start = datetime.datetime(2024,1,2,0), end=datetime.datetime(2024,1,4,20), params_list = ['temperature'])
    #create_dataset_yaml_file(start = datetime.datetime(2024,1,1,0), end=datetime.datetime(2024,1,2,23), params_list = ['temperature', 'depth'], outfile="norkyst-two2.yaml")
    import argparse

    parser = argparse.ArgumentParser(
        prog='CreateDatasetYaml'
    )

    parser.add_argument(
        '-s', '--start', default='2024-01-01-0000'
    )
    parser.add_argument(
        '-e', '--end', default='2024-01-02-2000'
    )
