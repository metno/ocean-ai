# Due to upgrades to anemoi-datasets frequency have changed from string to int 
# so we have to change it after having created the dataset
 
import zarr
import sys

#dataset = "/lustre/storeB/project/fou/hi/foccus/aifs-mono-ocean/make-datasets/data/norkyst_v3_2024_01_01-02.zarr"
dataset = sys.argv[1]
print("Changing frequency from string to int for dataset: \n",dataset)

z = zarr.convenience.open(dataset, 'r+')
print(z._attrs['frequency'])
z._attrs['frequency'] = 1
print("done")
print(z._attrs['frequency'])
z._attrs['resolution'] = 'o96'
print(z._attrs['resolution'])
# You can now check that it worked by:

#from anemoi.datasets import open_dataset
#ds = open_dataset("/lustre/storeB/project/fou/hi/foccus/aifs-mono-ocean/make-datasets/data/norkyst_v3_2024_01_01-02.zarr")
#ds.frequency
