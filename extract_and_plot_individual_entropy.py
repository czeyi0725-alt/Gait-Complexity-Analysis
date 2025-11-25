#!/usr/bin/env python3
"""
extract_and_plot_individual_entropy.py

Parse all analysis_output.*.log files in the current directory, extract per-subject
symbolic and permutation entropy values, and plot sample-point distributions.

Outputs saved to ./figures/
"""
import re
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ranksums


def parse_log_file(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    # locate the Individual Entropy Results section
    m = re.search(r'--- Individual Entropy Results ---(.*?)(--- Group Average Entropy Results ---|--- Analysis Complete ---|$)', text, re.S)
    if not m:
        return []
    block = m.group(1)

    rows = []
    # Find all Group: labels with their positions
    group_labels = [(gm.start(), gm.group(1).strip()) for gm in re.finditer(r'Group:\s*(\w+)', block)]

    # Find all File: lines with positions
    for fm in re.finditer(r'^\s*File:\s*(.+)$', block, re.M):
        line = fm.group(1).strip()
        pos = fm.start()
        # assign group by finding the nearest preceding Group label
        assigned_group = None
        prev_labels = [lbl for (p,lbl) in group_labels if p <= pos]
        if prev_labels:
            assigned_group = prev_labels[-1]
        else:
            assigned_group = None

        parts = [p.strip() for p in line.split(',')]
        if len(parts) < 3:
            continue
        fname = parts[0]
        # normalize whitespace on the line to avoid wrapped numbers
        clean_line = re.sub(r'\s+', ' ', line)
        num_re = r'([-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)'
        symb_m = re.search(r'Symb:\s*' + num_re, clean_line)
        perm_m = re.search(r'Perm:\s*' + num_re, clean_line)
        if symb_m and perm_m:
            try:
                symb = float(symb_m.group(1))
                perm = float(perm_m.group(1))
            except Exception:
                # fallback strip non-numeric
                symb = float(re.sub(r'[^0-9.+\-eE]', '', symb_m.group(1)))
                perm = float(re.sub(r'[^0-9.+\-eE]', '', perm_m.group(1)))
            # try extract subject and condition from fname
            subj = None
            cond = None
            if '_' in fname:
                parts_fname = fname.split('_')
                if parts_fname[0].upper().startswith('S'):
                    subj = parts_fname[0]
                    cond = '_'.join(parts_fname[1:])
                else:
                    subj = parts_fname[0]
                    cond = '_'.join(parts_fname[1:])
            rows.append({'logfile': os.path.basename(path), 'group': assigned_group, 'file': fname, 'subject': subj, 'condition': cond, 'symb': symb, 'perm': perm})
    return rows


def aggregate_logs(pattern='analysis_output.*.log'):
    files = sorted(glob.glob(pattern))
    allrows = []
    for p in files:
        rows = parse_log_file(p)
        allrows.extend(rows)
    df = pd.DataFrame(allrows)
    if df.empty:
        print('No individual entropy entries found in logs')
        return df

    # derive Day/Block/Trial from condition if present (expect Dxx_Bxx_Txx inside)
    def parse_condition(cond):
        if not cond or not isinstance(cond, str):
            return (None, None, None)
        m = re.search(r'(D\d{2})_(B\d{2})_(T\d{2})', cond)
        if m:
            return m.group(1), m.group(2), m.group(3)
        return (None, None, None)

    df[['Day','Block','Trial']] = df['condition'].apply(lambda x: pd.Series(parse_condition(x)))
    return df


def plot_individual_distribution(df, outdir='figures'):
    os.makedirs(outdir, exist_ok=True)
    sns.set(style='whitegrid')

    # Overall symbolic entropy distribution: jittered points + box
    plt.figure(figsize=(8,6))
    ax = sns.boxplot(x='group', y='symb', data=df, showcaps=True, boxprops={'facecolor':'None'}, showfliers=False)
    ax = sns.swarmplot(x='group', y='symb', data=df, color='.25', size=5)
    plt.ylabel('Symbolic Entropy (per-subject)')
    plt.xlabel('Group')
    # overall ranksum
    old = df[df.group=='old']['symb'].dropna()
    young = df[df.group=='young']['symb'].dropna()
    try:
        stat, p = ranksums(old, young)
        plt.title(f'Symbolic Entropy per subject — ranksum p={p:.4f}')
    except Exception:
        plt.title('Symbolic Entropy per subject')
    plt.tight_layout()
    out1 = os.path.join(outdir, 'individual_symb_entropy_overall.png')
    plt.savefig(out1, dpi=150)
    plt.close()

    # By day: swarm + box per group per day
    plt.figure(figsize=(10,6))
    # create a combined column Day_Group for easy plotting
    df['Day_group'] = df['Day'].fillna('Unknown') + ' ' + df['group'].str.capitalize()
    order_days = sorted(df['Day'].dropna().unique())
    # build order: for each day, show old then young
    order = []
    for d in order_days:
        order.append(f'{d} Old')
        order.append(f'{d} Young')
    # fallback to unique Day_group if no days parsed
    if not order:
        order = sorted(df['Day_group'].unique())

    ax = sns.boxplot(x='Day_group', y='symb', data=df, order=order, notch=True)
    ax = sns.swarmplot(x='Day_group', y='symb', data=df, color='k', size=4, order=order)
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('Symbolic Entropy (per-subject)')
    plt.xlabel('Day and Group')
    plt.title('Symbolic Entropy per subject by Day and Group')

    # annotate per-day p-values centered between the two groups for that day
    y_max = df['symb'].max()
    y_min = df['symb'].min()
    y_range = y_max - y_min if y_max is not None and y_min is not None else 1
    for i,d in enumerate(order_days):
        old_vals = df[(df['Day']==d)&(df['group']=='old')]['symb'].dropna()
        young_vals = df[(df['Day']==d)&(df['group']=='young')]['symb'].dropna()
        if len(old_vals)>0 and len(young_vals)>0:
            try:
                stat,p = ranksums(old_vals, young_vals)
            except Exception:
                p = None
            xpos = i*2 + 0.5
            txt = f'p={p:.3f}' if p is not None else 'n/a'
            plt.text(xpos, y_max + 0.07*y_range, txt, ha='center', fontsize=9, fontweight='bold')
            if p is not None and p<0.05:
                plt.text(xpos, y_max + 0.03*y_range, '*', ha='center', color='r', fontsize=14)

    plt.tight_layout()
    out2 = os.path.join(outdir, 'individual_symb_entropy_by_day.png')
    plt.savefig(out2, dpi=150)
    plt.close()

    # Also save CSV of extracted individuals
    csv_out = os.path.join(outdir, 'individual_entropies_extracted.csv')
    df.to_csv(csv_out, index=False)
    return out1, out2, csv_out


def main():
    df = aggregate_logs('analysis_output.*.log')
    if df.empty:
        print('No data to plot. Exiting.')
        return
    out1, out2, csv_out = plot_individual_distribution(df)
    print('Saved:', out1)
    print('Saved:', out2)
    print('Saved extracted CSV:', csv_out)


if __name__ == '__main__':
    main()
