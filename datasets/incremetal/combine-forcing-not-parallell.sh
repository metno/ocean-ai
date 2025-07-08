#$ -S /bin/bash
#$ -l h_rt=72:00:00
#$ -q bigmem-r8.q
#$ -l h_rss=80G,mem_free=80G,h_data=80G
#$ -o /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -e /lustre/storeB/project/fou/hi/foccus/mateuszm/outputs/
#$ -N forcing-combine

FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/forcing_norkystv3_hindcast_zarr/
ZARRFILE=$OUTDIR/forcing_norkystv3_hindcast_2017-2024.zarr

conda deactivate
source $FOCCUS_DIR/python-envs/anemoi-env-7-7-25/bin/activate

for i in {1..10}
do
    anemoi-datasets load $ZARRFILE --part $i/10
done

