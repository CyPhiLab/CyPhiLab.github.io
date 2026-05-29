---
layout: default
title: Cluster
robots: noindex
permalink: /cluster/
---
<br>

# CyPhiLab HPC Quickstart Guide

This page is a lab-facing quick reference for getting onto the cluster, starting work on compute nodes, and running jobs through Slurm. It is not a full replacement for the official HPC documentation, but it should cover the common day-to-day steps.

Official HPC docs: https://sites.google.com/a/case.edu/hpcc/

## What The Cluster Is

The cluster gives you access to shared compute resources that are much larger than a laptop or workstation. To use it, we request the resources that we would like to use and how long we would like to use them. The cluster then automatically schedules resource access for users based on an internal queuing system called [Slurm](https://en.wikipedia.org/wiki/Slurm_Workload_Manager). In our experience, all but the most powerful resources are usually available at any given time, but at periods of high demand you may have to wait in line until you are granted access to your requested reources.

For our lab, the common workflow is:

1. Connect to the cluster from your laptop.
2. Move into your project directory.
3. Start an interactive session for development or debugging, or submit a batch job for longer training runs.

## Connecting To The Cluster

### VPN

If off campus, you will need to connect to the Case VPN to access the cluster. This is very easy to use. Please see the Case guide for getting it installed and using it: https://vpnsetup.case.edu/.

### Terminal SSH

From a terminal on your laptop:

```bash
ssh <your_case_id>@pioneer.case.edu
```

If your access flow differs, use the hostname and login method provided by the university HPC docs.

### VS Code Remote SSH

VS Code is usually the easiest way to work on the cluster without constantly copying files back and forth. See comprehensive guide [here](https://code.visualstudio.com/docs/remote/ssh).

1. Install the `Remote - SSH` extension in VS Code.
2. Open the Command Palette (ctrl+shift+P).
3. Run `Remote-SSH: Add New SSH Host...`.
4. Enter:

```sshconfig
ssh <your_case_id>@pioneer.case.edu
```

5. Type your password to connect to host `pioneer`.
6. You can then open folders on the remote machine the same way you would normally.

Once connected, you can edit code in VS Code, use the remote terminal, and launch jobs without leaving the editor.

## Basic Layout And Expectations

When your cluster account is created, you are given a home directory and you can create project-specific directories under it. A typical pattern looks like this:

```text
/home/<your_case_id>/
```

### IMPORTANT: Understanding Login vs Compute Nodes

When you first log into the cluster, your terminal will look like this: <your_case_id>@hpcX (where X is a number). This means you are on the "login" node. You can edit code, transfer files, and launch jobs from the login node, but you are NOT to run any code on it - it has limited compute resources and doing so can slow things down for other users. If we consistently abuse the login node, our lab could see our HPC privileges demoted. 

NOTE: Do not let AI coding assistants (like Copilot or Claude Code) run code on the login node. If they want to test something, they can fire up compute nodes and run on those, or you can manually run code for them.

### Managing code on the cluster

Just like on your local machine, you always want to make sure you are using proper software management practices. You should log into your GitHub account on the cluster and make sure that you are regularly keeping your commits up to date on the remote repository so that you have a backup in case something goes wrong. When using Python, make sure to use proper package/environment management (i.e uv, conda, etc). 

## Running jobs on the cluster

There are two types of jobs that you can run on the cluster: interactive and batch jobs. You should use interactive jobs for debugging and development, and then once your job is ready to run for hours, you can dispatch it to a batch job.

### Interactive Compute Sessions

Use interactive sessions when you need to interactively run code on a compute node for development, debugging, testing, or short experiments. Note that when you close an interactive session (i.e. by disconnecting from SSH, by your computer going to sleep, by running out of time, etc), whatever code you are running at the time gets cut off. 

CPU Interactive Session: 

```bash
srun --pty --time=02:00:00 --cpus-per-task=4 --mem=8G bash
```

This requests 1 interactive shell with 4 CPU cores and 8 GB RAM for 2 hours.

### GPU Interactive Session

```bash
srun -p gpu --gres=gpu:1 -C gpul40s --time=01:00:00 --cpus-per-task=4 --mem=16G --pty bash
```

This requests a node with 1 `L40S`-class GPU, 4 CPU cores, and 16GB of RAM for 1 hour.



## GPU Notes

GPU availability changes over time, and the best source for live information is the [Pioneer cluster status page](https://ondemand-pioneer.case.edu/public/sinfo_pioneer.html), which tells you what resources are currently available. There are many different GPUs availability on the cluster, and you can request different ones depending on how computationally demanding your needs are. Typically, better GPUs are in higher demand and thus you are more likely to have to wait to use them. At the time of writing, here are the various GPUs available in order of increasing compute: `gpup100`, `gpu2080`, `gpu2080,rds`, `gpu4v100`, `gpu2v100`, `gpu2v100,rds`, `gpul40s`, `gpu2h100`, `gpu4090`. In our experience, the l40s is a good balance between power and availability.

## Batch Jobs With Slurm

Batch jobs are where the real value of the cluster comes from. Unlike an interactive job, you don't have to be logged into the cluster while a batch job is running: you can simply set it to run, log off, and come back later to view the results when the job is finished. This is essential for machine learning workflows because training large neural networks on lots of data usually takes hours to days. 

### Submit A Job

```bash
sbatch your_job.sh
```

### Check Your Jobs

```bash
squeue -u $USER
```

### Cancel A Job

```bash
scancel <job_id>
```

## Example Batch Script

Below is the structure of the included example job, [`ppo_training_example.sh`](https://github.com/CyPhiLab/CyPhiLab.github.io/blob/main/assets/ppo_training_example.sh).

```bash
#!/bin/bash
#SBATCH --job-name=spirob_mjlab_ppo
#SBATCH --output=logs/rsl_rl/spirob_hole/%j.out
#SBATCH --error=logs/rsl_rl/spirob_hole/%j.err
#SBATCH --partition=gpu
#SBATCH -C gpul40s
#SBATCH --cpus-per-task=8
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --time=10:00:00
```

What those lines mean:

- `--job-name`: readable name shown in Slurm tools
- `--output` and `--error`: = log destinations
- `--partition=gpu`: run on the GPU queue
- `-C gpul40s`: request a node with the `l40s` GPU
- `--cpus-per-task=8`: allocate 8 CPU cores
- `--nodes=1`: keep the job on one node
- `--gres=gpu:1`: request 1 GPUs
- `--mem=32G`: allocate 32 GB RAM
- `--time=10:00:00`: set a 10 hour wall-time limit

The example then does four useful things:

1. Loads CUDA.
2. Prints basic job metadata.
3. Changes into the project directory and creates a log folder.
4. Runs a small PyTorch CUDA check before launching training.

## Recommended Structure For Your Own Job Scripts

Use this as a starting template:

```bash
#!/bin/bash
#SBATCH --job-name=my_job
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err
#SBATCH --partition=gpu
#SBATCH -C gpul40s
#SBATCH --cpus-per-task=8
#SBATCH --nodes=1
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH --time=04:00:00

set -e

module load CUDA/12.8.0

cd /home/<your_case_id>/<your_project>
mkdir -p logs

echo "Job ID: $SLURM_JOB_ID"
echo "Node: $HOSTNAME"
echo "Date: $(date)"

nvidia-smi

# Replace with your actual command
python train.py
```

Adjust CPU count, RAM, runtime, and GPU to match the actual job. One way to speed up your job is to request to GPUs at a time by changing to #SBATCH --gres=gpu:2. However, your code specifically needs to be set up to utilize a multi-GPU setup.

## Useful Slurm Commands

```bash
squeue -u $USER
scontrol show job <job_id>
sinfo
tail -f logs/<job_id>.out
tail -f logs/<job_id>.err
```

These cover most debugging needs:

- `squeue` shows whether your job is pending or running.
- `scontrol show job` gives more scheduling detail.
- `sinfo` shows partition and node information.
- `tail -f` lets you watch logs in real time.

## Practical Advice

- Test with short jobs on an interactive session before launching long runs.
- Always send stdout and stderr to log files.
- Print environment information early in the script.
- Create output directories explicitly with `mkdir -p`.
- If a job is pending for a long time, check whether your requested GPU type is too restrictive.


## Suggested First-Time Setup Checklist

1. Confirm you can SSH into Pioneer.
2. Set up VS Code Remote SSH.
3. Find your project directory on the cluster.
4. Run a short CPU interactive session.
5. Run a short GPU interactive session.
6. Copy the example batch script and adapt it for your project.
7. Submit a short test job before submitting a full training run.

