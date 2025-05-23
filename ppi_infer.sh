#!/bin/bash
#$ -N ocean-infer
#$ -b n
#$ -S /bin/bash
#$ -l h_data=20G
#$ -l h_rss=20G
#$ -l h_rt=00:30:00
#$ -q gpu-r8.q
#$ -l h=sm-nx10077659-bc-compute.int.met.no
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/OUT_$JOB_NAME.$JOB_ID
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/ERR_$JOB_NAME.$JOB_ID

DIR=/lustre/storeB/project/fou/hi/foccus
cd $DIR/experiments/temp-jan
export HYDRA_FULL_ERROR=1
export ANEMOI_BASE_SEED=1
conda deactivate
source $DIR/python-envs/new-anemoi-env/bin/activate
anemoi-inference run $DIR/ina/ocean-ai/inference/inference.yaml
