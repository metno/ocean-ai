#!/bin/bash

YEAR=2024
FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/prepro_norkyst_tests/ # this has been changed to make sure I dont overwrite
YAMLFILE=$FOCCUS_DIR/ina/aifs-mono-ocean/dev-ina/preprocess-data/norkyst-2024-temp.yaml
ZARRFILE=$OUTDIR/norkyst800_his_zdepth_${YEAR}_temp_m00_AN_ml.zarr
CMD_OUTPUT_DIR=/lustre/storeB/project/fou/hi/foccus/ina/outputs/

echo $YAMLFILE
echo $ZARRFILE

total_jobs=16
i=4

failed_jobs=(4 7 11 13)

for i in "${failed_jobs[@]}"
do
    OUTFILE=$CMD_OUTPUT_DIR/debug-make-zarr-temp-$i.out # also changed this one
    echo $(date) &> $OUTFILE
    anemoi-datasets load $ZARRFILE --part $i/$total_jobs &> $OUTFILE &
done


