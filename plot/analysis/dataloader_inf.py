###############################################################################################################################
# INFORMATION ABOUT THE SCRIPT : 
###############################################################################################################################
# Contain functions to open Norkyst-3 based on inference file
# NB! Now assumes not 1D netCDF-files, but post-proccessed files, ready to go!

###############################################################################################################################
# IMPORT NECESSARY PACKAGES : 
###############################################################################################################################
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import os
from typing import Tuple, Optional, Union, List
from dataloader import open_dataset

###############################################################################################################################
# READ IN HAVBRIS-INFERRED NETCDF-FILES : (For now, not a 'general' file format, need path and filename!)
###############################################################################################################################
def read_havbris_inferred_nc_filename(file_path: str,
                                      file_name: str,
                                      debug: bool = False ) -> Optional[Tuple[xr.Dataset, list]]:
    """
    Reads a NetCDF file, extracts variables and time steps, and returns the dataset and inferred time steps.

    Args:
        file_path (str): Path to the directory containing the file.
        file_name (str): Name of the NetCDF file to read.
        debug (bool): If True, enables debug-level logging.

    Returns:
        Optional[Tuple[xr.Dataset, list]]: The opened xarray Dataset and a list of inferred time steps,
                                           or None if the file does not exist.
    """
    # Combine file path and file name
    file_to_open = os.path.join(file_path, file_name)
    if debug:
        print(f"Try to read file : {file_to_open}")
        print()

    # Check if the file exists
    if os.path.exists(file_to_open):
        if debug:
            print(f"File exists!")
            print()
        try:
            # Open the NetCDF file
            #havbris_file = xr.open_dataset(file_to_open)
            havbris_file = open_dataset(file_to_open).ds
            print(f"File exists and is read!")
            print()

            if debug:
                # List variables in the dataset
                print("Variables in the dataset:")
                print(list(havbris_file.data_vars))
                print()
            
            # Extract time values
            inf_time = havbris_file.time.values
            if debug:
                print("Inferred time-steps:")
                print(inf_time)

            # Extract dates and time-steps 
            # Convert to datetime objects
            datetime_objects = np.array([np.datetime64(ts).astype('datetime64[m]') for ts in inf_time])
            # Extract unique days
            unique_days = np.unique([str(dt)[:10] for dt in datetime_objects])
            # Create a list of 'yyyy-mm-dd-hh:mm' strings
            datetime_strings = [str(dt).replace('T', '-')[:-3] for dt in datetime_objects]
            if debug:
                print("Unique days:")
                print(unique_days)
            
            # Return the dataset and inferred time steps
            return havbris_file, inf_time, unique_days, datetime_strings
        
        except Exception as e:
            # Handle any errors related to opening or processing the file
            print(f"Error occurred while reading the file: {e}")
            return None
    else:
        # Handle case where the file does not exist
        print(f"File do not exist!")
        return None
def read_havbris_inferred_nc(file_path: str,
                             debug: bool = False ) -> Optional[Tuple[xr.Dataset, list]]:
    """
    Reads a NetCDF file, extracts variables and time steps, and returns the dataset and inferred time steps.

    Args:
        file_path (str): Path to the directory containing the file.
        debug (bool): If True, enables debug-level logging.

    Returns:
        Optional[Tuple[xr.Dataset, list]]: The opened xarray Dataset and a list of inferred time steps,
                                           or None if the file does not exist.
    """
    # Combine file path and file name
    file_to_open = file_path
    if debug:
        print(f"Try to read file : {file_to_open}")
        print()

    # Check if the file exists
    if os.path.exists(file_to_open):
        if debug:
            print(f"File exists!")
            print()
        try:
            # Open the NetCDF file
            #havbris_file = xr.open_dataset(file_to_open)
            havbris_file = open_dataset(file_to_open).ds
            print(f"File exists and is read!")
            print()

            if debug:
                # List variables in the dataset
                print("Variables in the dataset:")
                print(list(havbris_file.data_vars))
                print()
            
            # Extract time values
            inf_time = havbris_file.time.values
            if debug:
                print("Inferred time-steps:")
                print(inf_time)

            # Extract dates and time-steps 
            # Convert to datetime objects
            datetime_objects = np.array([np.datetime64(ts).astype('datetime64[m]') for ts in inf_time])
            # Extract unique days
            unique_days = np.unique([str(dt)[:10] for dt in datetime_objects])
            # Create a list of 'yyyy-mm-dd-hh:mm' strings
            datetime_strings = [str(dt).replace('T', '-')[:-3] for dt in datetime_objects]
            if debug:
                print("Unique days:")
                print(unique_days)
            
            # Return the dataset and inferred time steps
            return havbris_file, inf_time, unique_days, datetime_strings
        
        except Exception as e:
            # Handle any errors related to opening or processing the file
            print(f"Error occurred while reading the file: {e}")
            return None
    else:
        # Handle case where the file does not exist
        print(f"File do not exist!")
        return None
