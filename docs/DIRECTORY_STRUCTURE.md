# Directory Structure and Organization

This document explains the organization of files in this repository.

## Directory Layout

### `/src/` - Python Analysis Scripts
Contains all Python scripts for data analysis and visualization:
- `extract_and_plot_individual_entropy.py` - Extracts trial-level entropy from log files
- `trial_level_analysis.py` - Analyzes trends across trial sequence (1-9)
- `within_block_trial_analysis.py` - Analyzes within-block progression (T01→T03)
- `separate_group_within_block_analysis.py` - Age-stratified within-block analysis
- `plot_group_differences.py` - Generates publication-quality figures
- `classify_by_condition.py` - Organizes data by experimental condition
- `classify_and_verify.py` - Data verification utilities

**Usage**: Run scripts from the repository root:
```bash
python src/script_name.py
```

### `/scripts/` - MATLAB Scripts and Job Launchers
Contains MATLAB processing scripts and shell scripts for batch jobs:
- `process_gait_data.m` - Main MATLAB data processing pipeline
- `analyze_entropy_trends.m` - Entropy trend analysis
- `analyze_statistical_trends.m` - Statistical comparisons
- `find_significant_features.m` - Feature selection
- `plot_entropy_distribution.m` - Distribution visualizations
- `plot_entropy_functions.m` - Plotting utility functions
- `launch_all_jobs.sh` - Batch job submission script

**Usage**: MATLAB scripts are called by job scripts or run interactively in MATLAB.

### `/jobs/` - Cluster Job Submission Scripts
Contains `.qsub` files for cluster job submission:
- `run_gait_template.qsub` - Template for creating per-condition jobs
- `run_entropy_analysis.qsub` - Main entropy analysis job
- `run_feature_finder.qsub` - Feature finder job
- `run_job_*.qsub` - Per-condition processing jobs (e.g., D01_B01_T01)

**Note**: Individual condition jobs (`run_job_*.qsub`) are excluded from the repository via `.gitignore` since they are auto-generated.

### `/logs/` - Job Output Logs
Contains output logs from cluster jobs:
- `analysis_output.*.log` - Main analysis outputs (parsed by Python scripts)
- `entropy_analysis.*.log` - Entropy analysis logs
- `feature_finder_output.*.log` - Feature finder logs
- `test_analysis_output.*.log` - Test run logs

**Note**: This directory is excluded from the repository via `.gitignore` as logs are regenerated outputs, not source code.

### `/figures/` - Publication Figures and Results
Contains publication-ready figures and result summaries:
- `entropy_distribution.png` - Main group comparison figure
- `within_block_entropy_trend.png` - Within-block fatigue visualization
- `individual_entropies_extracted.csv` - Trial-level entropy data (1340 observations)
- `TABLES_FOR_MANUSCRIPT.txt` - Formatted statistical tables
- `COMPREHENSIVE_RESULTS_REPORT.txt` - Complete results summary

### `/outputs/` - Analysis Outputs
Contains processed results and summaries:
- `results/entropy_analysis_results.csv` - Condition-level entropy summaries
- `results/entropy_trends.pdf` - Trend visualizations

### `/data/` - Data Information
Contains data access information and sample data:
- `README.md` - Instructions for accessing full dataset
- `sample_small.csv` - Small sample dataset (20 observations)

**Note**: Raw gait data (`gait_old_full/`, `gait_young_full/`) are excluded from the repository.

### `/docs/` - Documentation and Manuscript Materials
Contains manuscript-related documentation:
- `results_update.tex` - LaTeX results section for manuscript

### `/archive/` - Historical Files
Contains snapshots and legacy files:
- Environment snapshots
- Sample file listings
- Historical documentation

### Root Directory Files
- `README.md` - Main project documentation
- `LICENSE` - MIT (code) + CC-BY-4.0 (data/figures)
- `CITATION.cff` - Citation metadata for GitHub
- `requirements.txt` - Python dependencies
- `run_all.sh` - Quick-start script to run all analyses
- `.gitignore` - Git exclusion rules
- `.gitattributes` - Git LFS configuration

## File Naming Conventions

### Python Scripts
- Descriptive names with underscores: `extract_and_plot_individual_entropy.py`
- Located in `/src/`

### MATLAB Scripts
- Descriptive names with underscores: `analyze_entropy_trends.m`
- Located in `/scripts/`

### Job Scripts
- Pattern: `run_<task>.qsub` for templates
- Pattern: `run_job_<condition>.qsub` for per-condition jobs (auto-generated)
- Located in `/jobs/`

### Log Files
- Pattern: `<task>_output.<jobid>.log` or `<task>.<jobid>.log`
- Located in `/logs/` (excluded from repo)

### Result Files
- Descriptive names: `entropy_analysis_results.csv`
- Located in `/outputs/results/` or `/figures/`

## Running Analyses

### Quick Start
Run all analyses from the repository root:
```bash
bash run_all.sh
```

### Individual Scripts
Run specific analyses:
```bash
python src/extract_and_plot_individual_entropy.py
python src/trial_level_analysis.py
python src/within_block_trial_analysis.py
python src/separate_group_within_block_analysis.py
python src/plot_group_differences.py
```

### MATLAB Processing
For MATLAB data processing:
```bash
cd scripts
matlab -nodisplay -r "process_gait_data; exit"
```

### Cluster Jobs
Submit jobs on the cluster:
```bash
cd jobs
qsub run_entropy_analysis.qsub
```

## Path References

All Python scripts use relative paths from the repository root:
- Read data: `figures/individual_entropies_extracted.csv`
- Read logs: `logs/analysis_output.*.log`
- Write outputs: `figures/<filename>`
- Write results: `outputs/results/<filename>`

When running scripts, always execute from the repository root directory.

## Excluded from Repository

The following are excluded via `.gitignore`:
- `/logs/` - Job output logs (regenerated)
- `/gait_old_full/` and `/gait_young_full/` - Raw data (large, restricted)
- `/.venv/` - Virtual environment (user-specific)
- `/jobs/run_job_*.qsub` - Auto-generated job scripts
- `*.log` - Log files anywhere in the repository
- Temporary files, caches, and OS-specific files

## Adding New Files

When adding new files:
- **Python scripts** → `/src/`
- **MATLAB scripts** → `/scripts/`
- **Job scripts** → `/jobs/`
- **Results/figures** → `/figures/`
- **Processed data** → `/outputs/results/`
- **Documentation** → `/docs/`

## Questions?

See the main [README.md](../README.md) for general project information, or open an issue on GitHub.
