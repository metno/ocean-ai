#!/bin/bash

FORCING_DIR=/lustre/storeB/project/metproduction/products/norkyst_v3/
OUTDIR=/lustre/storeB/project/fou/hi/foccus/datasets/norkyst_v3_forcing/

echo "--- Get new river file? ---"
# Get file that was most recently copied FOCCUS 
PREV_FILE=$OUTDIR/river/$(ls -1 $OUTDIR/river/ | sort | tail -n 1)
echo "Most recently copied FOCCUS:" $PREV_FILE
# And the potentially updated file
NEW_FILE=$FORCING_DIR/norkyst_river_800.nc

PREV_DATE=$(ncdump -i -v river_time $PREV_FILE  | grep -v 'UNLIMITED' | grep -oP '(?<=river_time = ).*' | sed 's/[",]//g' | awk '{print $NF}')
NEW_DATE=$(ncdump -i -v river_time $NEW_FILE  | grep -v 'UNLIMITED' | grep -oP '(?<=river_time = ).*' | sed 's/[",]//g' | awk '{print $NF}')
echo "Dates to compare" $PREV_DATE $NEW_DATE

# Get today's date in the format YYYY-MM-DD
TODAY_DATE=$(date +%Y-%m-%d)
echo "Date today:" $TODAY_DATE

if [ "$PREV_DATE" != "$NEW_DATE" ]; then
    # Extract the filename from the source file path
    FILENAME=$(basename "$NEW_FILE")
    
    # Create the new filename with today's date appended
    NEW_FILENAME="${FILENAME%.nc}_$TODAY_DATE.nc"
    
    # Copy the file to the new location with the new filename
    rsync -auv --progress $NEW_FILE $OUTDIR/river/$NEW_FILENAME
    
    echo "File copied to $OUTDIR/river/$NEW_FILENAME"
else
    echo "The dates are identical. No file copied."
fi
echo "---"

# TODO: concatenate the files...