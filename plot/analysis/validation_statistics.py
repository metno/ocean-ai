###############################################################################################################################
# IMPORT NECESSARY PACKAGES : 
###############################################################################################################################
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import os
import pandas as pd
import matplotlib.dates as mdates
from typing import Tuple, Optional, Union, List

def calculate_mae(norkyst_values, havbris_values):
    '''# Flatten and clean the data
    norkyst_values = norkyst3_ts_data.values.ravel()
    havbris_values = havbris_ts_data.values.ravel()
    mask = ~np.isnan(norkyst_values) & ~np.isnan(havbris_values)
    norkyst_values = norkyst_values[mask]
    havbris_values = havbris_values[mask]'''
    # Calculate MAE
    mae = np.mean(np.abs(norkyst_values - havbris_values))
    #print(f"Mean Absolute Error : {mae:.2f}")
    return mae

def calculate_rmse(norkyst_values, havbris_values):
    '''# Flatten and clean the data
    norkyst_values = norkyst3_ts_data.values.ravel()
    havbris_values = havbris_ts_data.values.ravel()
    mask = ~np.isnan(norkyst_values) & ~np.isnan(havbris_values)
    norkyst_values = norkyst_values[mask]
    havbris_values = havbris_values[mask]'''
    # Calculate RMSE
    rmse = np.sqrt(np.mean((norkyst_values - havbris_values) ** 2))
    #print(f"Root Mean Square Error : {rmse:.2f}")
    return rmse

def calculate_nmb(norkyst_values, havbris_values):
    '''# Flatten and clean the data
    norkyst_values = norkyst3_ts_data.values.ravel()
    havbris_values = havbris_ts_data.values.ravel()
    mask = ~np.isnan(norkyst_values) & ~np.isnan(havbris_values)
    norkyst_values = norkyst_values[mask]
    havbris_values = havbris_values[mask]'''
    # Calculate NMB
    nmb = np.sum(havbris_values - norkyst_values) / np.sum(norkyst_values)
    #print(f"Normalized Mean Bias : {nmb:.2%}")
    return nmb

def calculate_pearson_correlation(norkyst_values, havbris_values):
    """
    Calculate the Pearson correlation coefficient manually.
    Formula: r = cov(x, y) / (std(x) * std(y))
    """
    '''# Step 1: Flatten the DataArrays
    norkyst_values = norkyst3_ts_data.values.ravel()
    havbris_values = havbris_ts_data.values.ravel()
    # Step 2: Remove NaNs in a pairwise manner
    mask = ~np.isnan(norkyst_values) & ~np.isnan(havbris_values)
    norkyst_values = norkyst_values[mask]
    havbris_values = havbris_values[mask]'''
    x = norkyst_values
    y = havbris_values
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    covariance = np.mean((x - x_mean) * (y - y_mean))
    std_x = np.std(x)
    std_y = np.std(y)
    return covariance / (std_x * std_y)

def calculate_stats_per_variable(norkyst3_ts_data,havbris_ts_data):
    # Step 1: Flatten the DataArray
    values_nk = norkyst3_ts_data.values.ravel()
    values_hb = havbris_ts_data.values.ravel()
    # Step 2: Remove missing values (if NaNs are present)
    mask = ~np.isnan(values_nk) & ~np.isnan(values_hb)
    values_nk = values_nk[mask]
    values_hb = values_hb[mask]
    #values_nk = values_nk[~np.isnan(values_nk)]
    #values_hb = values_hb[~np.isnan(values_hb)]
    # Step 3: Calculate basic statistics 
    mean_value_nk = np.mean(values_nk)
    median_value_nk = np.median(values_nk)
    std_dev_nk = np.std(values_nk)
    mean_value_hb = np.mean(values_hb)
    median_value_hb = np.median(values_hb)
    std_dev_hb = np.std(values_hb)
    #print("Basic statistics :")
    #print(f"NORKYST-3 : Mean: {mean_value_nk:.2f}, Median: {median_value_nk:.2f}, Standard Deviation: {std_dev_nk:.2f}")
    #print(f"HAVBRIS   : Mean: {mean_value_hb:.2f}, Median: {median_value_hb:.2f}, Standard Deviation: {std_dev_hb:.2f}")
    #print()
    # Step 4: MAE, RMSE, NMB 
    #print("MAE, RMSE, NMB : ")
    mae  = calculate_mae(values_nk, values_hb)
    rmse = calculate_rmse(values_nk, values_hb)
    nmb  = calculate_nmb(values_nk, values_hb)
    #print()
    # Step 5: Correlation
    #print("Correlation :")
    corr = calculate_pearson_correlation(values_nk, values_hb)
    #print(f"Pearson Correlation : {corr:.2f}")
    # Return values
    return mean_value_nk, median_value_nk, std_dev_nk, mean_value_hb, median_value_hb, std_dev_hb, mae, rmse, nmb, corr

