import pandas as pd
import os
import glob
from cycler import cycler
import matplotlib.pyplot as plt

def parse_mlflow_dirs(infile,exp_base_dir='/lustre/storeB/project/fou/hi/foccus/experiments/'):
    # Simple way to get all relevant subdirs for mlflow plots
    # infile should contain lines with: exp_name run_id title
    # Lines starting with # are ignored

    # TODO: use csv for infile and read with pandas
    
    with open(infile, 'r') as f:
        lines = f.readlines()

    plot_dirs = []; titles = []
    for line in lines:
        if not line.startswith('#') and line.split():
            exp_name = line.strip().split()[0]
            run_id_in = line.strip().split()[1]
            title = line.strip().split()[2]
            run_dir = exp_base_dir + f'{exp_name}/logs/mlflow/*/{run_id_in}/*'
            # Expand the path to get all subdirs matching the pattern
            dirs = [d for d in glob.glob(run_dir) if os.path.isdir(d) and 'metrics' in d]
            # Read run_id from path
            run_id = [d.split('/')[-2] for d in dirs] 
            # Expand title list to same length, adding run_id to title if multiple dirs
            
            if len(dirs) > 1:
                sub_title = [title + ' (' + id[:5] + ')' for id in run_id]
            else:
                sub_title = [title]
            titles.extend(sub_title)
            plot_dirs.extend(dirs)
            #print(line.strip())
    return plot_dirs, titles

def mlflow_metadata(dir_in):
    # Read in metadata file from mlflow dir
    meta_file = os.path.join(dir_in, 'meta.yaml')
    run_id = 'unknown'; run_name = 'unknown'
    try:
        with open(meta_file, 'r') as f:
            metadata = f.read()
            if 'run_id:' in metadata:
                run_id = metadata.split('run_id:')[1].split('\n')[0].strip()
            if 'run_name:' in metadata:
                run_name = metadata.split('run_name:')[1].split('\n')[0].strip()
            
            # can also get 'experiment_id:' and 'user_id:'
    except Exception as e:
        print(f'Could not read in metadata from {meta_file}: {e}')
    return run_id, run_name

def read_config_param(dir_in, param_name):
    # Read in config param from mlflow dir
    #config_file = os.path.join(dir_in, '/params/'+param_name)
    config_file = dir_in + '/params/' + param_name
    param_value = 'unknown'
    try:
        with open(config_file, 'r') as f:
            param_value = f.read().strip()
    except Exception as e:
        print(f'Could not read in config param from {config_file}: {e}')
    return param_value

def diff_configs():
    pass

