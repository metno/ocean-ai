#$ -S /bin/bash
#$ -l h_rt=03:00:00
#$ -q research-r8.q
#$ -l h_rss=50G,mem_free=50G,h_data=50G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.err
#$ -N calc_mld
#$ -m bae
#$ -M makar5578@met.no

# activate python env
FOCCUS_DIR="/lustre/storeB/project/fou/hi/foccus"
DATSET_PATH=$FOCCUS_DIR/malene/ocean-ai/plot/yearly_means/seasonal_avg.nc
FILENAME=$FOCCUS_DIR/malene/ocean-ai/plot/mld_calculated.nc

#Activate env
source $FOCCUS_DIR/.venv/bin/activate

python3 $FOCCUS_DIR/malene/ocean-ai/plot/calc_mld.py -ds $DATSET_PATH -fn $FILENAME

echo "Starting Python"

# Then submit the script to the PPI que:
# qsub ppi-sub-animation.

# qstat - sjekke hvor i køen man er

# See resource usage and time run (-d for only list jobs from last two days):
# qacct -j $JOB_ID -d 2

#qdel + job id deletes the job from the queque