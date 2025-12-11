#$ -S /bin/bash
#$ -l h_rt=24:00:00
#$ -q research-r8.q
#$ -l h_rss=45G,mem_free=45G,h_data=45G
#$ -t 1-45
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID_$TASK_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID_$TASK_ID.err
#$ -N prepro-2025-800m
#$ -cwd

bash -l
conda deactivate

FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
PYTHON_SCRIPT=$(pwd -P)/impute_nans.py
MASKFILE=$FOCCUS_DIR/datasets/norkyst_v3-800m_mask.nc
# OUTDIR is set in python script to 
# /lustre/storeB/project/fou/hi/foccus/datasets/prepro_norkyst/

DATADIR=/lustre/storeB/project/fou/hi/oper/norkyst_v3/forecast/his_zdepths/2025/
# TO find the nr of jobs to start do 
# >> find $DATADIR -type f -name "*2025*m00_AN.nc" | wc -l

# Start one array job for each file in DATADIR (e.g. 2024/01/01, 2024/01/02, ...)
DATAFILE=$(find $DATADIR -type f -name "*2025*m00_AN.nc" | sort | sed -n "${SGE_TASK_ID}p")

source $FOCCUS_DIR/python-envs/preprocess/bin/activate
python3 $PYTHON_SCRIPT $DATAFILE $MASKFILE
# file written to disk from PYTHON_SCRIPT will have the name {DATAFILE}_ml.nc ish

# ---------------------------
# NEXT: run anemoi-datasets

