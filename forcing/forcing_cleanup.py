import os
import xarray as xr

dir_atm = '/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_forcing_oper/atm'
print("Starting processing of dir:", dir_atm)

# Get files larger than 6 GB from dir_atm
for filename in os.listdir(dir_atm):
    filepath = os.path.join(dir_atm, filename)
    if os.path.isfile(filepath) and filename.startswith('norkyst_atm') and not filename.endswith('_24h.nc'):

        print(f'Processing file: {filename} --> 24h slicing')
        date_string = filename.split('_')[-1][:8]
        date_range = xr.date_range(start=date_string, periods=24, freq='h')
        
        # Open the dataset
        ds = xr.open_dataset(filepath)
        if ds.time.size > 24:
            # Only overwrite file if more than 24 time steps exist

            # Perform slicing
            ds_24h = ds.sel(time=slice(str(date_range[0]), str(date_range[-1])))

            if ds_24h.time.size != 24:
                print(f'Error: Sliced dataset does not have 24 time steps for file {filename}')
                continue
            
            # Write new dataset to file and remove the old file
            filepath_new = os.path.join(dir_atm,filename).replace('.nc', '_24h.nc')
            ds_24h.to_netcdf(filepath_new, mode='w')
            os.remove(filepath)

        else:
            print(f'    File {filename} already has 24 (or less) time steps, skipping.')

    #elif filename.endswith('_24h.nc'):
    #    print(f'    File {filename} already processed, skipping.')
