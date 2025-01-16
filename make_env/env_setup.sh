#!/bin/bash

cd /pfs/lustrep2/projappl/project_465001629/python-envs
export VIRTUAL_ENV="anemoi-env-trimedge"
if [ ! -d "$VIRTUAL_ENV" ]; then
    mkdir -p $VIRTUAL_ENV/lib $VIRTUAL_ENV/bin
fi

export PYTHONUSERBASE=$VIRTUAL_ENV
export PATH=$PATH:VIRTUAL_ENV/bin

pip install anemoi-training
pip install anemoi-utils
pip install anemoi-models
pip install anemoi-graphs
pip install anemoi-inference
pip install anemoi-registry
pip uninstall anemoi-datasets
pip install /pfs/lustrep2/scratch/project_465001629/anemoi-datasets/.[dev]