def csv_stat_file_per_variable(norkyst3, havbris, variable, save_path, save_name):
    """
    Generate a CSV file containing statistical metrics for a given variable
    across timesteps for two datasets: `norkyst3` and `havbris`.

    Parameters:
        norkyst3: xarray.Dataset
            The first dataset containing the variable to analyze.
        havbris: xarray.Dataset
            The second dataset containing the variable to analyze.
        variable: str
            The name of the variable to analyze.
        save_path: str
            The directory to save the CSV file.
        save_name: str
            The name of the CSV file (without the .csv extension).
    """
    # Prepare a list to store results for each timestep
    results = []
    # Loop through each timestep
    num_timesteps = norkyst3.dims['time']
    for timestep in range(num_timesteps):
        # Extract the date for the current timestep
        date = norkyst3.isel(time=timestep).time.values
        date_str = str(date)  # Convert to string
        title_date = date_str[0:16]  # Format date string (optional)
        # Calculate statistics for the current timestep
        mean_value_nk, median_value_nk, std_dev_nk, mean_value_hb, median_value_hb, std_dev_hb, mae, rmse, nmb, corr = calculate_stats_per_variable(
            norkyst3[variable].isel(time=timestep),
            havbris[variable].isel(time=timestep)
        )
        # Append the results for the current timestep to the list
        results.append({
            "Date": title_date,
            "Mean_NK": mean_value_nk,
            "Median_NK": median_value_nk,
            "StdDev_NK": std_dev_nk,
            "Mean_HB": mean_value_hb,
            "Median_HB": median_value_hb,
            "StdDev_HB": std_dev_hb,
            "MAE": mae,
            "RMSE": rmse,
            "NMB": nmb,
            "Correlation": corr
        })
    # Convert the results list into a pandas DataFrame
    df = pd.DataFrame(results)
    # Save the DataFrame to a CSV file
    csv_file_path = f"{save_path}/{save_name}.csv"
    df.to_csv(csv_file_path, index=False)
    print(f"CSV file saved to: {csv_file_path}")
    return df

def csv_stat_file_per_variable_per_inf_file(norkyst3, havbris, variable, save_path):
    """
    Generate CSV files containing statistical metrics for a given variable
    across timesteps for Norkyst3 and multiple Havbris models.

    Parameters:
        norkyst3: xarray.Dataset
            The first dataset containing the variable to analyze.
        havbris: xarray.Dataset
            The second dataset containing the variable to analyze (with `inf_file` dimension).
        variable: str
            The name of the variable to analyze.
        save_path: str
            The directory to save the CSV files.
    """
    num_timesteps = norkyst3.dims["time"]
    inf_files = havbris.coords["inf_file"].values  # Get all `inf_file` names
    for inf_file in inf_files:
        # Select the specific `inf_file`
        havbris_subset = havbris.sel(inf_file=inf_file)
        # Prepare a list to store results for each timestep
        results = []
        # Loop through each timestep
        for timestep in range(num_timesteps):
            # Extract the date for the current timestep
            date = norkyst3.isel(time=timestep).time.values
            date_str = str(date)  # Convert to string
            title_date = date_str[0:16]  # Format date string (optional)
            # Calculate statistics for the current timestep
            mean_value_nk, median_value_nk, std_dev_nk, mean_value_hb, median_value_hb, std_dev_hb, mae, rmse, nmb, corr = calculate_stats_per_variable(
                norkyst3[variable].isel(time=timestep),
                havbris_subset[variable].isel(time=timestep),
            )
            # Append the results for the current timestep to the list
            results.append({
                "Date": title_date,
                "Mean_NK": mean_value_nk,
                "Median_NK": median_value_nk,
                "StdDev_NK": std_dev_nk,
                "Mean_HB": mean_value_hb,
                "Median_HB": median_value_hb,
                "StdDev_HB": std_dev_hb,
                "MAE": mae,
                "RMSE": rmse,
                "NMB": nmb,
                "Correlation": corr,
            })
        # Convert the results list into a pandas DataFrame
        df = pd.DataFrame(results)
        # Save the DataFrame to a CSV file
        csv_file_name = f"{inf_file}_{variable}.csv"
        csv_file_path = f"{save_path}/{csv_file_name}"
        df.to_csv(csv_file_path, index=False)
        print(f"CSV file saved to: {csv_file_path}")
    print("All CSV files have been generated.")

