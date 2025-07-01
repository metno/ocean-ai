#$ -S /bin/bash
#$ -l h_rt=24:00:00
#$ -q bigmem-r8.q
#$ -l h_rss=80G,mem_free=80G,h_data=80G
#$ -o /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -e /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -N hor_interp

conda activate myenv

ATM_FILE=arome_meps_2_5km_2018010100-2019010100_ext.nc
#arome_meps_2_5km_2017090700_ext.nc #arome_meps_2_5km_2017090609-2018010100_ext.nc

OUTDIR=/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_hindcast_atm_forcing/interpolated/
FILE=/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_hindcast_atm_forcing/orig_files/$ATM_FILE #arome_meps_2_5km_2017010100-2017090606_ext.nc
VAR=Pair,Uwind
#VAR=Vwind,Tair
#VAR=Qair,cloud,rain
#Pair,Uwind #,Vwind,Tair #,Qair,cloud,rain
#'Pair', 'Uwind', 'Vwind', 'Tair', 'Qair', 'cloud', 'rain'

python /lustre/storeB/project/fou/hi/foccus/mateuszm/ocean-ai/forcing/interpolate_forcing.py $FILE $OUTDIR $VAR $VAR


