#!/bin/bash

YEAR=2024
FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/prepro_norkyst_zarr/
#YAMLFILE=$FOCCUS_DIR/ina/aifs-mono-ocean/dev-ina/preprocess-data/norkyst-2024-depths.yaml
YAMLFILE=$FOCCUS_DIR/ina/aifs-mono-ocean/dev-ina/preprocess-data/norkyst-2024.yaml
#ZARRFILE=$OUTDIR/norkyst800_his_zdepth_${YEAR}_jan01_m00_AN_ml.zarr
#ZARRFILE=$OUTDIR/norkyst800_his_zdepth_${YEAR}_7levels_m00_AN_ml.zarr
ZARRFILE=$OUTDIR/norkyst800_his_zdepth_${YEAR}_m00_AN_ml.zarr
CMD_OUTPUT_DIR=/lustre/storeB/project/fou/hi/foccus/ina/outputs/

#anemoi-datasets init $YAMLFILE $ZARRFILE --overwrite > $CMD_OUTPUT_DIR/make-zarr.out
# dataset already initialized

# Total number of jobs to run
total_jobs=100

# Number of jobs to run at a time
jobs_at_a_time=10

# Counter for total jobs run
total_counter=0

echo $date
echo "Starting $total_jobs jobs, but only $jobs_at_a_time jobs at a time" &> $CMD_OUTPUT_DIR/make-zarr.out

while ((total_counter < total_jobs)); do
  # Counter for number of jobs currently running
  running_jobs=0

  # Start jobs
  while ((running_jobs < jobs_at_a_time && total_counter < total_jobs)); do
    i=$((total_counter + 1))
    OUTFILE=$CMD_OUTPUT_DIR/make-zarr-$i.out
    # Run your job in the background
    anemoi-datasets load $ZARRFILE --part $i/100 &> $OUTFILE &
    echo "Running $i" &>> $CMD_OUTPUT_DIR/make-zarr.out && sleep 1 &

    # Increment counters
    ((running_jobs++))
    ((total_counter++))
  done

  # Wait for all background jobs to finish
  wait

  # Optional: add a delay between batches of jobs
  sleep 1
  echo "Waited for $jobs_at_a_time jobs to finish and slept 1s" &>> $CMD_OUTPUT_DIR/make-zarr.out
done

echo "All $total_jobs jobs finished at $date" &> $CMD_OUTPUT_DIR/make-zarr.out


# Then finalize (see other script)
