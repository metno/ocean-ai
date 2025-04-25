#$ -S /bin/bash
#$ -l h_rt=01:00:00
#$ -q research-r8.q
#$ -l h_rss=20G,mem_free=20G,h_data=20G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.out
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/$JOB_NAME_$JOB_ID.err
#$ -N new-forcing
#$ -cwd

YEAR=2024
FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/
YAMLFILE=$(pwd -P)/norkystv3_forcing.yaml
ZARRFILE=$OUTDIR/norkystv3_${YEAR}_3d_new_forcings.zarr

conda deactivate
source $FOCCUS_DIR/python-envs/new-anemoi-env/bin/activate
anemoi-datasets create $YAMLFILE $ZARRFILE --overwrite 