def mlflow_multiple_dirs(dir_list, exp_names, vars_indx, suptitle='',plot_epoch=False):

    # Only plotting these metrics. Ignoring X_epoch if plot_epoch = False
    metrics_list = [
                    'train_mse_loss_step',
                    'train_mse_loss_epoch',
                    'val_mse_loss_step',
                    'val_mse_loss_epoch',                    
                    'lr-AdamW',
                    'epoch',
                    #'rollout'
                    ]
    # val_mse_inside_lam_metric is plotted separately. Only present if finish an epoch (?)
    val_metrics_list = [  # add more variables when expand to 3D
                    'all',
                    'sfc_salinity', 
                    'sfc_u_eastward', 
                    'sfc_v_northward',
                    'sfc_temperature', 
                    'sfc_zeta',
                    ]

    # different styles for each dir
    colors     = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    linestyles = ['-', '--', ':', '-.']

    #Fig 1
    if plot_epoch:
        fig1, ax1 = plt.subplots(3,2, figsize = (15,15))
    else:
        fig1, ax1 = plt.subplots(3,1, figsize = (15,15))
        metrics_list = [m for m in metrics_list if not m.endswith('epoch')]
        
    fig1.subplots_adjust(wspace=0.5, hspace=0.5) # adjust the spacing between subplots: wspace for width and hspace for height
    ax1 = ax1.ravel()
    fig1.suptitle(f'Metrics: {suptitle}', fontweight = 'bold', fontsize =15)
    
    #Fig 2
    fig2, ax2 = plt.subplots(3,2, figsize = (15,12))
    fig2.subplots_adjust(wspace=0.5, hspace=0.5) # adjust the spacing between subplots: wspace for width and hspace for height
    ax2 = ax2.ravel()
    fig2.suptitle(f'Validation metrics: val_mse_inside_lam_metric', fontweight = 'bold', fontsize = 15)

    n=0
    for dir_in, experiment in zip(dir_list, exp_names):
        print(f'Processing directory: {dir_in} with experiment name: {experiment}')
        
        for i, metric in enumerate(metrics_list):
            file_path = os.path.join(dir_in, metric)
            print(metric)

            if os.path.isfile(file_path):
                try:
                    ds = pd.read_csv(f'{file_path}', sep='\s+', names=["ID", "Vals", "Step"])

                except Exception as e:
                    print(f'Could not read in {metric} using Pandas: {e}')
                    continue

                #if lenth of step is 0, then the metric is not logged properly, skip it
                if len(ds["Step"]) == 0:
                    print(f'Skipping {metric} as it has 0 steps logged.')
                    continue

                #plotting
                ax1[i].plot(ds["Step"], ds["Vals"], label=experiment, color=colors[n % len(colors)], linestyle=linestyles[n % len(linestyles)])
                #ax1[i].scatter(ds["Step"], ds["Vals"], marker='x', s=3)  
                if 'loss' in metric:
                    ax1[i].set_yscale('log')  # log scale for loss    

        
        # Validation metrics for variables 
        if not os.path.isdir(os.path.join(f'{dir_in}/val_mse_inside_lam_metric')):
            print(f'No val_mse_inside_lam_metric directory in {dir_in}, skipping variable metrics plotting.')
            n+=1
            continue

        for j, vmetric in enumerate(val_metrics_list):
            file_path = os.path.join(f'{dir_in}/val_mse_inside_lam_metric', vmetric)

            if os.path.isdir(file_path):
                try: 
                    ds_vars = pd.read_csv(f'{file_path}/1', sep='\s+', names=["ID", "Vals", "Step"])

                except Exception as e:
                    print(f'Could not read in {file_path}/1 using Pandas: {e}')
                    continue

                #plotting 
                ax2[j].plot(ds_vars["Step"], ds_vars["Vals"], label=experiment, color=colors[n % len(colors)], linestyle=linestyles[n % len(linestyles)])
                ax2[j].scatter(ds_vars["Step"], ds_vars["Vals"], s = 4, color = 'black')
                  
        n+=1

    # Add legend only once, on the last iteration
    for i in range(len(metrics_list)):
        ax1[i].set_title(f'{metrics_list[i]}', fontweight = 'bold', fontsize=10)  
        ax1[i].set_xlabel(f'Step')
        ax1[i].grid(True, alpha = 0.5)   
        ax1[i].legend() 
        ax2[i].set_yscale('log')

    for j in range(len(val_metrics_list)):
        ax2[j].set_title(f'{val_metrics_list[j]} ', fontweight = 'bold', fontsize = 10)
        ax2[j].set_xlabel(f'Step')
        ax2[j].grid(True, alpha = 0.5)
        ax2[j].legend() 

    plt.tight_layout()
    plt.show()


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
                #print(f'Successfully read in {filename}.')
                #print(f'Start of data: {ds.head()}')

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
    #plt.ion()
    plt.show()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        prog='MLflow plots'
    )

    parser.add_argument(
        '-p', '--path', type=str, required=True, help='Full path to dir where MLflow logs are stored.'
    )
    parser.add_argument(
        '-vi', '--varsindex', type=int, default=1, help='Not sure, ask Malene.'
    )
    parser.add_argument(
        '-t', '--title', type=str, default='MLflow stats', help='Figure title.' 
    )
    args = parser.parse_args()

    mlflow_plots(dir_in=args.path,
                 vars_indx=args.varsindex,
                 suptitle=args.title)

#Example run:
#mlflow_plots('/lustre/storeB/project/fou/hi/foccus/experiments/min-max-all-2017-24/mlflow/187656373550779284/90ed5f0579a94e1cacec799fe5fcc6f1/metrics', 1, 'Min-max-all-2017-24')