def csv_stat_file_per_variable_combined(norkyst3, havbris, variable, save_path):
    """
    Generate a single CSV file containing statistical metrics for a given variable
    across timesteps for Norkyst3 and multiple Havbris models.

    Parameters:
        norkyst3: xarray.Dataset
            The first dataset containing the variable to analyze.
        havbris: xarray.Dataset
            The second dataset containing the variable to analyze (with `inf_file` dimension).
        variable: str
            The name of the variable to analyze.
        save_path: str
            The directory to save the CSV file.
    """
    num_timesteps = norkyst3.dims["time"]
    inf_files = havbris.coords["inf_file"].values  # Get all `inf_file` names
    all_results = []  # List to store results from all inf_files
    for inf_file in inf_files:
        # Select the specific `inf_file`
        havbris_subset = havbris.sel(inf_file=inf_file)
        # Loop through each timestep
        for timestep in range(num_timesteps):
            # Extract the date for the current timestep
            date = norkyst3.isel(time=timestep).time.values
            date_str = str(date)  # Convert to string
            title_date = date_str[0:16]  # Format date string (optional)
            # Calculate statistics for the current timestep
            mean_value_nk, median_value_nk, std_dev_nk, mean_value_hb, median_value_hb, std_dev_hb, mae, rmse, nmb, corr = calculate_stats_per_variable(
                norkyst3[variable].isel(time=timestep),
                havbris_subset[variable].isel(time=timestep),
            )
            # Append the results for the current timestep and inf_file to the list
            all_results.append({
                "Date": title_date,
                "inf_file": inf_file,
                "Mean_NK": mean_value_nk,
                "Median_NK": median_value_nk,
                "StdDev_NK": std_dev_nk,
                "Mean_HB": mean_value_hb,
                "Median_HB": median_value_hb,
                "StdDev_HB": std_dev_hb,
                "MAE": mae,
                "RMSE": rmse,
                "NMB": nmb,
                "Correlation": corr,
            })
    # Convert the combined results list into a pandas DataFrame
    df = pd.DataFrame(all_results)
    # Save the DataFrame to a single CSV file
    csv_file_name = f"combined_{variable}_stats.csv"
    csv_file_path = f"{save_path}/{csv_file_name}"
    df.to_csv(csv_file_path, index=False)
    print(f"Combined CSV file saved to: {csv_file_path}")
    print("CSV file with all inf_files has been generated.")
    return df

