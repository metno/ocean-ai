#!/bin/bash

cd $(pwd -P)

# Make files executable in the container (might not be needed)
chmod 770 env_setup.sh

PROJECT_DIR=/scratch/project_465001629
CONTAINER=$PROJECT_DIR/container/ocean-ai.sif

# Clone and pip install anemoi repos from the container
singularity exec -B /pfs:/pfs $CONTAINER $(pwd -P)/env_setup.sh
