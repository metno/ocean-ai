#$ -S /bin/bash
#$ -l h_rt=03:00:00
#$ -q research-r8.q
#$ -l h_rss=16G,mem_free=16G,h_data=16G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.err
#$ -N results_animation
#$ -m bae
#$ -M makar5578@met.no

FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
FILE_IN1=$FOCCUS_DIR/experiments/ngpus-2017-24/inference/lam-48h-step_002016.nc #result file
FILE_IN2=$/lustre/storeB/project/fou/hi/roms_hindcast/norkyst_v3/sdepth/2024/04/norkyst800-20240402.nc
DIR_OUT=$FOCCUS_DIR/malene/ocean-ai/plot/figures/
RUN='Animation_difference'
VARIABLE1='u_eastward_0'
VARIABLE2='u_eastward'
FRAME=$16
START_TIME=$0



# activate python env
source $FOCCUS_DIR/.venv/bin/activate
# run code
python3 $FOCCUS_DIR/malene/ocean-ai/plot/script_animation_results.py $RUN $FILE_IN1 $FILE_IN2 $VARIABLE1 $VARIABLE2 $DIR_OUT $FRAME $START_TIME

# Then submit the script to the PPI que:
# qsub ppi-sub-animation.

# qstat - sjekke hvor i køen man er

# See resource usage and time run (-d for only list jobs from last two days):
# qacct -j $JOB_ID -d 2

#qdel + job id deletes the job from the queque