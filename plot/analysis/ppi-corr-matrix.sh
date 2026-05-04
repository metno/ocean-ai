#$ -S /bin/bash
#$ -l h_rt=00:30:00
#$ -q research-r8.q
#$ -l h_rss=30G,mem_free=30G,h_data=30G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.err
#$ -N Correlation_matrix
#$ -m bae
#$ -M makar5578@met.no


#Correlation matrix 
#READYTORUN IN PPI

FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus
FILEPATH=$FOCCUS_DIR/malene/run-anemoi-ocean/ppi/external_checkpoint_inference/Inference_res/lr_v2/lr3-5e-04-st200-se42/2024-03-30_24h_18d28_e011_s049990.nc
TITLE_PLOT='24hr_lead_time_30th_of_March_using_rollout_Inf'
SAVEFIG_PATH=$FOCCUS_DIR/malene/ocean-ai/plot/figures/corr_matrices/rollout
#OPTIONAL (include if you are using Norkyst files)
#NORKYST=--Norkyst



echo "Starting Python"
# activate python env
source $FOCCUS_DIR/.venv/bin/activate
# run code
python3 $FOCCUS_DIR/malene/ocean-ai/plot/analysis/Correlation_matrix_script.py $FILEPATH $TITLE_PLOT $SAVEFIG_PATH

# Then submit the script to the PPI que:
# qsub ppi-sub-animation.

# qstat - sjekke hvor i køen man er

# See resource usage and time run (-d for only list jobs from last two days):
# qacct -j $JOB_ID -d 2

#qdel + job id deletes the job from the queque