def plot_statistics_combined_show(df, variable):
    """
    Creates a single 2x3 subplot figure:
    - First row: Mean, Median, and Standard Deviation for NK (green) and HB (blue).
    - Second row: MAE & RMSE, NMB, and Correlation.

    Parameters:
        df: pandas.DataFrame
            The DataFrame containing the statistical metrics.
        variable: str
            The name of the variable to use as the title.
    """
    # Convert the "Date" column to datetime for proper plotting
    df["Date"] = pd.to_datetime(df["Date"])

    # Create a 2x3 subplot layout
    fig, axes = plt.subplots(2, 3, figsize=(18, 12), sharex=True)
    fig.suptitle(f"Statistics for {variable}", fontsize=20)

    ### First Row (Mean, Median, StdDev) ###
    # Mean
    axes[0, 0].plot(df["Date"], df["Mean_NK"], color="green", label="Norkyst-3")
    axes[0, 0].plot(df["Date"], df["Mean_HB"], color="blue", label="Havbris")
    axes[0, 0].set_title("Mean")
    axes[0, 0].set_ylabel(variable)
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    # Median
    axes[0, 1].plot(df["Date"], df["Median_NK"], color="green", label="Norkyst-3")
    axes[0, 1].plot(df["Date"], df["Median_HB"], color="blue", label="Havbris")
    axes[0, 1].set_title("Median")
    axes[0, 1].legend()
    axes[0, 1].grid(True)

    # Standard Deviation
    axes[0, 2].plot(df["Date"], df["StdDev_NK"], color="green", label="Norkyst-3")
    axes[0, 2].plot(df["Date"], df["StdDev_HB"], color="blue", label="Havbris")
    axes[0, 2].set_title("Standard Deviation")
    axes[0, 2].legend()
    axes[0, 2].grid(True)

    ### Second Row (MAE & RMSE, NMB, Correlation) ###
    # MAE and RMSE
    axes[1, 0].plot(df["Date"], df["MAE"], label="MAE", color="red")
    axes[1, 0].plot(df["Date"], df["RMSE"], label="RMSE", color="orange")
    axes[1, 0].set_title("MAE and RMSE")
    axes[1, 0].set_ylabel("Error Metrics")
    axes[1, 0].legend()
    axes[1, 0].grid(True)

    # NMB
    axes[1, 1].plot(df["Date"], df["NMB"], label="NMB", color="purple")
    axes[1, 1].set_title("Normalized Mean Bias")
    axes[1, 1].set_ylabel("NMB")
    axes[1, 1].legend()
    axes[1, 1].grid(True)

    # Correlation
    axes[1, 2].plot(df["Date"], df["Correlation"], label="Correlation", color="brown")
    axes[1, 2].set_title("Correlation")
    axes[1, 2].set_ylabel("Correlation")
    axes[1, 2].legend()
    axes[1, 2].grid(True)

    # Set x-axis label for all subplots in the last row
    for ax in axes[1, :]:
        ax.set_xlabel("Date")

    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Leave space for the suptitle
    plt.show()

