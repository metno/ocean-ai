#$ -S /bin/bash
#$ -l h_rt=6:00:00
#$ -q bigmem-r8.q
#$ -l h_rss=80G,mem_free=80G,h_data=80G
#$ -o /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -e /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -N combine-zarr-files
#$ -t 1-10

FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/
ZARRFILE=$OUTDIR/norkystv3_hindcast_2012-2024_surface.zarr

conda deactivate
source $FOCCUS_DIR/python-envs/anemoi-env-16-4-25/bin/activate
#anemoi-datasets init $YAMLFILE $ZARRFILE --overwrite 
anemoi-datasets load $ZARRFILE --part $SGE_TASK_ID/10 #8784
#anemoi-datasets finalize $ZARRFILE