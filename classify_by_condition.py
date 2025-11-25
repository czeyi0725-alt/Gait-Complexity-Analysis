#!/usr/bin/env python3
import os, shutil, argparse

def classify(root_dir):
    out_base = os.path.join(root_dir, 'by_condition')
    os.makedirs(out_base, exist_ok=True)
    count = 0
    for cur, _, files in os.walk(root_dir):
        for f in files:
            if not f.lower().endswith('.csv') or not f.startswith('S'):
                continue
            parts = f.split('_', 1)
            if len(parts) != 2:
                continue
            cond = parts[1][:-4]   # 去掉 Sxxx_ 前缀 & .csv 后缀
            src  = os.path.join(cur, f)
            dst_dir = os.path.join(out_base, cond)
            os.makedirs(dst_dir, exist_ok=True)
            shutil.copy2(src, os.path.join(dst_dir, f))
            count += 1
            if count % 50 == 0:
                print(f"Copied {count} files...")

    print(f"\nDone! total copied: {count}")
    print(f"All classified under: {out_base}")

if __name__ == '__main__':
    p = argparse.ArgumentParser(description="按 Gxx_Dxx_Bxx_Txx 分类 CSV")
    p.add_argument('root', help="数据根目录，例如 gait_young_full")
    args = p.parse_args()
    classify(os.path.abspath(args.root))
