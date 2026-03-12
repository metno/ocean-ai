#$ -S /bin/bash
#$ -l h_rt=02:00:00
#$ -q research-r8.q
#$ -l h_rss=60G,mem_free=60G,h_data=60G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.err
#$ -N seasonal_avg
#$ -m bae
#$ -M makar5578@met.no

# activate python env
FOCCUS_DIR="/lustre/storeB/project/fou/hi/foccus"
SAVE_PATH=$FOCCUS_DIR/malene/ocean-ai/plot/yearly_means

#Activate env
source $FOCCUS_DIR/.venv/bin/activate

python3 $FOCCUS_DIR/malene/ocean-ai/plot/seasonal_avg.py -sp $SAVE_PATH 

echo "Starting Python"

# Then submit the script to the PPI que:
# qsub ppi-sub-animation.

# qstat - sjekke hvor i køen man er

# See resource usage and time run (-d for only list jobs from last two days):
# qacct -j $JOB_ID -d 2

#qdel + job id deletes the job from the queque