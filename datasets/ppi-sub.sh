#$ -S /bin/bash
#$ -l h_rt=2:00:00
#$ -q research-r8.q
#$ -l h_rss=64G,mem_free=64G,h_data=64G
#$ -wd /lustre/storeB/project/fou/hi/foccus/mateuszm/anemoi/logs/
#$ -N anemoi-datasets

bash -l
conda deactivate
source /lustre/storeB/project/fou/hi/foccus/python-envs/anemoi-env/bin/activate
anemoi-datasets create /lustre/storeB/project/fou/hi/foccus/mateuszm/anemoi/datasets/mask_zarr.yaml /lustre/storeB/project/fou/hi/foccus/mateuszm/anemoi/datasets/mask_2024010100-2024010320.zarr


