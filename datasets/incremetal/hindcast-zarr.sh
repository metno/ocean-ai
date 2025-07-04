#$ -S /bin/bash
#$ -l h_rt=1:00:00
#$ -q bigmem-r8.q
#$ -l h_rss=35G,mem_free=35G,h_data=35G
#$ -o /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -e /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -N surfacehindcast2012
#$ -t 1-10

YEAR=2012
FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/
ZARRFILE=$OUTDIR/norkystv3_hindcast_${YEAR}_surface.zarr

conda deactivate
source $FOCCUS_DIR/python-envs/anemoi-env-16-4-25/bin/activate
#anemoi-datasets init $YAMLFILE $ZARRFILE --overwrite 
anemoi-datasets load $ZARRFILE --part $SGE_TASK_ID/10 #8784
#anemoi-datasets finalize $ZARRFILE
