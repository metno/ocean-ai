#!/bin/bash

# After changing the scripts in the git repo on PPI 
# we should cp the new version to the location where 
# crontab runs the scripts:

DIR=/lustre/storeB/project/fou/hi/foccus/

cp get_forcings_daily.sh $DIR
cp forcing_check_dates.sh $DIR
cp get_river_forcings.sh $DIR
cp forcing_cleanup.sh $DIR
cp cronjob_email_error.sh $DIR

