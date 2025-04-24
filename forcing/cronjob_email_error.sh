#!/bin/bash

# Email address
EMAIL1="ina.k.kullmann@met.no"
EMAIL2="mateusz.matuszak@met.no"

# Path to the file you want to check
DIRECTORY="/home/inkul7832/"
FILE_PATH=$(ls -1t ${DIRECTORY}/forcings-rsync_*.err 2>/dev/null | head -n 1)

today_date=$(date +%Y-%m-%d)

# Check if a file was found
if [ -z "$FILE_PATH" ]; then
  echo "No .err files found in $DIRECTORY. Exiting."
  exit 0
fi

# Check if the file is not empty
if [ -s "$FILE_PATH" ]; then
  # Email address to send the content to
  /usr/sbin/sendmail -t <<EOF
To: $EMAIL1, $EMAIL2
Subject: Error from cronjob ($today_date)

$(cat "$FILE_PATH")
EOF

  # Check if sendmail succeeded
  if [ $? -ne 0 ]; then
    echo "Failed to send email. Please check the mail configuration."
    exit 1
  fi
else
  echo "File $FILE_PATH is empty. No email sent."
fi

