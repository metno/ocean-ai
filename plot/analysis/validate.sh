#$ -S /bin/bash
#$ -l h_rt=6:00:00
#$ -q research-r8.q
#$ -l h_rss=20G
#$ -l mem_free=20G 
#$ -l h_data=20G
#$ -wd /lustre/storeB/project/fou/hi/foccus/mateuszm/a/ocean-ai/plot/analysis
#$ -o output/
#$ -e output/

conda activate myenv

python plot_validate.py