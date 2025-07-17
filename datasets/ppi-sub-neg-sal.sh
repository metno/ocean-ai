#$ -S /bin/bash
#$ -l h_rt=3:00:00
#$ -q research-r8.q
#$ -l h_rss=32G,mem_free=32G,h_data=32G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME.$JOB_ID.$TASK_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME.$JOB_ID.$TASK_ID.err
#$ -N arr-negative-salinity
#$ -t 1-8

FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/
source $FOCCUS_DIR/ina/ocean-ai/.venv/bin/activate

# These years have negative salinity values in the dataset.
# see files /lustre/storeB/project/fou/hi/foccus/datasets/20*-stats.txt
YEARS=(2012 2013 2015 2017 2019 2020 2022 2024) 
#YEARS=(2012) # 2012 has missing dates, needs to be handled
YEAR=${YEARS[$SGE_TASK_ID-1]}
python3 $FOCCUS_DIR/ina/ocean-ai/datasets/negative_salinity.py $YEAR

# Then count the number of negative salinity values in all the files:
# cat /lustre/storeB/project/fou/hi/foccus/datasets/negative_salinity_20* | grep "ds_sal" | grep -v '^\s*#' | wc -l