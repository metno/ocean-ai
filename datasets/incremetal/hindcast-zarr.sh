#$ -S /bin/bash
#$ -l h_rt=0:20:00
#$ -q bigmem-r8.q
#$ -l h_rss=30G,mem_free=30G,h_data=30G
#$ -o /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -e /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -N surfacehindcast2018
#$ -t 1-366

YEAR=2018
FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/
ZARRFILE=$OUTDIR/norkystv3_hindcast_${YEAR}_surface.zarr

conda deactivate
source $FOCCUS_DIR/python-envs/anemoi-env-16-4-25/bin/activate
#anemoi-datasets init $YAMLFILE $ZARRFILE --overwrite 
anemoi-datasets load $ZARRFILE --part $SGE_TASK_ID/366 #8784
#anemoi-datasets finalize $ZARRFILE
