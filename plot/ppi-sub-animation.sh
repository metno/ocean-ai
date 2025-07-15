#$ -S /bin/bash
#$ -l h_rt=01:10:00
#$ -q research-r8.q
#$ -l h_rss=16G,mem_free=16G,h_data=16G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.err
#$ -N speed_animation

FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
FILE_IN=$FOCCUS_DIR/datasets/norkystv3_hindcast_2023.zarr
DIR_SAVE=$FOCCUS_DIR/malene/ocean-ai/plot/figures/

# activate python env
source $FOCCUS_DIR/.venv/bin/activate
# run code
python3 $FOCCUS_DIR/malene/ocean-ai/plot/animation_wind.py $FILE_IN $DIR_SAVE

# Then submit the script to the PPI que:
# qsub ppi-sub-animation.

# qstat - sjekke hvor i køen man er

# See resource usage and time run (-d for only list jobs from last two days):
# qacct -j $JOB_ID -d 2