#$ -S /bin/bash
#$ -l h_rt=2:00:00
#$ -q research-r8.q
#$ -l h_rss=20G,mem_free=20G,h_data=20G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/OUT_$JOB_NAME.$JOB_ID
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/ERR_$JOB_NAME.$JOB_ID
#$ -N mask
#$ -t 1-366

YEAR=2024
FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/
#YAMLFILE=$FOCCUS_DIR/mateuszm/OceanAI/datasets/mask_zarr.yaml
ZARRFILE=$OUTDIR/constant_mask_norkyst_${YEAR}.zarr

conda deactivate
source $FOCCUS_DIR/python-envs/anemoi-env-14-2-2025/bin/activate
#anemoi-datasets init $YAMLFILE $ZARRFILE --overwrite 
anemoi-datasets load $ZARRFILE --part $SGE_TASK_ID/366
#anemoi-datasets finalize $ZARRFILE
