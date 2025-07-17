#$ -S /bin/bash
#$ -l h_rt=03:00:00
#$ -q research-r8.q
#$ -l h_rss=64G,mem_free=64G,h_data=64G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID_$TASK_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID_$TASK_ID.err
#$ -N find_nans
#$ -t 1-13

YEAR_LIST=(2012 2013 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024)

YEAR=${YEAR_LIST[$SGE_TASK_ID-1]}
FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/

#echo "Running find_nans for year $YEAR"
conda deactivate
source $FOCCUS_DIR/ina/ocean-ai/.venv/bin/activate
python3 $FOCCUS_DIR/ina/ocean-ai/datasets/find_nans.py $YEAR
