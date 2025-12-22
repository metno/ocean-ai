#$ -S /bin/bash
#$ -l h_rt=01:00:00
#$ -q research-r8.q
#$ -l h_rss=30G,mem_free=30G,h_data=30G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.err
#$ -N mf_dataset
#$ -m bae
#$ -M makar5578@met.no


#Creating a yearly dataset of resampled monthly means with dropped vars to ease memory use
FOCCUS_DIR="/lustre/storeB/project/fou/hi/foccus"
FILE_PATH="/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/*.nc"
SAVE_PATH="/lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot/norkyst_monthly_means_2024.nc"

echo "Starting Python"

# activate python env
source $FOCCUS_DIR/.venv/bin/activate
# run code
python3 $FOCCUS_DIR/malene/ocean-ai/plot/mfdataset_run.py $FILE_PATH $SAVE_PATH

# Then submit the script to the PPI que:
# qsub ppi-sub-animation.

# qstat - sjekke hvor i køen man er

# See resource usage and time run (-d for only list jobs from last two days):
# qacct -j $JOB_ID -d 2

#qdel + job id deletes the job from the queque