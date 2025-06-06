# This script renames the variable layers and sets the resolution (which is default 'none'). Only needed for datasets, not forcing files. 

# NOTE: Previously it was needed to change frequency from string to int + set resolution, due to version updates. Not needed anymore.
 
import zarr
import sys
import re

dataset = sys.argv[1]
print("Renaming variable layers\n",dataset)

z = zarr.convenience.open(dataset, 'r+')

print("Renaming rho layers in zarr dataset")
def rename_srho_variables():
    r = '(?<=_)-.*'
    level_list = []
    w_list = []
    all_variables = z._attrs['variables']
    for variable in all_variables:
        if re.findall(r, variable) and re.findall(r, variable)[0] not in level_list:
            if re.findall('w_-.*', variable):
                w_list.append(re.findall(r, variable)[0])
            else: 
                level_list.append(re.findall(r, variable)[0])

    index_dict = {}
    for i in range(len(level_list)):
        index_dict[level_list[i]] = str(i)
    w_index_dict = {}
    for i in range(len(w_list)):
        w_index_dict[w_list[i]] = str(i)

    for i in range(len(all_variables)):
        find = re.findall(r, all_variables[i])
        if re.findall('w_-.*', all_variables[i]):
            print('w')
            if find and find[0] in list(w_index_dict.keys()):
                all_variables[i] = re.sub(find[0], w_index_dict[find[0]], all_variables[i])
        else:
            if find and find[0] in list(index_dict.keys()):
                all_variables[i] = re.sub(find[0], index_dict[find[0]], all_variables[i])
    
    z._attrs['variables'] = all_variables

    new_dict = {}

    for var in z._attrs['variables_metadata']:
        content = z._attrs['variables_metadata'][var]
        find = re.findall(r, var)
        if find and find[0] in list(w_index_dict.keys()):
            name = re.sub(find[0],w_index_dict[find[0]], var)
        elif find and find[0] in list(index_dict.keys()):
            name = re.sub(find[0],index_dict[find[0]], var)
        else:
            name = var
        new_dict[name] = content
    z._attrs['variables_metadata'] = new_dict


rename_srho_variables()

# You can now check that setting frequency worked by:

#from anemoi.datasets import open_dataset
#ds = open_dataset("/lustre/storeB/project/fou/hi/foccus/aifs-mono-ocean/make-datasets/data/norkyst_v3_2024_01_01-02.zarr")
#ds.frequency