###############################################################################################################################
# READ IN NORKYST-3 HINDCAST FILES BASED ON TIME-STEPS AND DATES FROM HAVBRIS-INFERRED NETCDF-FILES : 
###############################################################################################################################
def read_norkyst_hindcast_based_on_inferred_nc(file_path: str,
                                               file_name_template: str,
                                               unique_days_from_havbris: Union[np.ndarray, list],
                                               date_format: str = "%Y-%m-%d",  # Default date format
                                               debug: bool = False ) -> Optional[List[xr.Dataset]]:
    """
    Reads Norkyst hindcast NetCDF files based on inferred dates from Havbris.

    Args:
        file_path (str): Path to the directory containing the files.
        file_name_template (str): Template for file names, e.g., "norkyst_{year}_{month:02d}_{day:02d}.nc".
        unique_days_from_havbris (Union[np.ndarray, List[str]]): List or NumPy array of unique days (e.g., ['2024-04-02']).
        date_format (str): Format of the dates in `unique_days_from_havbris` (default is '%Y-%m-%d').
        debug (bool): If True, enables debug-level logging.

    Returns:
        Optional[List[xr.Dataset]]: A list of xarray Datasets from all valid NetCDF files, or None if no files are found.
    """
    truth_datasets = []

    if debug:
        print(f"Unique days : {unique_days_from_havbris}")
        print()

    for day in unique_days_from_havbris:
        try:
            # Parse the date string into a datetime object
            valid_time = dt.datetime.strptime(day, date_format)
            if debug:
                print(f"valid_time:{valid_time}")
                print()

            # Generate the full file path using the file name template and valid_time
            file_name = file_name_template.format(year  = valid_time.year,
                                                  month = valid_time.month,
                                                  day   = valid_time.day)
            if debug:
                print(f"file_name:{file_name}")
                print()
            full_file_path = os.path.join(file_path, file_name)
            if debug:
                print(f"full_file_path:{full_file_path}")
                print()

            print(f"Attempting to load file: {full_file_path}")
            # Read NetCDF file for the current day
            #ds = xr.open_dataset(full_file_path)
            ds = open_dataset(full_file_path).ds
            truth_datasets.append(ds)
            print(f"Successfully loaded: {full_file_path}")
            print()

        except FileNotFoundError:
            # File not found; skip to the next date
            print(f"File not found: {full_file_path}")

        except ValueError as e:
            # Handle invalid date formatting
            print(f"Error parsing date '{day}' with format '{date_format}': {e}")

        except Exception as e:
            # Catch any other unexpected errors
            print(f"An unexpected error occurred: {e}")

    # If no datasets were successfully loaded, return None
    if not truth_datasets:
        print("No valid datasets were found.")
        return None

    # Return the list of datasets
    return truth_datasets
