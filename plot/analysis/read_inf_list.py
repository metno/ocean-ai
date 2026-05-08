import pandas as pd
import os
import glob
import ast  # To safely evaluate string representations of lists

def get_inference_file_info(infile):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(infile, comment='#')
    # Initialize lists to collect data
    inference_files_paths = []
    inference_run_id      = []
    inferece_epoch        = []
    plot_titles           = []
    # Variables to check for consistency
    inf_date_set   = set()
    inf_length_set = set()
    variables_set  = set()
    for i in df.index:
        inf_path  = df['inference_file'][i]
        # Safely parse the string representation of a path if needed
        if isinstance(inf_path, str):
            try:
                # Handle cases where the path might look like a string with extra quotes
                inf_path = ast.literal_eval(inf_path)
            except (ValueError, SyntaxError):
                pass  # If parsing fails, assume it's already a clean string
        inf_file  = inf_path.split('/')[-1]
        inf_vars  = df['variables'][i]
        plt_title = df['plot_title'][i]
        # Handle default values for plot_title
        if plt_title == '' or plt_title == '*':
            plt_title = inf_file[-21:-4]
        # Handle default values or parse provided variables
        if inf_vars == '' or inf_vars == '*':
            inf_vars = ['salinity', 
                        'temperature', 
                        'u_eastward', 
                        'v_northward']
        else:
            # Safely parse the string representation of a list into an actual list
            if isinstance(inf_vars, str):
                try:
                    inf_vars = ast.literal_eval(inf_vars)  # Convert string to list
                except (ValueError, SyntaxError):
                    raise ValueError(f"Invalid format for variables: {inf_vars}")
            # Ensure variables are sorted for consistency
            inf_vars = sorted([var.strip() for var in inf_vars])
        # Extract information from the file name
        inf_date   = inf_file[0:10]
        inf_length = inf_file[11:14]
        inf_run_id = inf_file[15:20]
        inf_epoch  = inf_file[21:33]
        # Collect the extracted information
        inference_files_paths.append(inf_path)
        inference_run_id.append(inf_run_id)
        inferece_epoch.append(inf_epoch)
        plot_titles.append(plt_title)
        # Add to consistency check sets
        inf_date_set.add(inf_date)
        inf_length_set.add(inf_length)
        variables_set.add(tuple(inf_vars))  # Add variables as a tuple for immutability
    # Check if all inference files have the same date, length, and variables
    if len(inf_date_set) > 1:
        raise ValueError(f"Inconsistent inference dates found: {inf_date_set}")
    if len(inf_length_set) > 1:
        raise ValueError(f"Inconsistent inference lengths found: {inf_length_set}")
    if len(variables_set) > 1:
        raise ValueError(f"Inconsistent variables found: {variables_set}")
    # Prepare the plot dictionary
    plot_dict = {
        'inf_date'            : inf_date_set.pop(),         # Get the single consistent date
        'variables'           : list(variables_set.pop()),  # Convert the single consistent tuple back to a list
        'inf_length'          : inf_length_set.pop(),       # Get the single consistent length
        'number_of_inf_files' : len(inference_files_paths)
    }
    # Return the requested data
    return inference_files_paths, plot_titles, inference_run_id, inferece_epoch, plot_dict

def create_directory(path: str):
        """
        Create a directory if it does not exist, and handle the case where it already exists.
        """
        try:
            # Try to create the directory
            os.makedirs(path, exist_ok=False)
            print(f"Directory '{path}' created successfully.")
        except FileExistsError:
            # Handle the case where the directory already exists
            print(f"Directory '{path}' already exists. Skipping creation.")

