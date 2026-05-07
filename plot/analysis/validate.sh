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

inf_file_dist = '/lustre/storeB/project/fou/hi/foccus/ingvild/test_infrence/results/2024-04-02_72h_18d28_e011_s049990.nc'

python plot_validate.py "$inf_file_dist"