###############################################################################################################################
# GET DS OF SELECTED VARIABLES FOR MATCHING TIME-STEPS : 
###############################################################################################################################
def get_variable_ds_matching_time(ds_havbris: xr.Dataset,
                                  ds_norkyst: List[xr.Dataset],
                                  inf_time: np.ndarray,
                                  variable_havbris: str = "salinity",
                                  variable_norkyst3: str = "salinity",
                                  s_rho_n3: int = 0,
                                  debug: bool = False) -> Tuple[xr.Dataset, xr.Dataset]:
    """
    Extracts and aligns variables from Havbris and Norkyst datasets based on the inferred time steps.

    Args:
        ds_havbris (xr.Dataset): Havbris dataset containing the variable to extract.
        ds_norkyst (List[xr.Dataset]): List of Norkyst datasets containing the variable to extract.
        inf_time (np.ndarray): Array of inferred time steps to match against Norkyst datasets.
        variable_havbris (str): Name of the variable to extract from Havbris (default: 'salinity_0').
        variable_norkyst3 (str): Name of the variable to extract from Norkyst (default: 'salinity').
        s_rho_n3 (int): Index for vertical layer selection in the Norkyst datasets (default: 0).
        debug (bool): If True, prints debug information (default: False).

    Returns:
        Tuple[xr.Dataset, xr.Dataset]:
            - `havbris`: Dataset containing the extracted variable and its coordinates from Havbris.
            - `norkyst3`: Dataset containing the concatenated variable and its coordinates from Norkyst datasets.
    """

    # Check if the variable exists in the Havbris dataset
    if variable_havbris not in ds_havbris.variables:
        raise ValueError(f"Variable '{variable_havbris}' not found in the Havbris dataset.")

    # Extract the variable and coordinates from Havbris
    havbris_variable = ds_havbris[variable_havbris]
    havbris_lat = ds_havbris['lat']
    havbris_lon = ds_havbris['lon']

    # Create a new dataset for Havbris containing the variable and its coordinates
    havbris = xr.Dataset(
        {
            variable_havbris: havbris_variable
        },
        coords={
            'lat': havbris_lat,
            'lon': havbris_lon
        }
    )
    if debug:
        print(f"Extracted variable '{variable_havbris}' and coordinates ('lat', 'lon') from Havbris dataset.")

    # Initialize a list to store the selected variables from Norkyst datasets
    norkyst3_var_list = []

    # Iterate through each Norkyst dataset
    for i, df in enumerate(ds_norkyst):
        if variable_norkyst3 not in df.variables:
            raise ValueError(f"Variable '{variable_norkyst3}' not found in Norkyst dataset {i}.")

        # Match the time indices where Norkyst time matches inferred time
        matching_indices = np.where(np.isin(df['time'].values, inf_time))[0]

        if debug:
            print(f"Norkyst dataset {i}: Found {len(matching_indices)} matching time indices.")

        # Extract the variable for the matching time indices and along the specified `s_rho` layer
        for idx in matching_indices:
            selected_var = df[variable_norkyst3].isel(time=idx, s_rho=s_rho_n3)
            norkyst3_var_list.append(selected_var)

    # Check if we have any data to concatenate
    if not norkyst3_var_list:
        raise ValueError("No matching time indices found in any Norkyst dataset. Check `inf_time` and dataset alignment.")

    # Concatenate the list of variables along the time dimension
    norkyst3_variable = xr.concat(norkyst3_var_list, dim="time")

    # Extract lat and lon from the first Norkyst dataset (assuming they are consistent across all datasets)
    norkyst_lat = ds_norkyst[0]['lat']
    norkyst_lon = ds_norkyst[0]['lon']

    # Create a new dataset for Norkyst containing the concatenated variable and its coordinates
    norkyst3 = xr.Dataset({variable_norkyst3: norkyst3_variable},
                          coords={'lat': norkyst_lat,
                                  'lon': norkyst_lon})

    if debug:
        print(f"Successfully concatenated {len(norkyst3_var_list)} variables from Norkyst datasets.")
        print(f"Included coordinates ('lat', 'lon') in the Norkyst dataset.")

    return havbris, norkyst3
