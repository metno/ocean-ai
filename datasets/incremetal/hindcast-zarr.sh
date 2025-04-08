#$ -S /bin/bash
#$ -l h_rt=2:00:00
#$ -q bigmem-r8.q
#$ -l h_rss=81G,mem_free=81G,h_data=81G
#$ -o /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -e /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -N hindcast2023
#$ -t 1-2

YEAR=2023
FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/
#YAMLFILE=$FOCCUS_DIR/mateuszm/OceanAI/datasets/mask_zarr.yaml
ZARRFILE=$OUTDIR/norkystv3_hindcast_${YEAR}.zarr

conda deactivate
source $FOCCUS_DIR/python-envs/anemoi-env-8-4-25/bin/activate
#anemoi-datasets init $YAMLFILE $ZARRFILE --overwrite 
anemoi-datasets load $ZARRFILE --part $SGE_TASK_ID/366
#anemoi-datasets finalize $ZARRFILE