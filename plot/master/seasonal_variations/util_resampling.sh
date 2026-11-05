#$ -S /bin/bash
#$ -l h_rt=10:00:00
#$ -q research-r8.q
#$ -l h_rss=50G,mem_free=50G,h_data=50G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.err
#$ -N resampling_means
#$ -m bae
#$ -M makar5578@met.no

FILEPATH=/lustre/storeB/project/fou/hi/foccus/malene/run-ocean-anemoi/ppi/external_checkpoint_inference/results/rollout_benchmark_lr3.5e6-rs3-i0-m3/step_51000_e14
OUTPUT_PATH=/lustre/storeB/project/fou/hi/foccus/malene/run-ocean-anemoi/ppi/external_checkpoint_inference/results/rollout_benchmark_lr3.5e6-rs3-i0-m3/step_51000_e14/resampled_means


echo "Starting Python"
# activate python env
source $FOCCUS_DIR/.venv/bin/activate
# run code
python3 /lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot/master/seasonal_variations/utils_resampling.py $FILEPATH $OUTPUT_PATH
