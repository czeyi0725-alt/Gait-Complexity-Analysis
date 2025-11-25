# Data Access

Due to privacy and institutional restrictions, the raw gait data used in this study are **not publicly available** in this repository.

## Accessing the Full Dataset

To request access to the original data:

1. **Contact**: [Your email or PI's email]
2. **Institution**: [Lab/Institution name]
3. **Requirements**: 
   - IRB approval from your institution
   - Data use agreement
   - Justification for research use

## Data Overview

The complete dataset includes:

- **Subjects**: 76 participants (41 older adults aged 65-85; 35 younger adults aged 18-35)
- **Conditions**: 18 experimental conditions per subject (2 Days × 3 Blocks × 3 Trials)
- **Total observations**: 1,340 trial-level measurements
- **Measurements**: Postural sway features, symbolic entropy, permutation entropy

### File Format

The analysis expects data in CSV format with the following structure:

```csv
logfile,group,file,subject,condition,symb,perm,Day,Block,Trial,Day_group
analysis_output.1904647.log,old,S009_G03_D01_B01_T01,S009,G03_D01_B01_T01,2.2931,0.2236,D01,B01,T01,D01 Old
analysis_output.1904647.log,old,S013_G03_D01_B01_T01,S013,G03_D01_B01_T01,2.2853,0.2273,D01,B01,T01,D01 Old
...
```

### Column Descriptions

- `logfile`: Source analysis log file
- `group`: Age group ('old' or 'young')
- `file`: Original data filename
- `subject`: Subject ID (e.g., S009)
- `condition`: Experimental condition code (e.g., G03_D01_B01_T01)
- `symb`: Symbolic Shannon entropy value
- `perm`: Permutation entropy value
- `Day`: Day of testing (D01, D02)
- `Block`: Block number within day (B01, B02, B03)
- `Trial`: Trial number within block (T01, T02, T03)
- `Day_group`: Combined day and group label

## Sample Data (Coming Soon)

A small anonymized sample dataset (`sample_small.csv`) will be provided to demonstrate:
- Expected data format
- Variable ranges
- Data structure for running the analysis scripts

## Alternative Data Sources

Similar publicly available gait datasets:
- [PhysioNet Gait Databases](https://physionet.org/about/database/#gait)
- [UCI Machine Learning Repository - Activity Recognition](https://archive.ics.uci.edu/ml/datasets.php)

## Citation

If you use data from this study, please cite:

```
[Author et al. (2025). Title. Journal, Volume(Issue), Pages. DOI]
```

---

For questions about data access, contact: [your.email@institution.edu]
