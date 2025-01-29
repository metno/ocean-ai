#$ -S /bin/bash
#$ -l h_rt=02:00:00
#$ -q research-r8.q
#$ -l h_rss=45G,mem_free=45G,h_data=45G
#$ -o /lustre/storeB/project/fou/hi/foccus/ina/outputs/OUT_$JOB_NAME.$JOB_ID
#$ -e /lustre/storeB/project/fou/hi/foccus/ina/outputs/ERR_$JOB_NAME.$JOB_ID
#$ -N preprocess

bash -l
conda deactivate

FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
PYTHON_SCRIPT=$FOCCUS_DIR/ina/aifs-mono-ocean/dev-ina/preprocess-data/impute_nans.py
MASKFILE=$FOCCUS_DIR/ina/norkyst-data/postpro_changes/landsea_mask.nc
# OUTDIR is set in python script to 
# /lustre/storeB/project/fou/hi/foccus/datasets/prepro_norkyst/

# TODO: this should change for each array job...
DATAFILE=/lustre/storeB/project/fou/hi/oper/norkyst_v3/forecast/his_zdepths/2024/01/14/norkyst800_his_zdepth_20240114T00Z_m00_AN.nc

source $FOCCUS_DIR/python-envs/preprocess/bin/activate
python3 $PYTHON_SCRIPT $DATAFILE $MASKFILE
