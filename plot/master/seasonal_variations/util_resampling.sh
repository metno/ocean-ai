#$ -S /bin/bash
#$ -l h_rt=10:00:00
#$ -q research-r8.q
#$ -l h_rss=50G,mem_free=50G,h_data=50G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.err
#$ -N resampling_means
#$ -m bae
#$ -M makar5578@met.no

echo "Starting Python"
# activate python env
source $FOCCUS_DIR/.venv/bin/activate
# run code
python3 /lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot/master/seasonal_variations/utils_resampling.py 