def plot_statistics_combined(df, variable, save_path=None, save_name=None):
    """
    Creates a single 2x3 subplot figure and optionally saves it to a file:
    - First row: Mean, Median, and Standard Deviation for NK (green) and HB (blue).
    - Second row: MAE & RMSE, NMB, and Correlation.

    Parameters:
        df: pandas.DataFrame
            The DataFrame containing the statistical metrics.
        variable: str
            The name of the variable to use as the title.
        save_path: str or None
            The file path to save the plot. If None, the plot will not be saved.
    """
    # Convert the "Date" column to datetime for proper plotting
    df["Date"] = pd.to_datetime(df["Date"])

    # Create a 2x3 subplot layout
    fig, axes = plt.subplots(2, 3, figsize=(18, 12), sharex=True, facecolor="white")
    fig.suptitle(f"Statistics for {variable}", fontsize=20)

    ### First Row (Mean, Median, StdDev) ###
    # Mean
    axes[0, 0].plot(df["Date"], df["Mean_NK"], color="green", label="Norkyst-3")
    axes[0, 0].plot(df["Date"], df["Mean_HB"], color="blue", label="Havbris")
    axes[0, 0].set_title("Mean")
    axes[0, 0].set_ylabel(variable)
    axes[0, 0].legend()
    axes[0, 0].grid(True)

    # Median
    axes[0, 1].plot(df["Date"], df["Median_NK"], color="green", label="Norkyst-3")
    axes[0, 1].plot(df["Date"], df["Median_HB"], color="blue", label="Havbris")
    axes[0, 1].set_title("Median")
    axes[0, 1].legend()
    axes[0, 1].grid(True)

    # Standard Deviation
    axes[0, 2].plot(df["Date"], df["StdDev_NK"], color="green", label="Norkyst-3")
    axes[0, 2].plot(df["Date"], df["StdDev_HB"], color="blue", label="Havbris")
    axes[0, 2].set_title("Standard Deviation")
    axes[0, 2].legend()
    axes[0, 2].grid(True)

    ### Second Row (MAE & RMSE, NMB, Correlation) ###
    # MAE and RMSE
    axes[1, 0].plot(df["Date"], df["MAE"], label="MAE", color="red")
    axes[1, 0].plot(df["Date"], df["RMSE"], label="RMSE", color="orange")
    axes[1, 0].set_title("MAE and RMSE")
    axes[1, 0].set_ylabel("Error Metrics")
    axes[1, 0].legend()
    axes[1, 0].grid(True)

    # NMB
    axes[1, 1].plot(df["Date"], df["NMB"], label="NMB", color="purple")
    axes[1, 1].set_title("Normalized Mean Bias")
    axes[1, 1].set_ylabel("NMB")
    axes[1, 1].legend()
    axes[1, 1].grid(True)

    # Correlation
    axes[1, 2].plot(df["Date"], df["Correlation"], label="Correlation", color="brown")
    axes[1, 2].set_title("Correlation")
    axes[1, 2].set_ylabel("Correlation")
    axes[1, 2].legend()
    axes[1, 2].grid(True)

    # Set x-axis label for all subplots in the last row
    for ax in axes[1, :]:
        ax.set_xlabel("Date")

    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Leave space for the suptitle

    if save_path:
        # Save the plot to the specified path
        plt.savefig(f"{save_path}/{save_name}.png", format="png", dpi=300)
        print(f"Plot saved to: {save_path}")
        plt.close(fig)
    else:
        # Show the plot if no save_path is provided
        plt.show()

