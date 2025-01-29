#!/bin/bash
#
# This script monitors the CPU/GPU load of an already
# running job by running htop, nvtop or rocm-smi. Can
# either pass the job-ID + node name of an existing job
# or the username for the script to inspect the queue.
# If no command line argument is passed, the job-ID +
# node name will be taken from "squeue --me".
#
# Signatures:
#     ./monitor_interactive <job-id> <node-name>
#     ./monitor_interactive <user-name>
#     ./monitor_interactive


# Read job-ID and node name from queue
# Only tested when job runs on a single node
# and one job is in the queue. Modifications
# are required for other use cases
inspect_queue () {
    set -- $queue
    last_line=${@: -8}
    echo $last_line
    set -- $last_line
    jobid=$1
    node_name=$8
}


# Count number of command line arguments
if [ $# == 0 ]; then
    queue=$(squeue --me)
    inspect_queue
elif [ $# == 1 ]; then
    queue=$(squeue --user $1)
    inspect_queue
else
    jobid=$1
    node_name=$2
fi

echo "Job-ID: $jobid, Node name: $node_name"


# Monitoring mode (nvtop | htop | rocm)
mode=nvtop

# Enable partition
module load LUMI/23.09  partition/G EasyBuild-user

# Start interactive overlapping job running nvtop/htop/rocm-smi on
# the already allocated node
if [ $mode == "nvtop" ]; then
    eb nvtop-3.0.2.eb
    module load nvtop/3.0.2
    srun --overlap --pty --jobid=$jobid -w $node_name nvtop
elif [ $mode == "htop" ]; then
    eb systools-23.09.eb
    module load systools/23.09
    srun --overlap --pty --jobid=$jobid -w $node_name htop
elif [ $mode == "rocm" ]; then
    srun --overlap --pty --jobid=$jobid -w $node_name rocm-smi #--showuse
else
    echo "Unknown mode '$mode'!"
    exit 1
fi
