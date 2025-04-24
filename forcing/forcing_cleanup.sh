#!/bin/bash

# Use this script to remove uneccecary data from the forcing files (and save space)
DIR=/lustre/storeB/project/fou/hi/foccus/datasets/norkyst_v3_forcing/clm

# Find all files larger than 10GB and loop over them

find $DIR -type f -size +10G | while read -r file; do
    # Check if the file exists and not in $DIR/backup
    if [ -f "$file" ] && [[ "$file" != *"/backup/"* ]]; then
        echo "Processing clm-file: $file"
        # NOTE: the files will be overwritten!
        ncks -d clim_time,2,2 $file -O -o $file
        #echo $file
    fi
done

# TODO: add similar stuff for atm

# NOTE: do this separate script/terminal
# Now we may concat the files with a command like this:
#ncrcat -O -d time,0,366 $DIR/norkyst_clm_${YEAR}${MONTH}${DAY}T00Zm00.nc $DIR/norkyst_clm_${YEAR}m00.nc