#!/bin/bash

# Email address
EMAIL1="ina.k.kullmann@met.no"
EMAIL2="mateusz.matuszak@met.no"

# Path to the file you want to check
DIRECTORY="/home/inkul7832/"
FILE_PATH=$(ls -1t ${DIRECTORY}/forcings-rsync_*.err | head -n 1)

today_date=$(date +%Y-%m-%d)

# Check if the file is not empty
if [ -s "$FILE_PATH" ]; then
  # Email address to send the content to
  mail -s "Error from cronjob ($today_date)" "$EMAIL1" "$EMAIL2" < "$FILE_PATH"  
  #echo "Error from cronjob" "($today_date)" "$FILE_PATH"
fi