def plot_statistics_combined_multiple_inf(df, variable, save_path=None):
    """
    Creates a single 2x3 subplot figure and optionally saves it to a file:
    - First row: Mean, Median, and Standard Deviation for NK (green) and HB (one line per `inf_file`).
    - Second row: MAE & RMSE, NMB, and Correlation (one line per `inf_file`).

    Parameters:
        df: pandas.DataFrame
            The DataFrame containing the statistical metrics.
        variable: str
            The name of the variable to use as the title.
        save_path: str or None
            The file path to save the plot. If None, the plot will not be saved.
    """
    # Convert the "Date" column to datetime for proper plotting
    df["Date"] = pd.to_datetime(df["Date"])
    # Get unique `inf_file` values
    inf_files = df["inf_file"].unique()
    # Assign a unique color for each `inf_file`
    colors = plt.cm.tab10.colors  # Use a colormap (up to 10 unique colors)
    color_map = {inf_file: colors[i % len(colors)] for i, inf_file in enumerate(inf_files)}
    # Filter the data for the first `inf_file` to use for Mean_NK, Median_NK, and StdDev_NK
    first_inf_file = inf_files[0]
    nk_data = df[df["inf_file"] == first_inf_file]  # Use data from the first `inf_file` for NK metrics
    # Create a 2x3 subplot layout
    fig, axes = plt.subplots(2, 3, figsize=(18, 12), sharex=True, facecolor="white")
    fig.suptitle(f"Statistics for {variable}", fontsize=20)
    ### First Row (Mean, Median, StdDev) ###
    # Mean
    axes[0, 0].plot(nk_data["Date"], nk_data["Mean_NK"], color="green", label="Norkyst-3")
    for inf_file in inf_files:
        subset = df[df["inf_file"] == inf_file]
        axes[0, 0].plot(subset["Date"], subset["Mean_HB"], label=f"Havbris ({inf_file})", color=color_map[inf_file])
    axes[0, 0].set_title("Mean")
    axes[0, 0].set_ylabel(variable)
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    # Median
    axes[0, 1].plot(nk_data["Date"], nk_data["Median_NK"], color="green", label="Norkyst-3")
    for inf_file in inf_files:
        subset = df[df["inf_file"] == inf_file]
        axes[0, 1].plot(subset["Date"], subset["Median_HB"], label=f"Havbris ({inf_file})", color=color_map[inf_file])
    axes[0, 1].set_title("Median")
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    # Standard Deviation
    axes[0, 2].plot(nk_data["Date"], nk_data["StdDev_NK"], color="green", label="Norkyst-3")
    for inf_file in inf_files:
        subset = df[df["inf_file"] == inf_file]
        axes[0, 2].plot(subset["Date"], subset["StdDev_HB"], label=f"Havbris ({inf_file})", color=color_map[inf_file])
    axes[0, 2].set_title("Standard Deviation")
    axes[0, 2].legend()
    axes[0, 2].grid(True)
    ### Second Row (MAE & RMSE, NMB, Correlation) ###
    # MAE and RMSE
    for inf_file in inf_files:
        subset = df[df["inf_file"] == inf_file]
        axes[1, 0].plot(subset["Date"], subset["MAE"], label=f"MAE ({inf_file})", linestyle="--", color=color_map[inf_file])
        axes[1, 0].plot(subset["Date"], subset["RMSE"], label=f"RMSE ({inf_file})", linestyle="-", color=color_map[inf_file])
    axes[1, 0].set_title("MAE and RMSE")
    axes[1, 0].set_ylabel("Error Metrics")
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    # NMB
    for inf_file in inf_files:
        subset = df[df["inf_file"] == inf_file]
        axes[1, 1].plot(subset["Date"], subset["NMB"], label=f"NMB ({inf_file})", color=color_map[inf_file])
    axes[1, 1].set_title("Normalized Mean Bias")
    axes[1, 1].set_ylabel("NMB")
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    # Correlation
    for inf_file in inf_files:
        subset = df[df["inf_file"] == inf_file]
        axes[1, 2].plot(subset["Date"], subset["Correlation"], label=f"Correlation ({inf_file})", color=color_map[inf_file])
    axes[1, 2].set_title("Correlation")
    axes[1, 2].set_ylabel("Correlation")
    axes[1, 2].legend()
    axes[1, 2].grid(True)
    # Set x-axis label for all subplots in the last row and format the date
    for ax in axes[1, :]:
        ax.set_xlabel("Date")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%y %H"))  # Format as dd-mm-yy hh
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)  # Rotate x-axis labels by 45 degrees
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Leave space for the suptitle
    if save_path:
        # Save the plot to the specified path
        plt.savefig(f"{save_path}/{variable}_stats.png", format="png", dpi=300)
        print(f"Plot saved to: {save_path}/{variable}_stats.png")
        plt.close(fig)
    else:
        # Show the plot if no save_path is provided
        plt.show()

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

def create_stat_csv_plot(norkyst3, havbris):
    variables = ['salinity','temperature','u_eastward','v_northward']
    for variable in variables:
        df = csv_stat_file_per_variable(norkyst3, havbris, variable, 
                                        '/lustre/storeB/project/fou/hi/foccus/ingvild/ocean-ai/plot/notebooks/csv_output', f'stat_{variable}')
        plot_statistics_combined(df, variable=variable, 
                                     save_path='/lustre/storeB/project/fou/hi/foccus/ingvild/ocean-ai/plot/notebooks/csv_output/',
                                     save_name=f'stat_{variable}')
        
def create_stat_csv_plot_multiple_inf(norkyst3, havbris, variables):
    # Get the current working directory
    current_directory = os.getcwd()
    # Combine the current directory and the folder name
    full_path1 = os.path.join(current_directory, "validation_results/stat_csv")
    full_path2 = os.path.join(current_directory, "validation_results/stat_png")
    # Call the function to create the folder
    create_directory(full_path1)
    create_directory(full_path2)
    for variable in variables:
        df = csv_stat_file_per_variable_combined(norkyst3, havbris, variable, full_path1)
        plot_statistics_combined_multiple_inf(df, variable, full_path2)