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

module load CUDA/12.8.0

set -e

echo "Job ID:    $SLURM_JOB_ID"
echo "Node:      $HOSTNAME"
echo "GPUs:      $CUDA_VISIBLE_DEVICES"
echo "Date:      $(date)"

cd /home/zjp17/spirob_mjlab
mkdir -p logs/rsl_rl/spirob_hole

uv run python - <<'PY'
import torch
print("Torch", torch.__version__, "CUDA avail:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Device:", torch.cuda.get_device_name(0))
PY

uv run train Mjlab-SpiRob-Hole \
  --env.scene.num-envs 4096 \
  --agent.logger tensorboard \
  --agent.run-name "ppo_${SLURM_JOB_ID}" \
  --gpu-ids "[0]"

echo ""
echo "SpiRob mjlab PPO training finished at $(date)"

