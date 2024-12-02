#!/bin/bash
#$ -N ocean-training
#$ -b n
#$ -S /bin/bash
#$ -l h_data=10G
#$ -l h_rss=10G
#$ -l h_rt=01:00:00
#$ -q gpu-r8.q
#$ -l h=gpu-03.ppi.met.no
#$ -o /lustre/storeB/project/fou/hi/foccus/mateuszm/anemoi/logs/OUT_$JOB_NAME.$JOB_ID
#$ -e /lustre/storeB/project/fou/hi/foccus/mateuszm/anemoi/logs/ERR_$JOB_NAME.$JOB_ID

DIR=/lustre/storeB/project/fou/hi/foccus/mateuszm/aifs-mono-ocean//lustre/storeB/project/fou/hi/foccus/mateuszm/anemoi/
export HYDRA_FULL_ERROR=1
conda deactivate
source /lustre/storeB/project/fou/hi/foccus/python-envs/new-anemoi-env/bin/activate
anemoi-training train --config-name=//lustre/storeB/project/fou/hi/foccus/mateuszm/anemoi/training/config.yaml


#conda deactivate
#source /lustre/storeB/project/fou/hi/foccus/mateuszm/testing_envs/anemoi-env/bin/activate
#nemoi-training train --config-name=//lustre/storeB/project/fou/hi/foccus/mateuszm/aifs-mono-ocean/aifs/config/mateusz_metno_ocean.yaml
#python $PYTHON_SCRIPT