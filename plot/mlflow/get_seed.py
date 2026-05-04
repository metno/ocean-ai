import os
from mlflow__func import get_mlflow_dirs
import re

infile = '../mlflow/experiment_list.csv'
mlflow_dirs, titles = get_mlflow_dirs(infile)

for dir in mlflow_dirs:
    dir = re.sub('metrics', 'params', dir)
    files = os.listdir(dir)
    if 'metadata.seed' in files:
        with open(dir+'/'+'metadata.seed', 'r') as f:
            seed = f.readlines()[0]
            print(dir)
            print(seed)
            print('*******************')