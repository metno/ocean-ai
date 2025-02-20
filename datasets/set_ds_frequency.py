# Due to upgrades to anemoi-datasets frequency have changed from string to int 
# so we have to change it after having created the dataset
 
import zarr
import sys
import re
#dataset = "/lustre/storeB/project/fou/hi/foccus/aifs-mono-ocean/make-datasets/data/norkyst_v3_2024_01_01-02.zarr"
dataset = sys.argv[1]
print("Changing frequency from string to int for dataset: \n",dataset)

z = zarr.convenience.open(dataset, 'r+')
z._attrs['frequency'] = 1
z._attrs['resolution'] = 'o96'


def rename_srho_variables():
    r = '(?<=_)-.*'
    level_list = []
    all_variables = z._attrs['variables']
    for variable in all_variables:
        #if re.findall(r, variable):
        if re.findall(r, variable) and re.findall(r, variable)[0] not in level_list:
            level_list.append(re.findall(r, variable)[0])
    index_dict = {}
    for i in range(len(level_list)):
        index_dict[level_list[i]] = str(i)
    print(index_dict.keys())
    for i in range(len(all_variables)):
        find = re.findall(r, all_variables[i])
        if find and find[0] in list(index_dict.keys()):
            all_variables[i] = re.sub(find[0], index_dict[find[0]], all_variables[i])
    z._attrs['variables'] = all_variables

    new_dict = {}

    for var in z._attrs['variables_metadata']:
        content = z._attrs['variables_metadata'][var]
        find = re.findall(r, var)
        print(find)
        print(list(index_dict.keys()))
        if find and find[0] in list(index_dict.keys()):
            print('found')
            name = re.sub(find[0],index_dict[find[0]], var)
        else:
            name = var
        new_dict[name] = content
    z._attrs['variables_metadata'] = new_dict


rename_srho_variables()
# You can now check that it worked by:

#from anemoi.datasets import open_dataset
#ds = open_dataset("/lustre/storeB/project/fou/hi/foccus/aifs-mono-ocean/make-datasets/data/norkyst_v3_2024_01_01-02.zarr")
#ds.frequency
