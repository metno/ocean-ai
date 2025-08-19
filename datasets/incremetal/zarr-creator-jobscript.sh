#$ -S /bin/bash
#$ -l h_rt=72:00:00
#$ -q bigmem-r8.q
#$ -l h_rss=80G,mem_free=80G,h_data=80G
#$ -o /lustre/storeB/project/fou/hi/foccus/outputs/
#$ -e /lustre/storeB/project/fou/hi/foccus/outputs/
#$ -N anemoi-datasets

FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/
ZARRFILE=$OUTDIR/ <--- PUT IN .ZARR FILE --->

conda deactivate
source $FOCCUS_DIR/python-envs/anemoi-env-7-7-25/bin/activate

# No more parallell, because there are some buggs where it doesn't finish. 
# This is more consistent. 


#anemoi-datasets init $YAMLFILE $ZARRFILE --overwrite
for i in {1..10}
do
    anemoi-datasets load $ZARRFILE --part $i/10
done

#anemoi-datasets finalize $ZARRFILE
