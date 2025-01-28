#!/bin/bash -l
#SBATCH --job-name=ocean-ai-infer   # Job name
#SBATCH --output=outputs/output.o%j # Name of stdout output file
#SBATCH --error=outputs/error.e%j  # Name of stderr error file
#SBATCH --partition=dev-g  # partition name
#SBATCH --nodes=1               # Total number of nodes 
#SBATCH --ntasks-per-node=4     # 8 MPI ranks per node, 16 total (2x8)
#SBATCH --gpus-per-node=4       # Allocate one gpu per MPI rank
#SBATCH --cpus-per-task=8
#SBATCH --time=00:05:00       # Run time (d-hh:mm:ss)
#SBATCH --account=project_465001629 # Project for billing

CONFIG_DIR=$(pwd -P)/inference
CONFIG_NAME=$CONFIG_DIR/lumi_infer.yaml
PROJECT_DIR=/scratch/$SLURM_JOB_ACCOUNT
CONTAINER=$PROJECT_DIR/container/ocean-ai.sif
CONTAINER_SCRIPT=$(pwd -P)/run_pytorch_infer.sh
chmod 770 ${CONTAINER_SCRIPT}
VENV=/pfs/lustrep2/projappl/project_465001629/python-envs/anemoi-env-inference

module load LUMI/24.03 partition/G
export SINGULARITYENV_LD_LIBRARY_PATH=/opt/ompi/lib:${EBROOTAWSMINOFIMINRCCL}/lib:/opt/cray/xpmem/2.4.4-2.3_9.1__gff0e1d9.shasta/lib64:${SINGULARITYENV_LD_LIBRARY_PATH}
export VIRTUAL_ENV=$VENV

srun \
    singularity exec -B /pfs:/pfs \
                     -B /var/spool/slurmd \
                     -B /opt/cray \
                     -B /usr/lib64 \
                     -B /scratch/project_465001629 \
                     -B /projappl/project_465001629 \
                     $CONTAINER $CONTAINER_SCRIPT $CONFIG_NAME
#anemoi-inference run inference.yaml
