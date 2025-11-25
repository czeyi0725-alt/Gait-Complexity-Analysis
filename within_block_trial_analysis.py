#!/usr/bin/env python3
"""
Within-block trial analysis: Test if entropy increases across consecutive trials
within the same block (T01 -> T02 -> T03), which would indicate short-term fatigue.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import sys
import os

try:
    import statsmodels.api as sm
    from statsmodels.formula.api import mixedlm
except ImportError:
    print("Error: statsmodels not installed.")
    sys.exit(1)

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 10)

# Read data
print("Loading individual entropy data...")
df = pd.read_csv('/groups/jgoodwin/czeyi/balance/figures/individual_entropies_extracted.csv')

print(f"Loaded {len(df)} rows")
print(f"Groups: {df['group'].value_counts().to_dict()}")

# Extract numeric values
df['Block_num'] = df['Block'].str.extract(r'B(\d+)').astype(int)
df['Trial_within_block'] = df['Trial'].str.extract(r'T(\d+)').astype(int)  # 1, 2, or 3
df['Day_num'] = df['Day'].str.extract(r'D(\d+)').astype(int)

# Create a unique block identifier for each subject-day-block combination
df['block_id'] = df['subject'] + '_' + df['Day'] + '_' + df['Block']

df = df.dropna(subset=['symb', 'perm', 'subject'])

print(f"\nAfter cleaning: {len(df)} rows")
print(f"Trial within block range: {df['Trial_within_block'].min()} to {df['Trial_within_block'].max()}")
print(f"Subjects: {df['subject'].nunique()}")
print(f"Unique blocks: {df['block_id'].nunique()}")

# ============= WITHIN-BLOCK TRIAL ANALYSIS =============
print("\n" + "="*80)
print("WITHIN-BLOCK TRIAL MIXED-EFFECTS MODEL FOR SYMBOLIC ENTROPY")
print("="*80)
print("\nThis tests whether entropy increases across consecutive trials WITHIN each block")
print("(i.e., T01 -> T02 -> T03 within the same block)")

# Model with Trial_within_block as predictor
# Random effects: (1 | subject) and (1 | block_id) to account for block-level clustering
formula = 'symb ~ Trial_within_block + C(group) + Day_num + Trial_within_block:C(group) + Trial_within_block:Day_num'

print(f"\nModel formula: {formula}")
print("Random effects: (1 | subject)")
print("Note: Trial_within_block = 1, 2, or 3 (position within each block)\n")

try:
    # Fit model with subject random effect
    model_symb = mixedlm(formula, df, groups=df['subject'])
    result_symb = model_symb.fit(method='lbfgs')
    
    print("-"*80)
    print("MODEL SUMMARY - Symbolic Entropy (Within-Block Trial Effect)")
    print("-"*80)
    print(result_symb.summary())
    
    # Extract key statistics
    params = result_symb.params
    pvalues = result_symb.pvalues
    conf_int = result_symb.conf_int()
    
    print("\n" + "="*80)
    print("KEY FINDINGS:")
    print("="*80)
    
    # Within-block trial effect
    trial_coef = params['Trial_within_block']
    trial_pval = pvalues['Trial_within_block']
    trial_ci_low = conf_int.loc['Trial_within_block', 0]
    trial_ci_high = conf_int.loc['Trial_within_block', 1]
    
    print(f"\n1. WITHIN-BLOCK TRIAL EFFECT (main effect):")
    print(f"   Coefficient: {trial_coef:.6f}")
    print(f"   Interpretation: Change in entropy per trial within block")
    print(f"   p-value: {trial_pval:.6f}")
    print(f"   95% CI: [{trial_ci_low:.6f}, {trial_ci_high:.6f}]")
    
    if trial_pval < 0.05:
        direction = "INCREASES" if trial_coef > 0 else "DECREASES"
        print(f"   *** SIGNIFICANT: Entropy {direction} across consecutive trials within block ***")
        print(f"   Expected change from T01 to T03: {trial_coef * 2:.6f}")
    else:
        print(f"   Not significant (p >= 0.05)")
        print(f"   No evidence of systematic within-block entropy change")
    
    # Trial × group interaction
    if 'Trial_within_block:C(group)[T.young]' in params.index:
        int_group_coef = params['Trial_within_block:C(group)[T.young]']
        int_group_pval = pvalues['Trial_within_block:C(group)[T.young]']
        
        old_slope = trial_coef
        young_slope = trial_coef + int_group_coef
        
        print(f"\n2. TRIAL × GROUP interaction:")
        print(f"   Coefficient (young vs old): {int_group_coef:.6f}, p = {int_group_pval:.6f}")
        print(f"   Within-block trial slope for OLD: {old_slope:.6f}")
        print(f"   Within-block trial slope for YOUNG: {young_slope:.6f}")
        
        if int_group_pval < 0.05:
            print(f"   *** SIGNIFICANT: Groups differ in within-block trial effect ***")
        else:
            print(f"   Not significant - both groups show similar within-block pattern")
    
    # Trial × Day interaction
    if 'Trial_within_block:Day_num' in params.index:
        int_day_coef = params['Trial_within_block:Day_num']
        int_day_pval = pvalues['Trial_within_block:Day_num']
        
        print(f"\n3. TRIAL × DAY interaction:")
        print(f"   Coefficient: {int_day_coef:.6f}, p = {int_day_pval:.6f}")
        
        if int_day_pval < 0.05:
            print(f"   *** SIGNIFICANT: Within-block trial effect differs by day ***")
        else:
            print(f"   Not significant")
    
except Exception as e:
    print(f"Error fitting model: {e}")
    import traceback
    traceback.print_exc()
    result_symb = None

# ============= DESCRIPTIVE STATISTICS =============
print("\n" + "="*80)
print("DESCRIPTIVE STATISTICS: Mean entropy by trial position within block")
print("="*80)

for group_name in ['old', 'young']:
    print(f"\n{group_name.upper()} GROUP:")
    group_data = df[df['group'] == group_name]
    
    means = group_data.groupby('Trial_within_block')['symb'].agg(['mean', 'std', 'count'])
    print(means)
    
    # Paired t-test: T01 vs T03 within same blocks
    # Need to pivot data to have T01, T02, T03 as columns for each block
    pivot = group_data.pivot_table(values='symb', index='block_id', columns='Trial_within_block')
    
    if 1 in pivot.columns and 3 in pivot.columns:
        valid_blocks = pivot.dropna(subset=[1, 3])
        if len(valid_blocks) > 0:
            t_stat, t_pval = stats.ttest_rel(valid_blocks[1], valid_blocks[3])
            mean_diff = valid_blocks[3].mean() - valid_blocks[1].mean()
            print(f"\n   Paired t-test (T01 vs T03 within same blocks):")
            print(f"   n blocks = {len(valid_blocks)}, t = {t_stat:.4f}, p = {t_pval:.6f}")
            print(f"   Mean difference (T03 - T01) = {mean_diff:.6f}")
            if t_pval < 0.05:
                print(f"   *** SIGNIFICANT difference between T01 and T03 ***")

# ============= VISUALIZATION =============
print("\n\nCreating visualizations...")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

# 1. Overall within-block trend by group (mean ± SEM)
ax = axes[0, 0]
for group_name in ['old', 'young']:
    group_data = df[df['group'] == group_name]
    trial_stats = group_data.groupby('Trial_within_block')['symb'].agg(['mean', 'sem']).reset_index()
    
    color = '#d62728' if group_name == 'old' else '#1f77b4'
    ax.errorbar(trial_stats['Trial_within_block'], trial_stats['mean'], 
                yerr=trial_stats['sem'], 
                marker='o', linewidth=3, markersize=10, capsize=8,
                label=f'{group_name.upper()}', color=color, alpha=0.8)

ax.set_xlabel('Trial Position Within Block', fontsize=13, fontweight='bold')
ax.set_ylabel('Symbolic Entropy', fontsize=13, fontweight='bold')
ax.set_title('Within-Block Entropy Trend\n(Pooled Across All Blocks)', fontsize=14, fontweight='bold')
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(['T01', 'T02', 'T03'])
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# 2. Separate by Day
ax = axes[0, 1]
for day in ['D01', 'D02']:
    for group_name in ['old', 'young']:
        subset = df[(df['Day'] == day) & (df['group'] == group_name)]
        trial_means = subset.groupby('Trial_within_block')['symb'].mean().reset_index()
        
        color = '#d62728' if group_name == 'old' else '#1f77b4'
        linestyle = '-' if day == 'D01' else '--'
        marker = 'o' if day == 'D01' else 's'
        ax.plot(trial_means['Trial_within_block'], trial_means['symb'], 
                marker=marker, linestyle=linestyle, linewidth=2, markersize=8,
                label=f'{group_name.upper()} {day}', color=color, alpha=0.8)

ax.set_xlabel('Trial Position Within Block', fontsize=13, fontweight='bold')
ax.set_ylabel('Symbolic Entropy', fontsize=13, fontweight='bold')
ax.set_title('Within-Block Trend by Day and Group', fontsize=14, fontweight='bold')
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(['T01', 'T02', 'T03'])
ax.legend(fontsize=9, ncol=2)
ax.grid(True, alpha=0.3)

# 3. Separate by Block
ax = axes[0, 2]
for block_num in [1, 2, 3]:
    for group_name in ['old', 'young']:
        subset = df[(df['Block_num'] == block_num) & (df['group'] == group_name)]
        trial_means = subset.groupby('Trial_within_block')['symb'].mean().reset_index()
        
        color = '#d62728' if group_name == 'old' else '#1f77b4'
        linestyle = ['-', '--', ':'][block_num - 1]
        ax.plot(trial_means['Trial_within_block'], trial_means['symb'], 
                marker='o', linestyle=linestyle, linewidth=2, markersize=6,
                label=f'{group_name.upper()} B{block_num:02d}', color=color, alpha=0.7)

ax.set_xlabel('Trial Position Within Block', fontsize=13, fontweight='bold')
ax.set_ylabel('Symbolic Entropy', fontsize=13, fontweight='bold')
ax.set_title('Within-Block Trend by Block Number', fontsize=14, fontweight='bold')
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(['T01', 'T02', 'T03'])
ax.legend(fontsize=8, ncol=2)
ax.grid(True, alpha=0.3)

# 4. Violin plot - OLD group
ax = axes[1, 0]
old_data = df[df['group'] == 'old'].copy()
old_data['Trial_label'] = 'T' + old_data['Trial_within_block'].astype(str).str.zfill(2)
sns.violinplot(data=old_data, x='Trial_label', y='symb', ax=ax, color='#d62728', inner='box')
ax.set_xlabel('Trial Position Within Block', fontsize=13, fontweight='bold')
ax.set_ylabel('Symbolic Entropy', fontsize=13, fontweight='bold')
ax.set_title('OLD Group: Entropy Distribution', fontsize=14, fontweight='bold')

# 5. Violin plot - YOUNG group
ax = axes[1, 1]
young_data = df[df['group'] == 'young'].copy()
young_data['Trial_label'] = 'T' + young_data['Trial_within_block'].astype(str).str.zfill(2)
sns.violinplot(data=young_data, x='Trial_label', y='symb', ax=ax, color='#1f77b4', inner='box')
ax.set_xlabel('Trial Position Within Block', fontsize=13, fontweight='bold')
ax.set_ylabel('Symbolic Entropy', fontsize=13, fontweight='bold')
ax.set_title('YOUNG Group: Entropy Distribution', fontsize=14, fontweight='bold')

# 6. Individual block trajectories (sample)
ax = axes[1, 2]
# Plot a random sample of individual block trajectories
np.random.seed(42)
sample_blocks = np.random.choice(df['block_id'].unique(), size=min(30, df['block_id'].nunique()), replace=False)

for block_id in sample_blocks:
    block_data = df[df['block_id'] == block_id].sort_values('Trial_within_block')
    if len(block_data) == 3:  # Only complete blocks
        group_name = block_data['group'].iloc[0]
        color = '#d62728' if group_name == 'old' else '#1f77b4'
        ax.plot(block_data['Trial_within_block'], block_data['symb'], 
                marker='o', alpha=0.3, linewidth=1, markersize=4, color=color)

ax.set_xlabel('Trial Position Within Block', fontsize=13, fontweight='bold')
ax.set_ylabel('Symbolic Entropy', fontsize=13, fontweight='bold')
ax.set_title('Individual Block Trajectories (Sample)', fontsize=14, fontweight='bold')
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(['T01', 'T02', 'T03'])
ax.grid(True, alpha=0.3)

plt.tight_layout()

# Save figure
output_path = '/groups/jgoodwin/czeyi/balance/figures/within_block_trial_entropy_trend.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\nSaved figure to: {output_path}")

# ============= SAVE RESULTS =============
if result_symb is not None:
    output_file = '/groups/jgoodwin/czeyi/balance/figures/within_block_trial_analysis_results.txt'
    with open(output_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write("WITHIN-BLOCK TRIAL MIXED-EFFECTS ANALYSIS RESULTS\n")
        f.write("="*80 + "\n\n")
        f.write("Research Question: Does entropy increase across consecutive trials\n")
        f.write("within the same block (T01 -> T02 -> T03)?\n")
        f.write("This tests SHORT-TERM fatigue accumulation within each ~3-trial block.\n\n")
        f.write(f"Model: {formula}\n")
        f.write("Random effects: (1 | subject)\n\n")
        f.write(result_symb.summary().as_text())
        f.write("\n\n" + "="*80 + "\n")
        f.write("INTERPRETATION:\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"1. Within-block trial effect (main):\n")
        f.write(f"   Coefficient: {trial_coef:.6f}, p = {trial_pval:.6f}\n")
        f.write(f"   95% CI: [{trial_ci_low:.6f}, {trial_ci_high:.6f}]\n")
        if trial_pval < 0.05:
            f.write(f"   SIGNIFICANT: Entropy {'increases' if trial_coef > 0 else 'decreases'}\n")
            f.write(f"   Expected change T01→T03: {trial_coef * 2:.6f}\n")
        else:
            f.write(f"   Not significant - no systematic within-block entropy trend\n")
        
        if 'Trial_within_block:C(group)[T.young]' in params.index:
            f.write(f"\n2. Trial × Group interaction:\n")
            f.write(f"   Coefficient: {int_group_coef:.6f}, p = {int_group_pval:.6f}\n")
            f.write(f"   OLD slope: {old_slope:.6f}\n")
            f.write(f"   YOUNG slope: {young_slope:.6f}\n")
        
        if 'Trial_within_block:Day_num' in params.index:
            f.write(f"\n3. Trial × Day interaction:\n")
            f.write(f"   Coefficient: {int_day_coef:.6f}, p = {int_day_pval:.6f}\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("CONCLUSION:\n")
        f.write("="*80 + "\n")
        if trial_pval < 0.05:
            f.write("There IS evidence of within-block entropy changes across consecutive trials.\n")
        else:
            f.write("There is NO significant evidence that entropy systematically increases\n")
            f.write("across consecutive trials within blocks (T01→T02→T03).\n")
            f.write("This suggests that short-term fatigue (within ~3 trials) does not\n")
            f.write("manifest as increasing symbolic entropy.\n")
    
    print(f"Saved results to: {output_file}")

print("\n" + "="*80)
print("WITHIN-BLOCK ANALYSIS COMPLETE")
print("="*80)
