#$ -S /bin/bash
#$ -l h_rt=00:30:00
#$ -q research-r8.q
#$ -l h_rss=30G,mem_free=30G,h_data=30G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.err
#$ -N results_animation
#$ -m bae
#$ -M makar5578@met.no


#Correlation matrix 
#READYTORUN IN PPI

FILEPATH=/lustre/storeB/project/fou/hi/foccus/datasets/symlinks/norkystv3-hindcast/2024/norkyst800-20240502.nc
TITLE_PLOT='Norkyst_2024-05-02'
SAVEFIG_PATH=/lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot/figures
#OPTIONAL (include if you are using Norkyst files)
NORKYST=--Norkyst



echo "Starting Python"
# activate python env
source $FOCCUS_DIR/.venv/bin/activate
# run code
python3 $FOCCUS_DIR/malene/ocean-ai/plot/corr_matrix.py $RUN $FILEPATH $TITLE_PLOT $SAVEFIG_PATH $NORKYST

# Then submit the script to the PPI que:
# qsub ppi-sub-animation.

# qstat - sjekke hvor i køen man er

# See resource usage and time run (-d for only list jobs from last two days):
# qacct -j $JOB_ID -d 2

#qdel + job id deletes the job from the queque