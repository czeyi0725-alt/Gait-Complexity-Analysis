#!/usr/bin/env python3
"""
递归扫描 root_dir 下所有 Sxxx_Gxx_Dxx_Bxx_Txx.csv，
按 Gxx_Dxx_Bxx_Txx 分类复制到 root_dir/by_condition/，
并逐个比对大小+MD5，保证复制完整可复现。
"""

import os, hashlib, shutil, sys, argparse, pathlib, subprocess

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    print("缺少 tqdm，正在尝试安装到用户目录 …")
    subprocess.run([sys.executable, "-m", "pip", "install", "--user", "tqdm"], check=True)
    from tqdm import tqdm

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main(root):
    root = pathlib.Path(root).resolve()
    out  = root / "by_condition"
    out.mkdir(exist_ok=True)

    # 收集源文件，排除 by_condition 自身
    csvs = [p for p in root.rglob("S*_G*_D*_B*_T*.csv") if out not in p.parents]
    if not csvs:
        print("未找到任何 CSV，目录是否正确？")
        return

    print(f"共发现 {len(csvs)} 个源文件，开始分类复制 …")

    copied, repaired = 0, 0
    for src in tqdm(csvs, unit="file"):
        fname = src.name                       # S001_G03_D01_B01_T01.csv
        cond  = fname.split("_", 1)[1][:-4]    # G03_D01_B01_T01
        dst_dir = out / cond
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / fname

        need_copy = (
            not dst.exists()
            or src.stat().st_size != dst.stat().st_size
            or md5(src) != md5(dst)
        )
        if need_copy:
            shutil.copy2(src, dst)
            repaired += dst.exists()
        copied += 1

    print(f"\n已检查 {len(csvs)}，复制/修复 {copied} 个文件，其中修复 {repaired} 个。")
    print("全部分类目录位于：", out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="分类复制并校验 CSV")
    ap.add_argument("root", help="根目录，例如 gait_young_full / gait_old_full")
    args = ap.parse_args()
    main(args.root)