###############################################################################################################################
# GET DS OF SELECTED VARIABLES FOR MATCHING TIME-STEPS : 
###############################################################################################################################
def get_variables_ds_matching_time(ds_havbris: xr.Dataset,
                                  ds_norkyst: List[xr.Dataset],
                                  inf_time: np.ndarray,
                                  variables: list = ["salinity", "temperature", "u_eastward", "v_northward"],
                                  s_rho_n3: int = 0,
                                  debug: bool = False) -> Tuple[xr.Dataset, xr.Dataset]:
    """
    Extracts and aligns multiple variables from Havbris and Norkyst datasets based on the inferred time steps.

    Args:
        ds_havbris (xr.Dataset): Havbris dataset containing the variables to extract.
        ds_norkyst (List[xr.Dataset]): List of Norkyst datasets containing the variables to extract.
        inf_time (np.ndarray): Array of inferred time steps to match against Norkyst datasets.
        variables (list): List of variable names to extract from both Havbris and Norkyst datasets.
        s_rho_n3 (int): Index for vertical layer selection in the Norkyst datasets (default: 0).
        debug (bool): If True, prints debug information (default: False).

    Returns:
        Tuple[xr.Dataset, xr.Dataset]:
            - `havbris`: Dataset containing the extracted variables and their coordinates from Havbris.
            - `norkyst3`: Dataset containing the concatenated variables and their coordinates from Norkyst datasets.
    """

    # Initialize dictionaries to store variables for Havbris and Norkyst
    havbris_data = {}
    norkyst3_data = {}

    # Iterate over all variables to process them
    for variable in variables:
        # Check if the variable exists in the Havbris dataset
        if variable not in ds_havbris.variables:
            raise ValueError(f"Variable '{variable}' not found in the Havbris dataset.")

        # Extract the variable and coordinates from Havbris
        havbris_variable = ds_havbris[variable]
        havbris_lat = ds_havbris['lat']
        havbris_lon = ds_havbris['lon']

        # Add the variable to the Havbris dictionary
        havbris_data[variable] = havbris_variable
        if debug:
            print(f"Extracted variable '{variable}' from Havbris dataset.")

        # Initialize a list to store the selected variables from Norkyst datasets
        norkyst3_var_list = []

        # Iterate through each Norkyst dataset
        for i, df in enumerate(ds_norkyst):
            if variable not in df.variables:
                raise ValueError(f"Variable '{variable}' not found in Norkyst dataset {i}.")

            # Match the time indices where Norkyst time matches inferred time
            matching_indices = np.where(np.isin(df['time'].values, inf_time))[0]

            if debug:
                print(f"Norkyst dataset {i}: Found {len(matching_indices)} matching time indices for variable '{variable}'.")

            # Extract the variable for the matching time indices and along the specified `s_rho` layer
            for idx in matching_indices:
                selected_var = df[variable].isel(time=idx, s_rho=s_rho_n3)
                norkyst3_var_list.append(selected_var)

        # Check if we have any data to concatenate
        if not norkyst3_var_list:
            raise ValueError(f"No matching time indices found for variable '{variable}' in any Norkyst dataset. Check `inf_time` and dataset alignment.")

        # Concatenate the list of variables along the time dimension
        norkyst3_variable = xr.concat(norkyst3_var_list, dim="time")

        # Add the concatenated variable to the Norkyst dictionary
        norkyst3_data[variable] = norkyst3_variable

    # Extract lat and lon from the first Norkyst dataset (assuming they are consistent across all datasets)
    norkyst_lat = ds_norkyst[0]['lat']
    norkyst_lon = ds_norkyst[0]['lon']

    # Create new datasets for Havbris and Norkyst3 containing the extracted variables and their coordinates
    havbris = xr.Dataset(havbris_data,
                         coords={'lat': havbris_lat,
                                 'lon': havbris_lon})
    norkyst3 = xr.Dataset(norkyst3_data,
                          coords={'lat': norkyst_lat,
                                  'lon': norkyst_lon})

    if debug:
        print(f"Successfully extracted variables {variables} from Havbris and Norkyst datasets.")
        print(f"Havbris dataset contains variables: {list(havbris.data_vars.keys())}")
        print(f"Norkyst dataset contains variables: {list(norkyst3.data_vars.keys())}")

    return havbris, norkyst3
###############################################################################################################################
# GET DS OF SELECTED VARIABLES FOR MATCHING TIME-STEPS ONLY HAVBRIS: 
###############################################################################################################################
def get_variables_ds_matching_time_havbris(ds_havbris: xr.Dataset,
                                           variables: list = ["salinity", "temperature", "u_eastward", "v_northward"],
                                           s_rho_n3: int = 0, # Keep for future
                                           debug: bool = False) -> Tuple[xr.Dataset, xr.Dataset]:
    """
    Extracts and aligns multiple variables from Havbris and Norkyst datasets based on the inferred time steps.

    Args:
        ds_havbris (xr.Dataset): Havbris dataset containing the variables to extract.
        inf_time (np.ndarray): Array of inferred time steps to match against Norkyst datasets.
        variables (list): List of variable names to extract from both Havbris and Norkyst datasets.
        s_rho_n3 (int): Index for vertical layer selection in the Norkyst datasets (default: 0).
        debug (bool): If True, prints debug information (default: False).

    Returns:
        Tuple[xr.Dataset, xr.Dataset]:
            - `havbris`: Dataset containing the extracted variables and their coordinates from Havbris.
    """
    # Initialize dictionaries to store variables for Havbris and Norkyst
    havbris_data = {}
    # Iterate over all variables to process them
    for variable in variables:
        # Check if the variable exists in the Havbris dataset
        if variable not in ds_havbris.variables:
            raise ValueError(f"Variable '{variable}' not found in the Havbris dataset.")
        # Extract the variable and coordinates from Havbris
        havbris_variable = ds_havbris[variable]
        havbris_lat = ds_havbris['lat']
        havbris_lon = ds_havbris['lon']
        # Add the variable to the Havbris dictionary
        havbris_data[variable] = havbris_variable
        if debug:
            print(f"Extracted variable '{variable}' from Havbris dataset.")
    # Create new datasets for Havbris and Norkyst3 containing the extracted variables and their coordinates
    havbris = xr.Dataset(havbris_data,
                         coords={'lat': havbris_lat,
                                 'lon': havbris_lon})
    if debug:
        print(f"Successfully extracted variables {variables} from Havbris and Norkyst datasets.")
        print(f"Havbris dataset contains variables: {list(havbris.data_vars.keys())}")
    return havbris
