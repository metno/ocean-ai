#$ -S /bin/bash
#$ -l h_rt=2:00:00
#$ -q research-r8.q
#$ -l h_rss=4G,mem_free=4G,h_data=4G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/OUT_$JOB_NAME.$JOB_ID.$TASK_ID
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/ERR_$JOB_NAME.$JOB_ID.$TASK_ID
#$ -N forcing-cleanup-array
#$ -t 1-65

# Use this script to concat the forcing files (save space)

DIR=/lustre/storeB/project/fou/hi/foccus/datasets/norkyst_v3_forcing/clm

start_date=20250213

# Function to increment date
increment_date() {
    date -d "$1 + 1 day" +"%Y%m%d"
}

# Get a list of all dates to select the correct date for the array
date_now=$start_date
all_dates=()
all_dates+=("placeholder_first_element") # since $SGE_TASK_ID starts counting from 1
for i in $(seq 1 65);
do
    all_dates+=("$date_now")
    date_now=$(increment_date "$date_now")
done

# get the date for this job
job_date="${all_dates[$SGE_TASK_ID]}"

YEAR=${job_date:0:4}
MONTH=${job_date:4:2}
DAY=${job_date:6:2}

echo "Processing clm:" $job_date #$YEAR $MONTH $DAY
#echo $DIR/norkyst_clm_${YEAR}${MONTH}${DAY}T00Zm00.nc
ncks -d clim_time,2,2 $DIR/norkyst_clm_${YEAR}${MONTH}${DAY}T00Zm00.nc -O -o $DIR/norkyst_clm_${YEAR}${MONTH}${DAY}T00Zm00.nc

# then concat the files
 