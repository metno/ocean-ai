#$ -S /bin/bash
#$ -l h_rt=48:00:00
#$ -q research-r8.q
#$ -l h_rss=81G,mem_free=81G,h_data=81G
#$ -o /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -e /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -N hor_interp

OUTDIR=/lustre/storeB/project/fou/hi/foccus/datasets/norkyst-v3-hindcast/interp_forcings/
FILE=/lustre/storeB/project/fou/hi/foccus/datasets/norkyst-v3-hindcast/forcing/atm/arome_meps_2_5km_2017010100-2017090606_ext.nc

python /lustre/storeB/project/fou/hi/foccus/mateuszm/ocean-ai/forcing/interpolate_forcing.py $FILE $OUTDIR



