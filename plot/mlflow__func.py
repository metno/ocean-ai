import pandas as pd
import os
import matplotlib.pyplot as plt

#Plots one and one statistical plot from the MLFlow data.
#dir_in - the directory you want to plot from. 
def single_plots_mlflow(dir_in):
    filenames = os.listdir(dir_in) #A list with the files inside a given directory defined by dir_in
    for i, filename in enumerate(filenames):
        file_path = os.path.join(dir_in, filename)
        if os.path.isdir(file_path): #skips directories
            continue

        if filename.endswith(".swp"): #Skips .swp files
            continue
        else:
            #Reads in all files not swp and directories
            try:
                ds = pd.read_csv(f'{file_path}', delim_whitespace=True, names=["ID", "Vals", "Step"])
                print(f'Successfully read in {filename}. Directories and .swp files are ignored.')
                print(f'Start of data: {ds.head()}')
            #If one file is not read this print statement will inform you
            except Exception as e:
                print(f'Could not read in {filename} using Pandas: {e}')
                continue
        #Plotting the datsets
        plt.plot(ds["Step"], ds["Vals"])
        plt.scatter(ds["Step"], ds["Vals"], s = 6)
        plt.grid(True)
        plt.xlabel("Step")
        plt.title(f'{filename}')
        plt.tight_layout()
        plt.show()
"""
example of use:
from mlflow__func import single_plots_mlflow
single_plots_mlflow('/lustre/storeB/project/fou/hi/foccus/experiments/min-max-all-2017-24/mlflow/187656373550779284/90ed5f0579a94e1cacec799fe5fcc6f1/metrics'
"""


#SUBPLOTS - issue as it plots all files within a directory, so directories etc. come up as empty subplots.
def mlflow_subs(dir_in):
    fig, ax = plt.subplots(9, figsize = (10,15))
    filenames = os.listdir(dir_in)
    print(filenames)
    for i, filename in enumerate(filenames):
        file_path = os.path.join(dir_in, filename)
        if os.path.isdir(file_path):
            continue
        if filename.endswith(".swp"):
            continue

        if i >= len(ax):
            print(f'Files after {len(ax)} are skipped in subplot. Increase amount of subplots to include more files')
            break
        #Skip the rest of the files if it exceeds the number of subplots
        else:
            try:
                ds = pd.read_csv(f'{file_path}', delim_whitespace=True, names=["ID", "Vals", "Step"])
                print(f'Successfully read in {filename}. Directories and .swp files are ignored.')
                print(f'Start of data: {ds.head()}')
                ax[i].plot(ds["Step"], ds["Vals"])
                ax[i].scatter(ds["Step"], ds["Vals"], s = 6)
                ax[i].grid(True)
                ax[i].set_xlabel("Step")
                ax[i].set_title(f'{filename}')
            except Exception as e:
                print(f'Could not read in {filename} using Pandas: {e}')
                continue 
    plt.suptitle(f'Min-max-all-2017-24')
    plt.tight_layout()
    plt.show()