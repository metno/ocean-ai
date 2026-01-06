#$ -S /bin/bash
#$ -l h_rt=03:00:00
#$ -q research-r8.q
#$ -l h_rss=30G,mem_free=30G,h_data=30G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.err
#$ -N mf_dataset
#$ -m bae
#$ -M makar5578@met.no

# activate python env
FOCCUS_DIR="/lustre/storeB/project/fou/hi/foccus"
SAVE_PATH="/lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot"
MONTH="January February March April May June July August September October November December"

#Activate env
source $FOCCUS_DIR/.venv/bin/activate


echo "Starting Python"
echo "Iterating through months"

for m in ${MONTH}
do 
    python3 $FOCCUS_DIR/malene/ocean-ai/plot/mfdataset_run.py -sp $SAVE_PATH -mn $m
    echo "Creating a dataset for $m was successfull"
done

# Then submit the script to the PPI que:
# qsub ppi-sub-animation.

# qstat - sjekke hvor i køen man er

# See resource usage and time run (-d for only list jobs from last two days):
# qacct -j $JOB_ID -d 2

#qdel + job id deletes the job from the queque