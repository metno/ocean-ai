#!/bin/bash -l
#SBATCH --job-name=ocean-ai   # Job name
#SBATCH --output=output.o%j # Name of stdout output file
#SBATCH --error=error.e%j  # Name of stderr error file
#SBATCH --partition=dev-g  # partition name
#SBATCH --nodes=1               # Total number of nodes 
#SBATCH --ntasks-per-node=1     # 8 MPI ranks per node, 16 total (2x8)
#SBATCH --gpus-per-node=1       # Allocate one gpu per MPI rank
#SBATCH --time=2:00:00       # Run time (d-hh:mm:ss)
#SBATCH --account=project_465001629 # Project for billing
#SBATCH --exclusive

#Change this
CONFIG_NAME=main.yaml #This file should be located in run-anemoi/lumi

#Should not have to change these
PROJECT_DIR=/scratch/$SLURM_JOB_ACCOUNT
echo $(pwd -P)
CONTAINER_SCRIPT=$(pwd -P)/run_pytorch.sh
CONFIG_DIR=$(pwd -P)/training/
CONTAINER=$PROJECT_DIR/container/ocean-ai.sif
#VENV=$PROJECT_DIR/python-envs/anemoi-env-trimedge-branch/
VENV=/pfs/lustrep2/projappl/project_465001629/python-envs/anemoi-env-trimedge
export VIRTUAL_ENV=$VENV

module load LUMI/24.03 partition/G
export SINGULARITYENV_LD_LIBRARY_PATH=/opt/ompi/lib:${EBROOTAWSMINOFIMINRCCL}/lib:/opt/cray/xpmem/2.4.4-2.3_9.1__gff0e1d9.shasta/lib64:${SINGULARITYENV_LD_LIBRARY_PATH}

# MPI + OpenMP bindings: https://docs.lumi-supercomputer.eu/runjobs/scheduled-jobs/distribution-binding
CPU_BIND="mask_cpu:fe000000000000,fe00000000000000,fe0000,fe000000,fe,fe00,fe00000000,fe0000000000"

# run run-pytorch.sh in singularity container like recommended
# in LUMI doc: https://lumi-supercomputer.github.io/LUMI-EasyBuild-docs/p/PyTorch
srun \
    singularity exec -B /pfs:/pfs \
                     -B /var/spool/slurmd \
                     -B /opt/cray \
                     -B /usr/lib64 \
                     $CONTAINER $CONTAINER_SCRIPT $CONFIG_DIR $CONFIG_NAME
