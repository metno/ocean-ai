#$ -S /bin/bash
#$ -l h_rt=48:00:00
#$ -q research-r8.q
#$ -l h_rss=20G,mem_free=20G,h_data=20G
#$ -o /lustre/storeB/project/fou/hi/foccus/mateuszm/OceanAI/datasets/logs/OUT_$JOB_NAME.$JOB_ID
#$ -e /lustre/storeB/project/fou/hi/foccus/mateuszm/OceanAI/datasets/logs/ERR_$JOB_NAME.$JOB_ID
#$ -N h
#$ -t 1-366


YEAR=2024
FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/
#YAMLFILE=$FOCCUS_DIR/mateuszm/OceanAI/datasets/mask_zarr.yaml
ZARRFILE=$OUTDIR/h_norkyst_${YEAR}.zarr

conda deactivate
source $FOCCUS_DIR/python-envs/anemoi-env/bin/activate
#anemoi-datasets init $YAMLFILE $ZARRFILE --overwrite 
anemoi-datasets load $ZARRFILE --part $SGE_TASK_ID/366
#anemoi-datasets finalize $ZARRFILE
