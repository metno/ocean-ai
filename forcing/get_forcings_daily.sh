#$ -S /bin/bash
#$ -l h_rt=00:30:00
#$ -q research-r8.q
#$ -l h_rss=4G,mem_free=4G,h_data=4G
#$ -o $JOB_NAME_$JOB_ID.out
#$ -e $JOB_NAME_$JOB_ID.err
#$ -N forcings-rsync

# This script gets all the atm, clm and bry files (daily) and copies them to the below location

FORCING_DIR=/lustre/storeB/project/metproduction/products/norkyst_v3/
OUTDIR=/lustre/storeB/project/fou/hi/foccus/datasets/norkyst_v3_forcing/

# Loop over the three domains
for dir in m00 m70 m71; do
    rsync -auv --progress $FORCING_DIR/$dir/*atm* $OUTDIR/atm/
done
# These only exist for m00 domain / gobal
rsync -auv --progress $FORCING_DIR/m00/*bry* $OUTDIR/bry/ 
rsync -auv --progress $FORCING_DIR/m00/*clm* $OUTDIR/clm/ 

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
# TODO: atm files are not cleaned up yet
# remove uneccecary data from the forcing files (and save space)
source forcing_cleanup.sh

#---------------------------------------------------------------------
# email if there are errors in the output file
# (think it should work to do this inside qsub since the above tasks will have finished by now)
source /lustre/storeB/project/fou/hi/foccus/cronjob_email_error.sh

#---------------------------------------------------------------------
# Open crontab: 
# $ crontab -e 
# and add this:
# MAILTO=ina.k.kullmann@met.no
# 
# 0 6 * * * /bin/rcron 'source /opt/sge/default/common/settings.sh; qsub /lustre/storeB/project/fou/hi/foccus/get_forcings_daily.sh'


