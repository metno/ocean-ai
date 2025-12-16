# Copying 160m forcings 
Operational forcing files are only kept for a few days, so we copy them to our foccus dir daily. 

The scripts in `/forcing` inside this git repo are placed in:
`/lustre/storeB/project/fou/hi/foccus/`

The main script is `get_forcings_daily.sh` which is called from a cronjob on Ina's account. 

This is the content of the cronjob:
```
MAILTO=ina.k.kullmann@met.no
0 6 * * * /bin/rcron 'source /opt/sge/default/common/settings.sh; qsub /lustre/storeB/project/fou/hi/foccus/get_forcings_daily.sh'

```
