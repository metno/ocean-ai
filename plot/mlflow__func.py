import pandas as pd
import os
import matplotlib.pyplot as plt

def mlflow_plots(dir_in, vars_indx, suptitle):

    #Fig 1
    fig1, ax1 = plt.subplots(2,4, figsize = (20,15))
    fig1.subplots_adjust(wspace=0.5, hspace=0.5) # adjust the spacing between subplots: wspace for width and hspace for height
    ax1 = ax1.ravel()
    #Fig 2
    fig2, ax2 = plt.subplots(3,2, figsize = (15,12))
    fig2.subplots_adjust(wspace=0.5, hspace=0.5) # adjust the spacing between subplots: wspace for width and hspace for height
    ax2 = ax2.ravel()

    filenames = os.listdir(dir_in)
    print(filenames)
    filenames = [f for f in filenames if not f.endswith('metric') and not f.endswith('swp')] #manually removing the directory and the swp files from iteration in the following loop
    for indx, filnavn in enumerate(filenames):
        print(f'{filnavn}: Index {indx}') #check if the filenames are indexed correctly in the plots and that directories and swp files are removed from the iteration. 
    for i, filename in enumerate(filenames):
        file_path = os.path.join(dir_in, filename)
        
        #Ignoring directories
        if os.path.isdir(file_path):
            print(f'Directories ignored {filename}')
            continue

        #Ignoring swp files
        if filename.endswith(".swp"):
            print(f'Ignoring files ending with swp.')
            continue

        #Read in files selected files from filenames using pandas (filename in enumerate)
        else:
            try:
                ds = pd.read_csv(f'{file_path}', sep='\s+', names=["ID", "Vals", "Step"])
                print(f'Successfully read in {filename}.')
                print(f'Start of data: {ds.head()}')

            except Exception as e:
                print(f'Could not read in {filename} using Pandas: {e}')
                continue

        #plotting
        ax1[i].plot(ds["Step"], ds["Vals"])
        ax1[i].scatter(ds["Step"], ds["Vals"], s = 4, color = 'black')
        ax1[i].set_title(f'{filename}', fontweight = 'bold', fontsize=10)
        ax1[i].set_xlabel(f'Step')
        ax1[i].grid(True, alpha = 0.5)    

    #Variables     
    vars_file_path = os.path.join(f'{dir_in}/val_mse_inside_lam_metric')
    vars_dir = os.listdir(vars_file_path)
    print(vars_dir)
    for j, vars_filename in enumerate(vars_dir):
        dir_vars = os.path.join(f'{vars_file_path}/{vars_filename}/{vars_indx}')

        #Read in files selected files from filenames using pandas (filename in enumerate)
        try: 
            ds_vars = pd.read_csv(f'{dir_vars}', sep='\s+', names=["ID", "Vals", "Step"])
            print(f'Successfully read in {vars_filename}.')
            print(f'Start of data: {ds_vars.head()}')

        except Exception as e:
            print(f'Could not read in {vars_dir} using Pandas: {e}')
            continue

        #plotting 
        ax2[j].plot(ds_vars["Step"], ds_vars["Vals"])
        ax2[j].scatter(ds_vars["Step"], ds_vars["Vals"], s = 4, color = 'black')
        ax2[j].set_title(f'{vars_filename} ', fontweight = 'bold', fontsize = 10)
        ax2[j].set_xlabel(f'Step')
        ax2[j].grid(True, alpha = 0.5)

    fig1.suptitle(f'{suptitle}', fontweight = 'bold', fontsize =15)
    fig1.delaxes(ax1[7])
    fig2.suptitle(f'{suptitle}', fontweight = 'bold', fontsize = 15)

    plt.tight_layout()
    plt.ion()
    plt.show()

#Example run:
#mlflow_plots('/lustre/storeB/project/fou/hi/foccus/experiments/min-max-all-2017-24/mlflow/187656373550779284/90ed5f0579a94e1cacec799fe5fcc6f1/metrics', 1, 'Min-max-all-2017-24')