###############################################################################################################################
# GET NK AND HB DS OF SELECTED VARIABLES FOR MATCHING TIME-STEPS : 
###############################################################################################################################
def open_dataset_inf(path_to_inf,
                     truth_norkyst3_path = '/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/',
                     truth_file_name_template = "{year}/norkyst800-{year}{month:02d}{day:02d}.nc",
                     variables=["salinity", "temperature", "u_eastward", "v_northward"],
                     s_rho = -1,
                     crop_border = True,
                     debug=False):
    # 1) Get the inference file
    inference_file, inf_time, unique_days, datetime_strings = read_havbris_inferred_nc(path_to_inf, 
                                                                                       debug=debug)
    # 2) Get the Norkyst-3 file
    nk3_datasets = read_norkyst_hindcast_based_on_inferred_nc(truth_norkyst3_path,
                                                              truth_file_name_template,
                                                              unique_days,
                                                              date_format= "%Y-%m-%d",
                                                              debug=debug)
    # 3) Match dates and timesteps (For variables)
    havbris, norkyst3 = get_variables_ds_matching_time(ds_havbris=inference_file,
                                                       ds_norkyst=nk3_datasets,
                                                       inf_time=inf_time,
                                                       variables=variables,
                                                       s_rho_n3=s_rho,
                                                       debug=debug)
    # 4) Crop away the border if True
    if crop_border is True:
        havbris_uten_kant = havbris.isel(Y=slice(25, 1120))
        norkyst_uten_kant = norkyst3.isel(Y=slice(25, 1120))
        havbris_uten_kant = havbris_uten_kant.isel(X=slice(25, 2720))
        norkyst_uten_kant = norkyst_uten_kant.isel(X=slice(25, 2720))
        return havbris_uten_kant, norkyst_uten_kant
    else:
        return havbris, norkyst3
###############################################################################################################################
# GET NK AND HB DS OF SELECTED VARIABLES FOR MATCHING TIME-STEPS MULTIPLE HB FILES : 
###############################################################################################################################
def open_datasets_inf(paths_to_inf,
                     truth_norkyst3_path = '/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/',
                     truth_file_name_template = "{year}/norkyst800-{year}{month:02d}{day:02d}.nc",
                     variables=["salinity", "temperature", "u_eastward", "v_northward"],
                     s_rho = -1,
                     crop_border = True,
                     debug=False):
    # 1) Get the FIRST inference file
    inference_file_0, inf_time, unique_days, datetime_strings = read_havbris_inferred_nc(paths_to_inf[0], 
                                                                                       debug=debug)
    # 2) Get the Norkyst-3 file
    nk3_datasets = read_norkyst_hindcast_based_on_inferred_nc(truth_norkyst3_path,
                                                              truth_file_name_template,
                                                              unique_days,
                                                              date_format= "%Y-%m-%d",
                                                              debug=debug)
    # 3) Match dates and timesteps (For variables)
    havbris_list = []
    havbris_0, norkyst3 = get_variables_ds_matching_time(ds_havbris=inference_file_0,
                                                       ds_norkyst=nk3_datasets,
                                                       inf_time=inf_time,
                                                       variables=variables,
                                                       s_rho_n3=s_rho,
                                                       debug=debug)
    # 4) Get all havbris in paths_to_inf list
    for inf_path in paths_to_inf:
        inf_file  = inf_path.split('/')[-1]
        plt_title = inf_file[-21:-4]
        inference_file, _, _, _ = read_havbris_inferred_nc(inf_path, 
                                                           debug=debug)
        havbris = get_variables_ds_matching_time_havbris(ds_havbris=inference_file,
                                                         variables=variables,
                                                         s_rho_n3=s_rho,
                                                         debug=debug)
        # Add a new dimension for stacking, using the title and file name
        havbris = havbris.expand_dims(dim={"inf_file": [inf_file]})
        havbris = havbris.assign_coords(inf_file=[plt_title])
        havbris_list.append(havbris)
    # Combine all havbris datasets along the inf_file dimension
    havbris_combined = xr.concat(havbris_list, dim="inf_file")
    # 5) Crop away the border if True
    if crop_border is True:
        havbris_combined = havbris_combined.isel(Y=slice(25, 1120), X=slice(25, 2720))
        norkyst3 = norkyst3.isel(Y=slice(25, 1120), X=slice(25, 2720))
    # 6) Return the Norkyst3 dataset (cropped) and the stacked havbris dataset
    return norkyst3, havbris_combined
