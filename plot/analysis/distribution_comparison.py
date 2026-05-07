import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.animation import FuncAnimation
import xarray as xr  # Assuming you are working with xarray datasets

def plot_distribution(ax, data_norkyst, data_havbris, title, log, xlim=None, ylim=None):
    # Flatten the DataArrays and remove NaNs
    values_norkyst = data_norkyst.values.ravel()
    values_norkyst = values_norkyst[~np.isnan(values_norkyst)]
    values_havbris = data_havbris.values.ravel()
    values_havbris = values_havbris[~np.isnan(values_havbris)]
    # Plot the distributions
    ax.hist(values_norkyst, bins=50, color='lightgrey', histtype='step',       linewidth=3, 
            edgecolor='black',    log=log, alpha=1,   label='Norkyst', zorder=5)
    ax.hist(values_havbris, bins=50, color='steelblue', histtype='stepfilled', linewidth=3, 
            edgecolor='darkblue', log=log, alpha=0.5, label='Havbris', zorder=5)
    # Set x and y limits if specified
    if xlim is not None:
        ax.set_xlim(xlim)
    if ylim is not None:
        ax.set_ylim(ylim)
    # Add labels, title, and legend
    ax.set_title(title, fontsize=16)
    ax.set_xlabel(title, fontsize=14)
    if log is True:
        ax.set_ylabel('Log Frequency', fontsize=14)
    else:
        ax.set_ylabel('Frequency', fontsize=14)
    ax.legend(fontsize=12, loc='upper left')
    ax.grid(True)

def make_dist_plot(timestep,norkyst3,havbris):
    date = norkyst3.isel(time=timestep).time.values
    date_str = str(date)  # Convert to string
    title_date = date_str[0:16]
    # Create a 2x2 subplot
    fig, axes = plt.subplots(2, 2, figsize=(15, 15))
    fig.suptitle(f'Distribution of Variables at Timestep={timestep} on {title_date}', fontsize=22)
    # Plot Temperature
    plot_distribution(axes[0, 0], norkyst3.temperature.isel(time=timestep), havbris.temperature.isel(time=timestep), 'Temperature', log=False)
    # Plot Salinity
    plot_distribution(axes[0, 1], norkyst3.salinity.isel(time=timestep), havbris.salinity.isel(time=timestep), 'Salinity', log=False)
    # Plot U Eastward
    plot_distribution(axes[1, 0], norkyst3.u_eastward.isel(time=timestep), havbris.u_eastward.isel(time=timestep), 'U Eastward', log=False)
    # Plot V Northward
    plot_distribution(axes[1, 1], norkyst3.v_northward.isel(time=timestep), havbris.v_northward.isel(time=timestep), 'V Northward', log=False)
    # Adjust layout and show the plot
    plt.tight_layout(rect=[0, 0, 1, 0.98])  # Leave space for the main title
    plt.show()

def make_dist_plot_log(timestep,norkyst3,havbris):
    date = norkyst3.isel(time=timestep).time.values
    date_str = str(date)  # Convert to string
    title_date = date_str[0:16]
    # Create a 2x2 subplot
    fig, axes = plt.subplots(2, 2, figsize=(15, 15))
    fig.suptitle(f'Distribution of Variables at Timestep={timestep} on {title_date}', fontsize=22)
    # Plot Temperature
    plot_distribution(axes[0, 0], norkyst3.temperature.isel(time=timestep), havbris.temperature.isel(time=timestep), 'Temperature', log=True)
    # Plot Salinity
    plot_distribution(axes[0, 1], norkyst3.salinity.isel(time=timestep), havbris.salinity.isel(time=timestep), 'Salinity', log=True)
    # Plot U Eastward
    plot_distribution(axes[1, 0], norkyst3.u_eastward.isel(time=timestep), havbris.u_eastward.isel(time=timestep), 'U Eastward', log=True)
    # Plot V Northward
    plot_distribution(axes[1, 1], norkyst3.v_northward.isel(time=timestep), havbris.v_northward.isel(time=timestep), 'V Northward', log=True)
    # Adjust layout and show the plot
    plt.tight_layout(rect=[0, 0, 1, 0.98])  # Leave space for the main title
    plt.show()

