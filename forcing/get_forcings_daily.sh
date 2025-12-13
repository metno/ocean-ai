#$ -S /bin/bash
#$ -l h_rt=00:30:00
#$ -q research-r8.q
#$ -l h_rss=8G,mem_free=8G,h_data=8G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.err
#$ -N forcings-rsync

# This script gets all the atm and bry files (daily) and copies them to the below location

FORCING_DIR=/lustre/storeB/project/metproduction/products/norkyst_v3/
OUTDIR=/lustre/storeB/project/fou/hi/foccus/datasets/norkystv3_forcing_oper/

# Loop over the three domains
for dir in m00 m70 m71; do
    rsync -auv --progress $FORCING_DIR/$dir/*atm* $OUTDIR/atm/
done
# These only exist for m00 domain / gobal
rsync -auv --progress $FORCING_DIR/m00/*bry* $OUTDIR/bry/ 

# Only copy river-file if there are new dates in the file
chmod 770 /lustre/storeB/project/fou/hi/foccus/get_river_forcings.sh
source /lustre/storeB/project/fou/hi/foccus/get_river_forcings.sh

#---------------------------------------------------------------------
# If dataroom B was down, and the filenames in OUTDIR are 
# not consecutive in dates check dataroom A for missing files

#TODO: copy from dataroom A, now only write warning
echo "Check for missing files (in case dataroom B shutdown)"
source /lustre/storeB/project/fou/hi/foccus/forcing_check_dates.sh $OUTDIR
echo "See file /lustre/storeB/project/fou/hi/foccus/forcing_warning.out"

#---------------------------------------------------------------------
# Remove uneccecary time steps from the atm forcing files (and save space)
# Keep only 24h
echo "Cleanup atm forcing files to save space"
source /modules/rhel8/mamba-mf3/etc/profile.d/conda.sh
conda activate 2025-01-development
python3 /lustre/storeB/project/fou/hi/foccus/forcing_cleanup.py

#---------------------------------------------------------------------
# email if there are errors in the output file
source /lustre/storeB/project/fou/hi/foccus/cronjob_email_error.sh

#---------------------------------------------------------------------
# Open crontab: 
# $ crontab -e 
# and add this:
# MAILTO=ina.k.kullmann@met.no
# 
# 0 6 * * * /bin/rcron 'source /opt/sge/default/common/settings.sh; qsub /lustre/storeB/project/fou/hi/foccus/get_forcings_daily.sh'


