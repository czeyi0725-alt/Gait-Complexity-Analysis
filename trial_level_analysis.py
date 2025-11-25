#!/usr/bin/env python3
"""
Trial-level mixed-effects analysis to test whether entropy increases with trial sequence.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import sys
import os

# Add statsmodels
try:
    import statsmodels.api as sm
    from statsmodels.formula.api import mixedlm
except ImportError:
    print("Error: statsmodels not installed. Installing...")
    sys.exit(1)

# Set plot style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Read individual-level data
print("Loading individual entropy data...")
df = pd.read_csv('/groups/jgoodwin/czeyi/balance/figures/individual_entropies_extracted.csv')

print(f"Loaded {len(df)} rows")
print(f"Groups: {df['group'].value_counts().to_dict()}")
print(f"Days: {df['Day'].value_counts().to_dict()}")

# Create numeric trial number (1-9 for 3 blocks × 3 trials)
# Block: B01, B02, B03; Trial: T01, T02, T03
df['Block_num'] = df['Block'].str.extract(r'B(\d+)').astype(int)
df['Trial_num'] = df['Trial'].str.extract(r'T(\d+)').astype(int)
df['trial_number'] = (df['Block_num'] - 1) * 3 + df['Trial_num']  # 1-9

# Create numeric Day (1 or 2)
df['Day_num'] = df['Day'].str.extract(r'D(\d+)').astype(int)

# Drop any rows with missing entropy values
df = df.dropna(subset=['symb', 'perm', 'subject'])

print(f"\nAfter cleaning: {len(df)} rows")
print(f"Trial numbers range: {df['trial_number'].min()} to {df['trial_number'].max()}")
print(f"Subjects: {df['subject'].nunique()}")

# ============= TRIAL-LEVEL MIXED-EFFECTS MODEL =============
print("\n" + "="*70)
print("TRIAL-LEVEL MIXED-EFFECTS MODEL FOR SYMBOLIC ENTROPY")
print("="*70)

# Model: symb ~ trial_number + group + Day_num + trial_number:group + trial_number:Day_num + (1|subject)
formula = 'symb ~ trial_number + C(group) + Day_num + trial_number:C(group) + trial_number:Day_num'

print(f"\nFitting model: {formula}")
print("Random effects: (1 | subject)")

try:
    model_symb = mixedlm(formula, df, groups=df['subject'])
    result_symb = model_symb.fit(method='lbfgs')
    
    print("\n" + "-"*70)
    print("MODEL SUMMARY - Symbolic Entropy")
    print("-"*70)
    print(result_symb.summary())
    
    # Extract key statistics
    params = result_symb.params
    pvalues = result_symb.pvalues
    conf_int = result_symb.conf_int()
    
    print("\n" + "="*70)
    print("KEY FINDINGS:")
    print("="*70)
    
    # Trial number main effect
    trial_coef = params['trial_number']
    trial_pval = pvalues['trial_number']
    trial_ci_low = conf_int.loc['trial_number', 0]
    trial_ci_high = conf_int.loc['trial_number', 1]
    
    print(f"\n1. TRIAL NUMBER (main effect):")
    print(f"   Coefficient: {trial_coef:.6f}")
    print(f"   p-value: {trial_pval:.4f}")
    print(f"   95% CI: [{trial_ci_low:.6f}, {trial_ci_high:.6f}]")
    if trial_pval < 0.05:
        direction = "INCREASE" if trial_coef > 0 else "DECREASE"
        print(f"   *** SIGNIFICANT {direction} in entropy with trial sequence ***")
    else:
        print(f"   Not significant (p >= 0.05)")
    
    # Trial × group interaction
    if 'trial_number:C(group)[T.young]' in params.index:
        int_group_coef = params['trial_number:C(group)[T.young]']
        int_group_pval = pvalues['trial_number:C(group)[T.young]']
        int_group_ci_low = conf_int.loc['trial_number:C(group)[T.young]', 0]
        int_group_ci_high = conf_int.loc['trial_number:C(group)[T.young]', 1]
        
        print(f"\n2. TRIAL × GROUP interaction:")
        print(f"   Coefficient (young vs old): {int_group_coef:.6f}")
        print(f"   p-value: {int_group_pval:.4f}")
        print(f"   95% CI: [{int_group_ci_low:.6f}, {int_group_ci_high:.6f}]")
        
        # Calculate slopes for each group
        old_slope = trial_coef
        young_slope = trial_coef + int_group_coef
        
        print(f"\n   Trial slope for OLD group: {old_slope:.6f}")
        print(f"   Trial slope for YOUNG group: {young_slope:.6f}")
        
        if int_group_pval < 0.05:
            print(f"   *** SIGNIFICANT interaction - groups differ in trial effect ***")
        else:
            print(f"   Interaction not significant")
    
    # Trial × Day interaction
    if 'trial_number:Day_num' in params.index:
        int_day_coef = params['trial_number:Day_num']
        int_day_pval = pvalues['trial_number:Day_num']
        int_day_ci_low = conf_int.loc['trial_number:Day_num', 0]
        int_day_ci_high = conf_int.loc['trial_number:Day_num', 1]
        
        print(f"\n3. TRIAL × DAY interaction:")
        print(f"   Coefficient: {int_day_coef:.6f}")
        print(f"   p-value: {int_day_pval:.4f}")
        print(f"   95% CI: [{int_day_ci_low:.6f}, {int_day_ci_high:.6f}]")
        if int_day_pval < 0.05:
            print(f"   *** SIGNIFICANT - trial effect differs by day ***")
        else:
            print(f"   Not significant")
    
except Exception as e:
    print(f"Error fitting model: {e}")
    import traceback
    traceback.print_exc()

# ============= VISUALIZATION =============
print("\n\nCreating visualizations...")

# Create figure with multiple subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Overall trial trend by group
ax = axes[0, 0]
for group_name in ['old', 'young']:
    group_data = df[df['group'] == group_name]
    # Calculate mean entropy per trial number
    trial_means = group_data.groupby('trial_number')['symb'].agg(['mean', 'sem']).reset_index()
    
    color = '#d62728' if group_name == 'old' else '#1f77b4'
    ax.errorbar(trial_means['trial_number'], trial_means['mean'], 
                yerr=trial_means['sem'], 
                marker='o', linewidth=2, capsize=5,
                label=f'{group_name.upper()} (n={group_data["subject"].nunique()})',
                color=color, alpha=0.8)
    
    # Add linear fit line
    z = np.polyfit(trial_means['trial_number'], trial_means['mean'], 1)
    p = np.poly1d(z)
    x_smooth = np.linspace(trial_means['trial_number'].min(), trial_means['trial_number'].max(), 100)
    ax.plot(x_smooth, p(x_smooth), '--', color=color, alpha=0.6, linewidth=1.5)

ax.set_xlabel('Trial Number (1-9)', fontsize=12, fontweight='bold')
ax.set_ylabel('Symbolic Entropy', fontsize=12, fontweight='bold')
ax.set_title('Entropy Trend Across Trial Sequence by Group', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# 2. Separate by Day
ax = axes[0, 1]
for day in ['D01', 'D02']:
    for group_name in ['old', 'young']:
        subset = df[(df['Day'] == day) & (df['group'] == group_name)]
        trial_means = subset.groupby('trial_number')['symb'].mean().reset_index()
        
        color = '#d62728' if group_name == 'old' else '#1f77b4'
        linestyle = '-' if day == 'D01' else '--'
        ax.plot(trial_means['trial_number'], trial_means['symb'], 
                marker='o', linestyle=linestyle, 
                label=f'{group_name.upper()} {day}',
                color=color, alpha=0.7, markersize=5)

ax.set_xlabel('Trial Number (1-9)', fontsize=12, fontweight='bold')
ax.set_ylabel('Symbolic Entropy', fontsize=12, fontweight='bold')
ax.set_title('Entropy by Trial, Day, and Group', fontsize=14, fontweight='bold')
ax.legend(fontsize=9, ncol=2)
ax.grid(True, alpha=0.3)

# 3. Box plot by trial number (old group)
ax = axes[1, 0]
old_data = df[df['group'] == 'old']
sns.boxplot(data=old_data, x='trial_number', y='symb', ax=ax, color='#d62728', showfliers=False)
ax.set_xlabel('Trial Number', fontsize=12, fontweight='bold')
ax.set_ylabel('Symbolic Entropy', fontsize=12, fontweight='bold')
ax.set_title('OLD Group: Entropy Distribution by Trial', fontsize=14, fontweight='bold')

# 4. Box plot by trial number (young group)
ax = axes[1, 1]
young_data = df[df['group'] == 'young']
sns.boxplot(data=young_data, x='trial_number', y='symb', ax=ax, color='#1f77b4', showfliers=False)
ax.set_xlabel('Trial Number', fontsize=12, fontweight='bold')
ax.set_ylabel('Symbolic Entropy', fontsize=12, fontweight='bold')
ax.set_title('YOUNG Group: Entropy Distribution by Trial', fontsize=14, fontweight='bold')

plt.tight_layout()

# Save figure
output_path = '/groups/jgoodwin/czeyi/balance/figures/trial_level_entropy_trend.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\nSaved figure to: {output_path}")

# ============= SAVE RESULTS TO TEXT FILE =============
output_file = '/groups/jgoodwin/czeyi/balance/figures/trial_level_analysis_results.txt'
with open(output_file, 'w') as f:
    f.write("="*70 + "\n")
    f.write("TRIAL-LEVEL MIXED-EFFECTS ANALYSIS RESULTS\n")
    f.write("="*70 + "\n\n")
    f.write(f"Model: {formula}\n")
    f.write("Random effects: (1 | subject)\n\n")
    f.write(result_symb.summary().as_text())
    f.write("\n\n" + "="*70 + "\n")
    f.write("INTERPRETATION:\n")
    f.write("="*70 + "\n\n")
    
    f.write(f"1. Trial number main effect:\n")
    f.write(f"   Coefficient: {trial_coef:.6f}, p = {trial_pval:.4f}\n")
    f.write(f"   95% CI: [{trial_ci_low:.6f}, {trial_ci_high:.6f}]\n")
    if trial_pval < 0.05:
        f.write(f"   SIGNIFICANT: Entropy {'increases' if trial_coef > 0 else 'decreases'} with trial sequence\n")
    else:
        f.write(f"   Not significant\n")
    
    if 'trial_number:C(group)[T.young]' in params.index:
        f.write(f"\n2. Trial × Group interaction:\n")
        f.write(f"   Coefficient: {int_group_coef:.6f}, p = {int_group_pval:.4f}\n")
        f.write(f"   OLD slope: {old_slope:.6f}\n")
        f.write(f"   YOUNG slope: {young_slope:.6f}\n")
        if int_group_pval < 0.05:
            f.write(f"   SIGNIFICANT: Groups differ in how entropy changes across trials\n")
    
    if 'trial_number:Day_num' in params.index:
        f.write(f"\n3. Trial × Day interaction:\n")
        f.write(f"   Coefficient: {int_day_coef:.6f}, p = {int_day_pval:.4f}\n")

print(f"Saved results to: {output_file}")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
