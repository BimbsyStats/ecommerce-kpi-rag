#!/bin/bash
set -e

DATA_DIR="data"
KAGGLE_DATASET="geethasagarbonthu/marketing-and-e-commerce-analytics-dataset"

if [ -f "$DATA_DIR/events.csv" ]; then
  echo "events.csv already present, skipping download."
  exit 0
fi

echo "Downloading dataset from Kaggle..."
mkdir -p "$DATA_DIR"
kaggle datasets download -d "$KAGGLE_DATASET" -p "$DATA_DIR" --unzip
echo "Download complete."
