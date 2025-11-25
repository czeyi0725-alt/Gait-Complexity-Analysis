#!/bin/bash
# Quick start script to reproduce main analyses
# Usage: bash run_all.sh

set -e  # Exit on error

echo "==================================="
echo "Gait Entropy Analysis - Quick Start"
echo "==================================="

# Check Python version
echo "Checking Python version..."
python --version

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Running analysis pipeline..."
echo ""

# Step 1: Extract individual entropy values
echo "[1/5] Extracting individual-level entropy values..."
python src/extract_and_plot_individual_entropy.py

# Step 2: Trial-level analysis
echo "[2/5] Running trial-level analysis (cross-block)..."
python src/trial_level_analysis.py

# Step 3: Within-block analysis
echo "[3/5] Running within-block analysis..."
python src/within_block_trial_analysis.py

# Step 4: Age-stratified within-block analysis
echo "[4/5] Running age-stratified within-block analysis..."
python src/separate_group_within_block_analysis.py

# Step 5: Generate publication figures
echo "[5/5] Generating publication figures..."
python src/plot_group_differences.py

echo ""
echo "==================================="
echo "Analysis complete!"
echo "==================================="
echo ""
echo "Key outputs:"
echo "  - figures/individual_entropies_extracted.csv"
echo "  - figures/entropy_distribution.png"
echo "  - figures/within_block_entropy_trend.png"
echo "  - figures/TABLES_FOR_MANUSCRIPT.txt"
echo ""
echo "See README.md for detailed documentation."
