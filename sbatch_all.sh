#!/bin/bash
set -euo pipefail

shopt -s nullglob
for dir in ./Sbatch/*/; do
  for f in "$dir"*.sbatch; do
    echo "Submitting: $f"
    sbatch "$f"
    sleep 0.5
  done
done
