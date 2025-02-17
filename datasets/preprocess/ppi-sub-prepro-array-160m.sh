#$ -S /bin/bash
#$ -l h_rt=24:00:00
#$ -q research-r8.q
#$ -l h_rss=45G,mem_free=45G,h_data=45G
#$ -t 1-296
#$ -o /lustre/storeB/project/fou/hi/foccus/ina/outputs/OUT_$JOB_NAME.$JOB_ID.$TASK_ID
#$ -e /lustre/storeB/project/fou/hi/foccus/ina/outputs/ERR_$JOB_NAME.$JOB_ID.$TASK_ID
#$ -N prepro-m70-2024

bash -l
conda deactivate

FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
PYTHON_SCRIPT=$FOCCUS_DIR/ina/ocean-ai/datasets/preprocess/impute_nans.py
MASKFILE=$FOCCUS_DIR/ina/norkyst-data/postpro_changes/landsea_mask_160m.nc
# OUTDIR is set in python script to 
# /lustre/storeB/project/fou/hi/foccus/datasets/prepro_norkyst/

DATADIR=/lustre/storeB/project/fou/hi/oper/norkyst_v3/forecast/his_zdepths/2024/
# TO find the nr of jobs to start do 
# >> find $DATADIR -type f -name "*2024*m70_AN.nc" | wc -l

# Start one array job for each file in DATADIR (e.g. 2024/01/01, 2024/01/02, ...)
# 295 files in 2024 for domain m70
DATAFILE=$(find $DATADIR -type f -name "*2024*m70_AN.nc" | sort | sed -n "${SGE_TASK_ID}p")
source $FOCCUS_DIR/python-envs/preprocess/bin/activate
python3 $PYTHON_SCRIPT $DATAFILE $MASKFILE
# file written to disk from PYTHON_SCRIPT will have the name {DATAFILE}_ml.nc ish

# 296 files in 2024 for domain m71
#DATAFILE=$(find $DATADIR -type f -name "*2024*m71_AN.nc" | sort | sed -n "${SGE_TASK_ID}p")
#python3 $PYTHON_SCRIPT $DATAFILE $MASKFILE

# ---------------------------
# NEXT: run anemoi-datasets

