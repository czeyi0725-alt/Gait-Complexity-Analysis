#!/bin/bash

# --- 在这里定义您想分析的所有实验条件的“通用后缀”部分 ---
# 这个列表里现在只包含正确的 Dxx_Bxx_Txx 格式
common_suffixes=(
    "D01_B01_T01" "D01_B01_T02" "D01_B01_T03"
    "D01_B02_T01" "D01_B02_T02" "D01_B02_T03"
    "D01_B03_T01" "D01_B03_T02" "D01_B03_T03"
    "D02_B01_T01" "D02_B01_T02" "D02_B01_T03"
    "D02_B02_T01" "D02_B02_T02" "D02_B02_T03"
    "D02_B03_T01" "D02_B03_T02" "D02_B03_T03"
)
# -----------------------------------------------------------

echo "=== Starting to launch multiple gait analysis jobs with corrected logic ==="

for suffix in "${common_suffixes[@]}"
do
    echo "--> Preparing job for condition suffix: $suffix"

    # 为老年组和年轻组构建正确的、不同的路径
    OLD_PATH="gait_old_full/by_condition/G03_${suffix}"
    YOUNG_PATH="gait_young_full/by_condition/G01_${suffix}"

    JOB_SCRIPT_NAME="run_job_${suffix}.qsub"

    # 使用sed命令进行多次替换，生成最终的qsub脚本
    sed -e "s/CONDITION_PLACEHOLDER/${suffix}/g" \
        -e "s|OLD_CONDITION_PATH_PLACEHOLDER|${OLD_PATH}|g" \
        -e "s|YOUNG_CONDITION_PATH_PLACEHOLDER|${YOUNG_PATH}|g" \
        run_gait_template.qsub > "$JOB_SCRIPT_NAME"

    echo "    Created submission script: $JOB_SCRIPT_NAME"

    qsub "$JOB_SCRIPT_NAME" &
    sleep 1

    echo "--------------------------------------------------"
done

echo "=== All jobs have been submitted. ==="
