# Forcing Shell Scripts

This directory contains scripts for managing the copying and handling of forcing files to the `foccus` directory. 

## Main Script: `get_forcings_daily.sh`
The primary script, `get_forcings_daily.sh`, is executed as a cron job under Ina's profile. It is located at:
`/lustre/storeB/project/fou/hi/foccus`


### Important Note:
If you make any changes to the scripts in this Git repository, you must manually copy the updated files to the directory mentioned above to ensure the cron job uses the latest version.

## Forcing Cleanup
For scenarios where a large number of files need to be processed, an array-job version of the script is available to handle such cases efficiently.

## TODO
We could also do a cleanup of the amt files in a similar way to the clm files. 
