#$ -S /bin/bash
#$ -l h_rt=72:00:00
#$ -q bigmem-r8.q
#$ -l h_rss=80G,mem_free=80G,h_data=80G
#$ -o /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -e /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -N hor_interp

ATM_FILE=arome_meps_2_5km_2024010100-2025010100_ext_newTair.nc
#arome_meps_2_5km_2017090700_ext.nc #arome_meps_2_5km_2017090609-2018010100_ext.nc

OUTDIR=/lustre/storeB/project/fou/hi/foccus/datasets/norkyst-v3-hindcast/interp_forcings/
FILE=/lustre/storeB/project/fou/hi/foccus/datasets/norkyst-v3-hindcast/forcing/atm/$ATM_FILE #arome_meps_2_5km_2017010100-2017090606_ext.nc
VAR=Uwind,Vwind,Tair,Qair,cloud,rain
#Pair,Uwind,Vwind,Tair,Qair,cloud,rain
#'Pair', 'Uwind', 'Vwind', 'Tair', 'Qair', 'cloud', 'rain'

python /lustre/storeB/project/fou/hi/foccus/mateuszm/ocean-ai/forcing/interpolate_forcing.py $FILE $OUTDIR $VAR $VAR



#6258271 0.25000 hor_interp mateuszm     r     05/15/2025 11:00:52 bigmem-r8.q@sm-nx10077955-be-c     1        
#6258312 0.25000 hor_interp mateuszm     r     05/15/2025 11:02:23 bigmem-r8.q@c6525-hw8rl83-bn-c     1        
#6258318 0.25000 hor_interp mateuszm     r     05/15/2025 11:02:51 bigmem-r8.q@c6525-hw8rl83-bn-c     1        
#6258335 0.25000 hor_interp mateuszm     r     05/15/2025 11:04:43 bigmem-r8.q@c6525-hw8rl83-bn-c     1        
#6258377 0.25000 hor_interp mateuszm     r     05/15/2025 11:05:32 bigmem-r8.q@c6525-hw8rl83-bn-c     1        
#6258394 0.00000 hor_interp mateuszm     qw    05/15/2025 11:06:06    