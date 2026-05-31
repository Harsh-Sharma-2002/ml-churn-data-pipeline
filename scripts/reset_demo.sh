#!/bin/bash

set -e

echo "[RESET] Cleaning demo runtime state..."

rm -f logs/processed_files.json

rm -f data/raw/*.csv
rm -f data/processed/*.csv
rm -f data/rejected/*.csv

rm -f reports/*.json
rm -f reports/pre_clean/*.json
rm -f reports/post_clean/*.json
rm -f reports/combined/*.json
rm -f reports/training/*.json

rm -f models/*.pkl

find . -type d -name "__pycache__" -prune -exec rm -rf {} +

mkdir -p data/raw data/demo_daily_files data/processed data/rejected
mkdir -p reports/pre_clean reports/post_clean reports/combined reports/training
mkdir -p logs models

touch data/raw/.gitkeep
touch data/demo_daily_files/.gitkeep
touch data/processed/.gitkeep
touch data/rejected/.gitkeep

touch reports/pre_clean/.gitkeep
touch reports/post_clean/.gitkeep
touch reports/combined/.gitkeep
touch reports/training/.gitkeep

touch logs/.gitkeep
touch models/.gitkeep

echo "[RESET] Regenerating staged demo daily files..."
python -m scripts.prepare_demo_data

echo "[RESET] Demo reset complete."
