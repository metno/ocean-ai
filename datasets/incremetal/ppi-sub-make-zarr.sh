# NOTE: this file was not used as is, see the shell scripts

#$ -S /bin/bash
#$ -l h_rt=72:00:00
#$ -q research-r8.q
#$ -l h_rss=50G,mem_free=50G,h_data=50G
#$ -o /lustre/storeB/project/fou/hi/foccus/ina/outputs/OUT_$JOB_NAME.$JOB_ID
#$ -e /lustre/storeB/project/fou/hi/foccus/ina/outputs/ERR_$JOB_NAME.$JOB_ID
#$ -N make-zarr-oneyear

bash -l
conda deactivate

YEAR=2024
FOCCUS_DIR=/lustre/storeB/project/fou/hi/foccus/
OUTDIR=$FOCCUS_DIR/datasets/prepro_norkyst_zarr/
YAMLFILE=$FOCCUS_DIR/ina/aifs-mono-ocean/dev-ina/preprocess-data/norkyst-2024-depths.yaml
#ZARRFILE=$OUTDIR/norkyst800_his_zdepth_${YEAR}_7levels_m00_AN_ml.zarr
ZARRFILE=$OUTDIR/norkyst800_his_zdepth_${YEAR}_surface_m00_AN_ml.zarr

source /lustre/storeB/project/fou/hi/foccus/python-envs/anemoi-env/bin/activate

anemoi-datasets init $YAMLFILE $ZARRFILE --overwrite
# use array job here
anemoi-datasets load $ZARRFILE --part 1/3 #1/100 

# Then when all arrays are done:
#anemoi-datasets finalise $ZARRFILE
# Clean up temp files
#anemoi-datasets cleanup $ZARRFILE
# Remove yaml info from zarr file
#anemoi-datasets patch $ZARRFILE

# Change frequency from string to int
python3 $FOCCUS_DIR/ina/aifs-mono-ocean/make-datasets/postpro_zarr.py $ZARRFILE
# TODO: also fix resolution in above script!!


#---- 
# Old version
#anemoi-datasets create $YAMLFILE $ZARRFILE #--overwrite
#----
