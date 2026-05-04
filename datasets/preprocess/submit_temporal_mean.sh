#$ -S /bin/bash
#$ -l h_rt=3:00:00
#$ -q bigmem-r8.q
#$ -l h_rss=80G
#$ -l mem_free=80G 
#$ -l h_data=80G
#$ -wd /lustre/storeB/project/fou/hi/foccus/mateuszm/c/ocean-ai/datasets/preprocess
#$ -o output/
#$ -e output/

conda activate myenv

python preprocess_temporal_mean.py