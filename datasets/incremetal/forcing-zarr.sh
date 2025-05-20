#$ -S /bin/bash
#$ -l h_rt=0:20:00
#$ -q bigmem-r8.q
#$ -l h_rss=81G,mem_free=81G,h_data=81G
#$ -o /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/forcing/
#$ -e /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/forcing/
#$ -N forcing
#$ -t 1-122

DATE=2017
FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/norkystv3_forcing_zarr
ZARRFILE=$OUTDIR/forcing_norkystv3_hindcast_${DATE}.zarr

conda deactivate
source $FOCCUS_DIR/python-envs/anemoi-env-16-4-25/bin/activate
#anemoi-datasets init $YAMLFILE $ZARRFILE --overwrite 
anemoi-datasets load $ZARRFILE --part $SGE_TASK_ID/122 #8784
#anemoi-datasets finalize $ZARRFILE
