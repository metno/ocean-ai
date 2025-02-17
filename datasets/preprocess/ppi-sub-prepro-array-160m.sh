#$ -S /bin/bash
#$ -l h_rt=24:00:00
#$ -q research-r8.q
#$ -l h_rss=20G,mem_free=20G,h_data=20G
#$ -t 1-297
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID_$TASK_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID_$TASK_ID.err
#$ -N prepro-m71-2024
#$ -cwd

bash -l
conda deactivate

FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
PYTHON_SCRIPT=$(pwd -P)/impute_nans.py
MASKFILE=$FOCCUS_DIR/datasets/norkyst_v3-160m-70_mask.nc
# OUTDIR is set in python script to 
# /lustre/storeB/project/fou/hi/foccus/datasets/prepro_norkyst/

YEAR=2024
DATADIR=/lustre/storeB/project/fou/hi/oper/norkyst_v3/forecast/his_zdepths/${YEAR}/
# TO find the nr of jobs to start do 
# >> find $DATADIR -type f -name "*2024*m70_AN.nc" | wc -l

# Start one array job for each file in DATADIR (e.g. 2024/01/01, 2024/01/02, ...)
# 295 files in 2024 for domain m70
#DATAFILE=$(find $DATADIR -type f -name "*${YEAR}*m70_AN.nc" | sort | sed -n "${SGE_TASK_ID}p")
#source $FOCCUS_DIR/python-envs/preprocess/bin/activate
#python3 $PYTHON_SCRIPT $DATAFILE $MASKFILE
# file written to disk from PYTHON_SCRIPT will have the name {DATAFILE}_ml.nc ish

# Then do the same for the other domain
# 296 files in 2024 for domain m71
DATAFILE=$(find $DATADIR -type f -name "*${YEAR}*m71_AN.nc" | sort | sed -n "${SGE_TASK_ID}p")
source $FOCCUS_DIR/python-envs/preprocess/bin/activate
python3 $PYTHON_SCRIPT $DATAFILE $MASKFILE

# ---------------------------
# NEXT: run anemoi-datasets

