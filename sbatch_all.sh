#!/bin/bash
sbdir=./Sbatch

set -euo pipefail

shopt -s nullglob
for dir in "$sbdir"/*/; do
  for f in "$dir"*.sbatch; do
    echo "Submitting: $f"
    sbatch "$f"
    sleep 0.05
  done
done
