# Age-Related Differences in Gait Complexity and Fatigue Effects

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Analysis code and supplementary materials for studying age-related differences in gait complexity using symbolic entropy measures.

## Overview

This repository contains the analysis pipeline for investigating:
- **Between-group differences** in symbolic entropy of postural sway between older and younger adults
- **Temporal dynamics** across multiple time scales (days, blocks, trials)
- **Short-term fatigue effects** within experimental blocks
- **Day-to-day adaptation** patterns across consecutive sessions

### Key Findings

- Older adults exhibit significantly higher symbolic entropy than younger adults (p < 10⁻²¹, Cohen's d = 0.155)
- Older adults show marginal evidence of within-block fatigue accumulation (p = 0.069)
- Younger adults maintain stable entropy across all temporal scales
- Day-to-day changes differ by age group: older adults show significant entropy reduction on Day 2 (p = 0.027)

## Repository Structure

```
.
├── README.md                              # This file
├── LICENSE                                # MIT (code) + CC-BY-4.0 (data/figures)
├── requirements.txt                       # Python dependencies
├── CITATION.cff                          # Citation metadata
│
├── code/                                 # Analysis scripts (not yet organized)
│   ├── extract_and_plot_individual_entropy.py    # Extract trial-level entropy
│   ├── trial_level_analysis.py                   # Cross-block trial effects
│   ├── within_block_trial_analysis.py            # Within-block fatigue analysis
│   ├── separate_group_within_block_analysis.py   # Age-stratified analysis
│   └── plot_group_differences.py                 # Generate publication figures
│
├── figures/                              # Publication-ready figures
│   ├── entropy_distribution.png          # Group comparison (violin + box)
│   ├── within_block_entropy_trend.png    # Within-block trajectories
│   ├── TABLES_FOR_MANUSCRIPT.txt         # Statistical tables
│   └── COMPREHENSIVE_RESULTS_REPORT.txt  # Full results summary
│
├── docs/                                 # Documentation and manuscript materials
│   └── results_update.tex                # LaTeX results section
│
├── data/                                 # Data access information
│   └── README.md                         # How to obtain/access datasets
│
└── archive/                              # Legacy files and snapshots
    └── [various historical files]
```

## Installation

### Prerequisites
- Python 3.9 or higher
- MATLAB R2023b (for initial gait data processing, optional for reproduction)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/czeyi0725-alt/Gait-Complexity-Analysis.git
cd Gait-Complexity-Analysis
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Reproducing Main Analyses

The analysis pipeline consists of several steps:

1. **Extract individual-level entropy values** from analysis logs:
```bash
python extract_and_plot_individual_entropy.py
```
Output: `figures/individual_entropies_extracted.csv`

2. **Trial-level analysis** (cross-block trial sequence 1-9):
```bash
python trial_level_analysis.py
```
Output: `figures/trial_level_analysis_results.txt`, `trial_level_entropy_trend.png`

3. **Within-block analysis** (trials 1-3 within each block):
```bash
python within_block_trial_analysis.py
```
Output: `figures/within_block_trial_analysis_results.txt`, `within_block_trial_entropy_trend.png`

4. **Age-stratified within-block analysis**:
```bash
python separate_group_within_block_analysis.py
```
Output: `figures/within_block_by_group_results.txt`, `within_block_by_group_comparison.png`

5. **Generate publication figures**:
```bash
python plot_group_differences.py
```
Output: `figures/enhanced_group_comparison.png` (4-panel comparison)

### Key Output Files

- `figures/individual_entropies_extracted.csv`: Trial-level entropy data (1340 observations)
- `figures/TABLES_FOR_MANUSCRIPT.txt`: Formatted statistical tables for publication
- `figures/entropy_distribution.png`: Main group comparison figure
- `figures/within_block_entropy_trend.png`: Within-block fatigue visualization

## Data

Due to privacy and institutional restrictions, raw gait data are not included in this repository. 

**To access the data:**
- Contact: czeyi@nd.edu
- Data source: the University of Notre Dame
- IRB approval required for access

A small sample dataset demonstrating the expected format will be provided in `data/sample_small.csv` (coming soon).

### Data Structure

The analysis expects CSV files with the following columns:
- `subject`: Subject identifier (e.g., S009)
- `group`: Age group ('old' or 'young')
- `condition`: Experimental condition (e.g., G03_D01_B01_T01)
- `symb`: Symbolic entropy value
- `perm`: Permutation entropy value (optional)
- `Day`, `Block`, `Trial`: Parsed experimental factors

## Statistical Methods

- **Group comparisons**: Mann-Whitney U test (one-sided, Old > Young)
- **Paired analyses**: Wilcoxon signed-rank test, paired t-test with bootstrap CIs
- **Repeated measures**: Mixed-effects linear models with random intercepts per subject
- **Effect sizes**: Cohen's d (paired and unpaired)
- **Significance threshold**: α = 0.05; marginal significance α = 0.10

Software: Python 3.9 (statsmodels 0.14, scipy 1.13)

## Citation

If you use this code or data in your research, please cite:

```bibtex
@software{balance_entropy_analysis,
  author = {[Your Name]},
  title = {Age-Related Differences in Gait Complexity and Fatigue Effects},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/czeyi0725-alt/Gait-Complexity-Analysis}
}
```

**Manuscript citation** (if published):
```
[Author et al. (2025). Title. Journal, Volume(Issue), Pages. DOI]
```

## License

- **Code**: MIT License (see [LICENSE](LICENSE))
- **Figures and data summaries**: CC BY 4.0 License
- **Raw data**: Contact institution for access and licensing terms

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/czeyi0725-alt/Gait-Complexity-Analysis/issues).

## Acknowledgments

- Data collection: [Lab/Institution name]
- Funding: [Grant information if applicable]
- Computing resources: [Cluster/HPC acknowledgment]

## Contact

- **Author**: [Your Name]
- **Email**: [Your email]
- **Institution**: [Your institution]
- **Lab/Group**: [Lab website or PI]

---

**Keywords**: gait analysis, symbolic entropy, aging, postural control, fatigue, complexity, time-series analysis
