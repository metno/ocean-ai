#$ -S /bin/bash
#$ -l h_rt=01:00:00
#$ -q research-r8.q
#$ -l h_rss=16G,mem_free=16G,h_data=16G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID_$TASK_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID_$TASK_ID.err
#$ -N find_nans
#$ -cwd
#$ -t 1-11

YEAR_LIST=(2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024)
# TODO: test 2012 as well

YEAR=${YEAR_LIST[$SGE_TASK_ID-1]}
FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/

echo "Running find_nans for year $YEAR"
conda deactivate
source $FOCCUS_DIR/.venv/bin/activate
python3 find_nans.py $YEAR