def plot_dist_animate(norkyst3, havbris, save_name, save_path):
    # Define the update function for the animation
    def update(timestep):
        # Clear the axes for the new frame
        for ax in axes.flat:
            ax.clear()
        # Get the date for the current timestep
        date = norkyst3.isel(time=timestep).time.values
        date_str = str(date)  # Convert to string
        title_date = date_str[0:16]
        # Set the main title for the figure
        fig.suptitle(f'Distribution of Variables at Timestep={timestep} on {title_date}', fontsize=22)
        # Plot Temperature
        plot_distribution(axes[0, 0], norkyst3.temperature.isel(time=timestep), havbris.temperature.isel(time=timestep), 
                        'Temperature', log=False, xlim=(-4,10), ylim=(0,155000))
        # Plot Salinity
        plot_distribution(axes[0, 1], norkyst3.salinity.isel(time=timestep), havbris.salinity.isel(time=timestep), 
                        'Salinity', log=False, xlim=(-2,50), ylim=(0,1.3e6))
        # Plot U Eastward
        plot_distribution(axes[1, 0], norkyst3.u_eastward.isel(time=timestep), havbris.u_eastward.isel(time=timestep), 
                        'U Eastward', log=False, xlim=(-3,3), ylim=(0,1.85e6))
        # Plot V Northward
        plot_distribution(axes[1, 1], norkyst3.v_northward.isel(time=timestep), havbris.v_northward.isel(time=timestep), 
                        'V Northward', log=False, xlim=(-3,3), ylim=(0,1.85e6))
        # Adjust the layout
        plt.tight_layout(rect=[0, 0, 1, 0.98])
    # Initialize the figure and axes
    fig, axes = plt.subplots(2, 2, figsize=(15, 15), facecolor="white")
    # Number of timesteps
    num_timesteps = norkyst3.dims['time']
    # Create the animation
    ani = FuncAnimation(fig, update, frames=num_timesteps, interval=500)  # 500ms between frames
    #plt.show()
    #ani = FuncAnimation(fig, update, frames=range(frame), interval = 400)
    #print('Trying to save it')
    ani.save(f'{save_path}{save_name}.gif', writer="imagemagick")  
    print(f"GIF created and saved: {save_path}{save_name}.gif")
    plt.close(fig)

def plot_dist_log_animate(norkyst3, havbris, save_name, save_path):
    # Define the update function for the animation
    def update(timestep):
        # Clear the axes for the new frame
        for ax in axes.flat:
            ax.clear()
        # Get the date for the current timestep
        date = norkyst3.isel(time=timestep).time.values
        date_str = str(date)  # Convert to string
        title_date = date_str[0:16]
        # Set the main title for the figure
        fig.suptitle(f'Distribution of Variables at Timestep={timestep} on {title_date}', fontsize=22)
        # Plot Temperature
        plot_distribution(axes[0, 0], norkyst3.temperature.isel(time=timestep), havbris.temperature.isel(time=timestep), 
                        'Temperature', log=True, xlim=(-4,10), ylim=(0,155000))
        # Plot Salinity
        plot_distribution(axes[0, 1], norkyst3.salinity.isel(time=timestep), havbris.salinity.isel(time=timestep), 
                        'Salinity', log=True, xlim=(-2,50), ylim=(0,1.3e6))
        # Plot U Eastward
        plot_distribution(axes[1, 0], norkyst3.u_eastward.isel(time=timestep), havbris.u_eastward.isel(time=timestep), 
                        'U Eastward', log=True, xlim=(-3,3), ylim=(0,1.85e6))
        # Plot V Northward
        plot_distribution(axes[1, 1], norkyst3.v_northward.isel(time=timestep), havbris.v_northward.isel(time=timestep), 
                        'V Northward', log=True, xlim=(-3,3), ylim=(0,1.85e6))
        # Adjust the layout
        plt.tight_layout(rect=[0, 0, 1, 0.98])
    # Initialize the figure and axes
    fig, axes = plt.subplots(2, 2, figsize=(15, 15), facecolor="white")
    # Number of timesteps
    num_timesteps = norkyst3.dims['time']
    # Create the animation
    ani = FuncAnimation(fig, update, frames=num_timesteps, interval=500)  # 500ms between frames
    #plt.show()
    #ani = FuncAnimation(fig, update, frames=range(frame), interval = 400)
    #print('Trying to save it')
    ani.save(f'{save_path}{save_name}.gif', writer="imagemagick")  
    print(f"GIF created and saved: {save_path}{save_name}.gif")
    plt.close(fig)

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

def create_distribution_plots(norkyst3, havbris):
    # Get the current working directory
    current_directory = os.getcwd()
    # Combine the current directory and the folder name
    full_path = os.path.join(current_directory, "validation_results/dist_gif")
    # Call the function to create the folder
    create_directory(full_path)
    plot_dist_animate(norkyst3, havbris, 
                    save_name='distribution', 
                    save_path=f'{full_path}/')
    plot_dist_log_animate(norkyst3, havbris, 
                        save_name='distribution_log', 
                        save_path=f'{full_path}/')