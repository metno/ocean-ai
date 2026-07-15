#$ -S /bin/bash
#$ -l h_rt=03:00:00
#$ -q bigmem-r8.q
#$ -l h_rss=80G,mem_free=80G,h_data=80G
#$ -o /lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/datasets/preprocess/outputs/
#$ -e /lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/datasets/preprocess/outputs
#$ -N results_animation
#$ -m bae
#$ -M makar5578@met.no


FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
source $FOCCUS_DIR/.venv/bin/activate

python /lustre/storeB/project/fou/hi/foccus/malene/ocean-ai/plot/analysis/salinity_anomalies.py