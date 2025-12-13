#$ -S /bin/bash
#$ -l h_rt=04:00:00
#$ -q research-r8.q
#$ -l h_rss=8G,mem_free=8G,h_data=8G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.err
#$ -N forcings-cleanup

# This is a test script, 
# the main script is get_forcings_daily.sh where
# forcing_cleanup.py is called

# Use this script to remove uneccecary data from the atm forcing files (and save space)
echo "Cleanup atm forcing files to save space"
source /modules/rhel8/mamba-mf3/etc/profile.d/conda.sh
conda activate 2025-01-development
python3 /lustre/storeB/project/fou/hi/foccus/forcing_cleanup.py


# Now we may concat the files with a command similar to this:
#ncrcat -O -d time,0,366 $DIR/norkyst_clm_${YEAR}${MONTH}${DAY}T00Zm00.nc $DIR/norkyst_clm_${YEAR}m00.nc


