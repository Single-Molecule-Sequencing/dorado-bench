#!/bin/bash
set -euo pipefail

DORADO_EXEC="./dorado-1.1.1-linux-x64/bin/dorado"
MODELS_DIR=./Models
mkdir -p $MODELS_DIR

VERSIONS=("v4.2.0" "v4.3.0" "v5.0.0" "v5.2.0")
TYPES=("fast" "hac" "sup")

for v in "${VERSIONS[@]}"; do
  for t in "${TYPES[@]}"; do
    MODEL="dna_r10.4.1_e8.2_400bps_${t}@${v}"
    echo "Downloading $MODEL..."
    "$DORADO_EXEC" download --model $MODEL --directory $MODELS_DIR
  done
done
