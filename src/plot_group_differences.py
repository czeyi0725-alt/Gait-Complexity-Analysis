import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Read the data
df = pd.read_csv('figures/individual_entropies_extracted.csv')

# Pre-compute stats for annotations and later panels
old_data = df[df['group']=='old']['symb']
young_data = df[df['group']=='young']['symb']
stat, p_value = stats.mannwhitneyu(old_data, young_data, alternative='greater')
old_mean, young_mean = old_data.mean(), young_data.mean()
old_sem, young_sem = stats.sem(old_data), stats.sem(young_data)
cohens_d = (old_mean - young_mean) / np.sqrt((old_data.var(ddof=1) + young_data.var(ddof=1)) / 2)

# Create a figure with multiple subplots
# Set the style to a basic theme
plt.style.use('default')
fig = plt.figure(figsize=(15, 10))
# Set general style parameters
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# 1. Violin plot with individual points (black and white version)
plt.subplot(221)
# Use grayscale violin plots
parts = plt.violinplot([df[df['group']=='old']['symb'].values, 
                        df[df['group']=='young']['symb'].values],
                       positions=[0, 1], showmeans=False, showmedians=False, showextrema=False)
for pc in parts['bodies']:
    pc.set_facecolor('lightgray')
    pc.set_edgecolor('black')
    pc.set_alpha(0.7)

# Add boxplot overlay
bp = plt.boxplot([df[df['group']=='old']['symb'].values, 
                  df[df['group']=='young']['symb'].values],
                 positions=[0, 1], widths=0.15, patch_artist=True,
                 boxprops=dict(facecolor='white', edgecolor='black'),
                 medianprops=dict(color='black', linewidth=2),
                 whiskerprops=dict(color='black'),
                 capprops=dict(color='black'))

# Calculate median values (the widest part of the box)
old_median_val = df[df['group']=='old']['symb'].median()
young_median_val = df[df['group']=='young']['symb'].median()

# Draw horizontal lines at median positions
plt.axhline(y=old_median_val, color='darkgray', linewidth=2, linestyle='--', alpha=0.6, zorder=1)
plt.axhline(y=young_median_val, color='darkgray', linewidth=2, linestyle='--', alpha=0.6, zorder=1)

# Add text labels - old on the left, young on the right
plt.text(-0.5, old_median_val, f'Old: {old_median_val:.3f}', 
         color='black', fontsize=11, fontweight='bold', va='center', ha='left',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', alpha=0.8))
plt.text(1.5, young_median_val, f'Young: {young_median_val:.3f}', 
         color='black', fontsize=11, fontweight='bold', va='center', ha='right',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='black', alpha=0.8))

plt.title('A. Distribution of Symbolic Entropy by Group (Median Values)')
plt.ylabel('Symbolic Entropy')
ax = plt.gca()
ax.set_xticks([0, 1])
ax.set_xticklabels([f'old\n(n={len(old_data)})', f'young\n(n={len(young_data)})'])
plt.xlim(-0.6, 1.6)

# Add p-value and effect size annotation at the top of panel A
ymax = ax.get_ylim()[1]
ax.text(0.5, ymax - 0.02, f'Old > Young: p={p_value:.2e}, d={cohens_d:.3f}',
    ha='center', va='top', fontsize=11)

# 2. Kernel Density Estimation plot
plt.subplot(222)
sns.kdeplot(data=df[df['group']=='old'], x='symb', label='Old', 
            fill=True, alpha=0.5, color='red')
sns.kdeplot(data=df[df['group']=='young'], x='symb', label='Young', 
            fill=True, alpha=0.5, color='blue')
plt.title('B. Density Distribution Comparison')
plt.xlabel('Symbolic Entropy')
plt.ylabel('Density')
plt.legend()

# 3. Enhanced Box Plot
plt.subplot(223)
bp = sns.boxplot(data=df, x='group', y='symb', showfliers=False)
# Add individual points with jitter (smaller and lighter)
sns.swarmplot(data=df, x='group', y='symb', color='black', alpha=0.35, size=2.5)
plt.title('C. Box Plot with Individual Points')
plt.ylabel('Symbolic Entropy')

# 4. Statistical comparison
plt.subplot(224)
# stats already computed above

# Plot means with error bars
plt.bar(['Old', 'Young'], [old_mean, young_mean], 
        yerr=[old_sem, young_sem], capsize=5,
        color=['red', 'blue'], alpha=0.6)
plt.title(f'D. Group Means\np={p_value:.4f}')
plt.ylabel('Mean Symbolic Entropy (± SEM)')

# Add effect size
plt.text(0.5, 2.15, f"Cohen's d = {cohens_d:.3f}", ha='center')

# Adjust layout and save
plt.tight_layout()
plt.savefig('figures/enhanced_group_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# Print summary statistics
print("\nSummary Statistics:")
print("Old Group:")
print(f"Mean ± SD: {old_mean:.3f} ± {old_data.std():.3f}")
print(f"N = {len(old_data)}")
print("\nYoung Group:")
print(f"Mean ± SD: {young_mean:.3f} ± {young_data.std():.3f}")
print(f"N = {len(young_data)}")
print(f"\nMann-Whitney U test p-value: {p_value:.4f}")
print(f"Cohen's d: {cohens_d:.3f}")