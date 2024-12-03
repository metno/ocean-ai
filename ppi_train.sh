#!/bin/bash
#$ -N ocean-training
#$ -b n
#$ -S /bin/bash
#$ -l h_data=20G
#$ -l h_rss=20G
#$ -l h_rt=01:00:00
#$ -q gpu-r8.q
#$ -l h=gpu-04.ppi.met.no
#$ -o /lustre/storeB/project/fou/hi/foccus/mateuszm/OceanAI/logs/OUT_$JOB_NAME.$JOB_ID
#$ -e /lustre/storeB/project/fou/hi/foccus/mateuszm/OceanAI/logs/ERR_$JOB_NAME.$JOB_ID

DIR=/lustre/storeB/project/fou/hi/foccus/mateuszm/OceanAI/
export HYDRA_FULL_ERROR=1
export ANEMOI_BASE_SEED=1337420
conda deactivate
source /lustre/storeB/project/fou/hi/foccus/python-envs/new-anemoi-env/bin/activate
anemoi-training train --config-dir=//lustre/storeB/project/fou/hi/foccus/mateuszm/OceanAI/training/ --config-name=master.yaml


#conda deactivate
#source /lustre/storeB/project/fou/hi/foccus/mateuszm/testing_envs/anemoi-env/bin/activate
#nemoi-training train --config-name=//lustre/storeB/project/fou/hi/foccus/mateuszm/aifs-mono-ocean/aifs/config/mateusz_metno_ocean.yaml
#python $PYTHON_SCRIPT
