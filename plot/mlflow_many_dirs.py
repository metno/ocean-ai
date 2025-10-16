import sys
sys.path.append('../')
from mlflow__func import mlflow_multiple_dirs, get_mlflow_dirs, get_mlflow_metadata, get_config_param

infile = '../mlflow/experiment_list.csv' # default exp. base_dir = '/lustre/storeB/project/fou/hi/foccus/experiments/'
mlflow_dirs, titles = get_mlflow_dirs(infile)

#--------
# This is where you can configure which runs to include in the plot,
# and also modify the titles with config metadata.
print("\nWhich runs to plot?")
mlflow_dirs_short = []; titles_short = []
for dir,title in zip(mlflow_dirs,titles):
    run_id, run_name = get_mlflow_metadata(dir+ '/../')
    lr = get_config_param(dir+ '/../', 'config.training.lr.rate')
    max_steps = get_config_param(dir+ '/../', 'config.training.max_steps')

    # Add exceptions to exclude certain runs & make better titles for plotting
    # ex: excluding 6.25e-2 runs since they are very noisy
    if lr != 'unknown' and max_steps != 'unknown' and float(lr) != 6.25E-2: # and 'E-2' not in run_name:
        titles_short.append(f'{run_name}, lr={lr}, max_steps={max_steps}')
        mlflow_dirs_short.append(dir)
    else:
        print(f'  Excluding {title}')
print(f"Plotting {len(mlflow_dirs_short)} mlflow directories.")
#--------

# Save figures as files instead of showing them interactively.
# include full path in name, else saved to current dir. 
base_figname = 'mlflow_learning_rate'
mlflow_multiple_dirs(mlflow_dirs_short, titles_short, suptitle='many dirs',figname=base_figname)