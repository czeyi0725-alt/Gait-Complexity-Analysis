#!/usr/bin/env python3
"""
Separate within-block trial analysis for OLD and YOUNG groups.
Tests fatigue accumulation within blocks independently for each age group.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import sys

try:
    import statsmodels.api as sm
    from statsmodels.formula.api import mixedlm
except ImportError:
    print("Error: statsmodels not installed.")
    sys.exit(1)

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)

# Read data
print("Loading individual entropy data...")
df = pd.read_csv('/groups/jgoodwin/czeyi/balance/figures/individual_entropies_extracted.csv')

# Extract numeric values
df['Block_num'] = df['Block'].str.extract(r'B(\d+)').astype(int)
df['Trial_within_block'] = df['Trial'].str.extract(r'T(\d+)').astype(int)
df['Day_num'] = df['Day'].str.extract(r'D(\d+)').astype(int)
df['block_id'] = df['subject'] + '_' + df['Day'] + '_' + df['Block']

df = df.dropna(subset=['symb', 'perm', 'subject'])

print(f"Total data: {len(df)} rows, {df['subject'].nunique()} subjects")
print(f"OLD: {len(df[df['group']=='old'])} rows, {df[df['group']=='old']['subject'].nunique()} subjects")
print(f"YOUNG: {len(df[df['group']=='young'])} rows, {df[df['group']=='young']['subject'].nunique()} subjects")

# ============= SEPARATE ANALYSIS BY GROUP =============
results = {}

for group_name in ['old', 'young']:
    print("\n" + "="*80)
    print(f"{group_name.upper()} GROUP - WITHIN-BLOCK TRIAL ANALYSIS")
    print("="*80)
    
    group_data = df[df['group'] == group_name].copy()
    
    print(f"\nSample size: {len(group_data)} observations")
    print(f"Subjects: {group_data['subject'].nunique()}")
    print(f"Blocks: {group_data['block_id'].nunique()}")
    
    # ========== MODEL 1: Simple model with trial effect ==========
    formula1 = 'symb ~ Trial_within_block'
    print(f"\n--- Model 1 (Simple): {formula1} ---")
    
    try:
        model1 = mixedlm(formula1, group_data, groups=group_data['subject'])
        result1 = model1.fit(method='lbfgs')
        
        trial_coef1 = result1.params['Trial_within_block']
        trial_pval1 = result1.pvalues['Trial_within_block']
        trial_ci1 = result1.conf_int().loc['Trial_within_block']
        
        print(f"Trial coefficient: {trial_coef1:.6f}")
        print(f"p-value: {trial_pval1:.6f}")
        print(f"95% CI: [{trial_ci1[0]:.6f}, {trial_ci1[1]:.6f}]")
        
        if trial_pval1 < 0.05:
            print(f"*** SIGNIFICANT within-block trial effect ***")
        elif trial_pval1 < 0.10:
            print(f"* Marginally significant (p < 0.10) *")
        else:
            print(f"Not significant")
        
        results[f'{group_name}_simple'] = {
            'coef': trial_coef1,
            'pval': trial_pval1,
            'ci_low': trial_ci1[0],
            'ci_high': trial_ci1[1],
            'result': result1
        }
        
    except Exception as e:
        print(f"Error fitting model 1: {e}")
        results[f'{group_name}_simple'] = None
    
    # ========== MODEL 2: With Day effect ==========
    formula2 = 'symb ~ Trial_within_block + Day_num + Trial_within_block:Day_num'
    print(f"\n--- Model 2 (With Day): {formula2} ---")
    
    try:
        model2 = mixedlm(formula2, group_data, groups=group_data['subject'])
        result2 = model2.fit(method='lbfgs')
        
        trial_coef2 = result2.params['Trial_within_block']
        trial_pval2 = result2.pvalues['Trial_within_block']
        trial_ci2 = result2.conf_int().loc['Trial_within_block']
        
        print(f"Trial coefficient: {trial_coef2:.6f}")
        print(f"p-value: {trial_pval2:.6f}")
        print(f"95% CI: [{trial_ci2[0]:.6f}, {trial_ci2[1]:.6f}]")
        
        if 'Trial_within_block:Day_num' in result2.params.index:
            int_coef = result2.params['Trial_within_block:Day_num']
            int_pval = result2.pvalues['Trial_within_block:Day_num']
            print(f"\nTrial × Day interaction: coef={int_coef:.6f}, p={int_pval:.6f}")
        
        if trial_pval2 < 0.05:
            print(f"*** SIGNIFICANT within-block trial effect ***")
        elif trial_pval2 < 0.10:
            print(f"* Marginally significant (p < 0.10) *")
        
        results[f'{group_name}_day'] = {
            'coef': trial_coef2,
            'pval': trial_pval2,
            'ci_low': trial_ci2[0],
            'ci_high': trial_ci2[1],
            'result': result2
        }
        
    except Exception as e:
        print(f"Error fitting model 2: {e}")
        results[f'{group_name}_day'] = None
    
    # ========== DESCRIPTIVE STATS & PAIRED TESTS ==========
    print(f"\n--- Descriptive Statistics ---")
    
    # Mean by trial position
    trial_means = group_data.groupby('Trial_within_block')['symb'].agg(['mean', 'std', 'sem', 'count'])
    print("\nMean entropy by trial position:")
    print(trial_means)
    
    # Calculate mean change from T01 to T03
    mean_t01 = trial_means.loc[1, 'mean']
    mean_t03 = trial_means.loc[3, 'mean']
    mean_change = mean_t03 - mean_t01
    pct_change = (mean_change / mean_t01) * 100
    
    print(f"\nMean change T01→T03: {mean_change:.6f} ({pct_change:.3f}%)")
    
    # Paired t-test (block-level)
    pivot = group_data.pivot_table(values='symb', index='block_id', columns='Trial_within_block')
    
    if 1 in pivot.columns and 3 in pivot.columns:
        valid_blocks = pivot.dropna(subset=[1, 3])
        
        if len(valid_blocks) >= 5:  # Need reasonable sample size
            t_stat, t_pval = stats.ttest_rel(valid_blocks[1], valid_blocks[3])
            
            # Calculate Cohen's d for paired samples
            diffs = valid_blocks[3] - valid_blocks[1]
            cohens_d = diffs.mean() / diffs.std()
            
            # Bootstrap CI for mean difference
            n_bootstrap = 5000
            np.random.seed(42)
            bootstrap_diffs = []
            for _ in range(n_bootstrap):
                sample_idx = np.random.choice(len(diffs), size=len(diffs), replace=True)
                bootstrap_diffs.append(diffs.iloc[sample_idx].mean())
            
            ci_low = np.percentile(bootstrap_diffs, 2.5)
            ci_high = np.percentile(bootstrap_diffs, 97.5)
            
            print(f"\nPaired t-test (T01 vs T03, block-level):")
            print(f"  n blocks: {len(valid_blocks)}")
            print(f"  t-statistic: {t_stat:.4f}")
            print(f"  p-value: {t_pval:.6f}")
            print(f"  Mean difference: {diffs.mean():.6f}")
            print(f"  95% CI (bootstrap): [{ci_low:.6f}, {ci_high:.6f}]")
            print(f"  Cohen's d: {cohens_d:.4f}")
            
            if t_pval < 0.05:
                print(f"  *** SIGNIFICANT increase from T01 to T03 ***")
            elif t_pval < 0.10:
                print(f"  * Marginally significant (p < 0.10) *")
            else:
                print(f"  Not significant")
            
            results[f'{group_name}_paired'] = {
                't_stat': t_stat,
                'pval': t_pval,
                'mean_diff': diffs.mean(),
                'ci_low': ci_low,
                'ci_high': ci_high,
                'cohens_d': cohens_d,
                'n_blocks': len(valid_blocks)
            }
    
    # Linear regression on individual trials (not accounting for clustering)
    from sklearn.linear_model import LinearRegression
    X = group_data['Trial_within_block'].values.reshape(-1, 1)
    y = group_data['symb'].values
    
    reg = LinearRegression().fit(X, y)
    slope = reg.coef_[0]
    r2 = reg.score(X, y)
    
    # Pearson correlation
    corr, corr_pval = stats.pearsonr(group_data['Trial_within_block'], group_data['symb'])
    
    print(f"\nSimple linear regression (ignoring clustering):")
    print(f"  Slope: {slope:.6f}")
    print(f"  R²: {r2:.6f}")
    print(f"  Pearson r: {corr:.4f}, p={corr_pval:.6f}")

# ============= COMPARISON BETWEEN GROUPS =============
print("\n" + "="*80)
print("COMPARISON: OLD vs YOUNG")
print("="*80)

if results.get('old_simple') and results.get('young_simple'):
    old_coef = results['old_simple']['coef']
    old_pval = results['old_simple']['pval']
    young_coef = results['young_simple']['coef']
    young_pval = results['young_simple']['pval']
    
    print(f"\nWithin-block trial slope (simple model):")
    print(f"  OLD:   {old_coef:.6f} (p={old_pval:.6f})")
    print(f"  YOUNG: {young_coef:.6f} (p={young_pval:.6f})")
    print(f"  Difference: {old_coef - young_coef:.6f}")

if results.get('old_paired') and results.get('young_paired'):
    old_diff = results['old_paired']['mean_diff']
    old_pval_paired = results['old_paired']['pval']
    young_diff = results['young_paired']['mean_diff']
    young_pval_paired = results['young_paired']['pval']
    
    print(f"\nMean change T01→T03 (paired tests):")
    print(f"  OLD:   {old_diff:.6f} (p={old_pval_paired:.6f}, d={results['old_paired']['cohens_d']:.4f})")
    print(f"  YOUNG: {young_diff:.6f} (p={young_pval_paired:.6f}, d={results['young_paired']['cohens_d']:.4f})")

# ============= VISUALIZATION =============
print("\n\nCreating visualizations...")

fig = plt.figure(figsize=(18, 14))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Row 1: Line plots with error bars
for idx, group_name in enumerate(['old', 'young']):
    ax = fig.add_subplot(gs[0, idx])
    
    group_data = df[df['group'] == group_name]
    trial_stats = group_data.groupby('Trial_within_block')['symb'].agg(['mean', 'sem', 'std']).reset_index()
    
    color = '#d62728' if group_name == 'old' else '#1f77b4'
    
    # Error bars (SEM)
    ax.errorbar(trial_stats['Trial_within_block'], trial_stats['mean'], 
                yerr=trial_stats['sem'], 
                marker='o', linewidth=3, markersize=12, capsize=10,
                label=f'Mean ± SEM', color=color, alpha=0.8, zorder=3)
    
    # Add regression line
    from scipy.stats import linregress
    slope, intercept, r_value, p_value, std_err = linregress(trial_stats['Trial_within_block'], 
                                                               trial_stats['mean'])
    x_line = np.array([1, 2, 3])
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, '--', color=color, alpha=0.6, linewidth=2, 
            label=f'Linear fit (slope={slope:.4f})')
    
    ax.set_xlabel('Trial Position Within Block', fontsize=13, fontweight='bold')
    ax.set_ylabel('Symbolic Entropy', fontsize=13, fontweight='bold')
    ax.set_title(f'{group_name.upper()} Group\nWithin-Block Entropy Trend', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(['T01', 'T02', 'T03'])
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Add statistics text
    if results.get(f'{group_name}_simple'):
        coef = results[f'{group_name}_simple']['coef']
        pval = results[f'{group_name}_simple']['pval']
        sig_text = "***" if pval < 0.001 else "**" if pval < 0.01 else "*" if pval < 0.05 else "n.s."
        ax.text(0.05, 0.95, f'Mixed model:\nβ={coef:.5f}\np={pval:.4f} {sig_text}',
                transform=ax.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Row 1, Col 3: Direct comparison
ax = fig.add_subplot(gs[0, 2])
for group_name in ['old', 'young']:
    group_data = df[df['group'] == group_name]
    trial_means = group_data.groupby('Trial_within_block')['symb'].mean().reset_index()
    
    color = '#d62728' if group_name == 'old' else '#1f77b4'
    ax.plot(trial_means['Trial_within_block'], trial_means['symb'], 
            marker='o', linewidth=3, markersize=10,
            label=f'{group_name.upper()}', color=color, alpha=0.8)

ax.set_xlabel('Trial Position Within Block', fontsize=13, fontweight='bold')
ax.set_ylabel('Symbolic Entropy', fontsize=13, fontweight='bold')
ax.set_title('Direct Comparison\n(Mean Entropy)', fontsize=14, fontweight='bold')
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(['T01', 'T02', 'T03'])
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

# Row 2: Scatter plots with individual block trajectories (sample)
for idx, group_name in enumerate(['old', 'young']):
    ax = fig.add_subplot(gs[1, idx])
    
    group_data = df[df['group'] == group_name]
    
    # Sample random blocks
    np.random.seed(42)
    sample_blocks = np.random.choice(group_data['block_id'].unique(), 
                                     size=min(50, group_data['block_id'].nunique()), 
                                     replace=False)
    
    color = '#d62728' if group_name == 'old' else '#1f77b4'
    
    for block_id in sample_blocks:
        block_data = group_data[group_data['block_id'] == block_id].sort_values('Trial_within_block')
        if len(block_data) == 3:
            ax.plot(block_data['Trial_within_block'], block_data['symb'], 
                    marker='o', alpha=0.15, linewidth=0.8, markersize=3, color=color)
    
    # Overlay mean
    trial_means = group_data.groupby('Trial_within_block')['symb'].mean().reset_index()
    ax.plot(trial_means['Trial_within_block'], trial_means['symb'], 
            marker='o', linewidth=4, markersize=12, color=color, 
            label='Mean', zorder=100, markeredgewidth=2, markeredgecolor='white')
    
    ax.set_xlabel('Trial Position', fontsize=12, fontweight='bold')
    ax.set_ylabel('Symbolic Entropy', fontsize=12, fontweight='bold')
    ax.set_title(f'{group_name.upper()}: Individual Blocks (n=50)', fontsize=13, fontweight='bold')
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(['T01', 'T02', 'T03'])
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

# Row 2, Col 3: Distribution comparison (paired differences)
ax = fig.add_subplot(gs[1, 2])

for group_name in ['old', 'young']:
    group_data = df[df['group'] == group_name]
    pivot = group_data.pivot_table(values='symb', index='block_id', columns='Trial_within_block')
    
    if 1 in pivot.columns and 3 in pivot.columns:
        valid_blocks = pivot.dropna(subset=[1, 3])
        diffs = valid_blocks[3] - valid_blocks[1]
        
        color = '#d62728' if group_name == 'old' else '#1f77b4'
        ax.hist(diffs, bins=30, alpha=0.6, color=color, label=f'{group_name.upper()}', density=True)

ax.axvline(x=0, color='black', linestyle='--', linewidth=2, alpha=0.5, label='No change')
ax.set_xlabel('Entropy Change (T03 - T01)', fontsize=12, fontweight='bold')
ax.set_ylabel('Density', fontsize=12, fontweight='bold')
ax.set_title('Distribution of Within-Block Changes', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# Row 3: Box/violin plots
for idx, group_name in enumerate(['old', 'young']):
    ax = fig.add_subplot(gs[2, idx])
    
    group_data = df[df['group'] == group_name].copy()
    group_data['Trial_label'] = 'T' + group_data['Trial_within_block'].astype(str).str.zfill(2)
    
    color = '#d62728' if group_name == 'old' else '#1f77b4'
    
    parts = ax.violinplot([group_data[group_data['Trial_within_block']==i]['symb'].values 
                            for i in [1, 2, 3]],
                           positions=[1, 2, 3], widths=0.7,
                           showmeans=True, showmedians=True)
    
    for pc in parts['bodies']:
        pc.set_facecolor(color)
        pc.set_alpha(0.7)
    
    ax.set_xlabel('Trial Position', fontsize=12, fontweight='bold')
    ax.set_ylabel('Symbolic Entropy', fontsize=12, fontweight='bold')
    ax.set_title(f'{group_name.upper()}: Distribution by Trial', fontsize=13, fontweight='bold')
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(['T01', 'T02', 'T03'])
    ax.grid(True, alpha=0.3, axis='y')

# Row 3, Col 3: Effect sizes comparison
ax = fig.add_subplot(gs[2, 2])

if results.get('old_paired') and results.get('young_paired'):
    groups = ['OLD', 'YOUNG']
    effects = [results['old_paired']['cohens_d'], results['young_paired']['cohens_d']]
    pvals = [results['old_paired']['pval'], results['young_paired']['pval']]
    colors = ['#d62728', '#1f77b4']
    
    bars = ax.bar(groups, effects, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    
    # Add significance stars
    for i, (bar, pval) in enumerate(zip(bars, pvals)):
        height = bar.get_height()
        if pval < 0.001:
            sig = '***'
        elif pval < 0.01:
            sig = '**'
        elif pval < 0.05:
            sig = '*'
        elif pval < 0.10:
            sig = '†'
        else:
            sig = 'n.s.'
        
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                sig, ha='center', va='bottom', fontsize=16, fontweight='bold')
        ax.text(bar.get_x() + bar.get_width()/2., 0.005,
                f'p={pval:.3f}', ha='center', va='bottom', fontsize=9)
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax.set_ylabel("Cohen's d (T03 vs T01)", fontsize=12, fontweight='bold')
    ax.set_title('Effect Size Comparison\n(Paired within-block change)', fontsize=13, fontweight='bold')
    ax.set_ylim([min(effects) - 0.1, max(effects) + 0.15])
    ax.grid(True, alpha=0.3, axis='y')

plt.suptitle('SEPARATE ANALYSIS: Within-Block Fatigue Effects by Age Group', 
             fontsize=16, fontweight='bold', y=0.995)

# Save figure
output_path = '/groups/jgoodwin/czeyi/balance/figures/within_block_by_group_comparison.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\nSaved figure to: {output_path}")

# ============= SAVE RESULTS =============
output_file = '/groups/jgoodwin/czeyi/balance/figures/within_block_by_group_results.txt'
with open(output_file, 'w') as f:
    f.write("="*80 + "\n")
    f.write("SEPARATE WITHIN-BLOCK ANALYSIS BY AGE GROUP\n")
    f.write("="*80 + "\n\n")
    
    for group_name in ['old', 'young']:
        f.write("\n" + "-"*80 + "\n")
        f.write(f"{group_name.upper()} GROUP\n")
        f.write("-"*80 + "\n\n")
        
        if results.get(f'{group_name}_simple'):
            res = results[f'{group_name}_simple']
            f.write(f"Mixed-effects model (simple):\n")
            f.write(f"  Trial coefficient: {res['coef']:.6f}\n")
            f.write(f"  p-value: {res['pval']:.6f}\n")
            f.write(f"  95% CI: [{res['ci_low']:.6f}, {res['ci_high']:.6f}]\n")
            if res['pval'] < 0.05:
                f.write(f"  *** SIGNIFICANT ***\n")
            elif res['pval'] < 0.10:
                f.write(f"  * Marginally significant (p < 0.10) *\n")
            f.write("\n")
        
        if results.get(f'{group_name}_paired'):
            res = results[f'{group_name}_paired']
            f.write(f"Paired t-test (T01 vs T03):\n")
            f.write(f"  n blocks: {res['n_blocks']}\n")
            f.write(f"  t-statistic: {res['t_stat']:.4f}\n")
            f.write(f"  p-value: {res['pval']:.6f}\n")
            f.write(f"  Mean difference: {res['mean_diff']:.6f}\n")
            f.write(f"  95% CI: [{res['ci_low']:.6f}, {res['ci_high']:.6f}]\n")
            f.write(f"  Cohen's d: {res['cohens_d']:.4f}\n")
            if res['pval'] < 0.05:
                f.write(f"  *** SIGNIFICANT ***\n")
            elif res['pval'] < 0.10:
                f.write(f"  * Marginally significant (p < 0.10) *\n")
            f.write("\n")
    
    f.write("\n" + "="*80 + "\n")
    f.write("SUMMARY & INTERPRETATION\n")
    f.write("="*80 + "\n\n")
    
    if results.get('old_paired') and results.get('young_paired'):
        old_pval = results['old_paired']['pval']
        young_pval = results['young_paired']['pval']
        old_d = results['old_paired']['cohens_d']
        young_d = results['young_paired']['cohens_d']
        
        f.write(f"OLD group shows ")
        if old_pval < 0.05:
            f.write(f"SIGNIFICANT ")
        elif old_pval < 0.10:
            f.write(f"MARGINALLY SIGNIFICANT ")
        else:
            f.write(f"NO significant ")
        f.write(f"within-block entropy increase (p={old_pval:.4f}, d={old_d:.4f})\n\n")
        
        f.write(f"YOUNG group shows ")
        if young_pval < 0.05:
            f.write(f"SIGNIFICANT ")
        elif young_pval < 0.10:
            f.write(f"MARGINALLY SIGNIFICANT ")
        else:
            f.write(f"NO significant ")
        f.write(f"within-block entropy increase (p={young_pval:.4f}, d={young_d:.4f})\n\n")
        
        if old_pval < 0.10 and young_pval >= 0.10:
            f.write("\nCONCLUSION: Older adults show evidence of SHORT-TERM fatigue accumulation\n")
            f.write("within blocks (increasing entropy across T01→T02→T03), while younger adults\n")
            f.write("do not show this pattern. This suggests age-related differences in the\n")
            f.write("rate of fatigue development during consecutive balance tasks.\n")
        elif old_pval >= 0.10 and young_pval >= 0.10:
            f.write("\nCONCLUSION: Neither age group shows significant within-block entropy changes.\n")
            f.write("Short-term fatigue (across 3 consecutive trials) does not manifest as\n")
            f.write("systematic entropy increases in either older or younger adults.\n")

print(f"Saved results to: {output_file}")

print("\n" + "="*80)
print("SEPARATE GROUP ANALYSIS COMPLETE")
print("="*80)
