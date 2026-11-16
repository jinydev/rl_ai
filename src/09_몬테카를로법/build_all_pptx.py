import os
import subprocess
import shutil

base_dir = os.path.dirname(os.path.abspath(__file__))
subdirs = [
    base_dir,
    os.path.join(base_dir, "9_0_수학적기초"),
    os.path.join(base_dir, "9_1_몬테카를로법_기초"),
    os.path.join(base_dir, "9_2_몬테카를로법으로_정책_평가하기"),
    os.path.join(base_dir, "9_3_몬테카를로법_구현"),
    os.path.join(base_dir, "9_4_몬테카를로법으로_정책_제어하기"),
    os.path.join(base_dir, "9_5_오프-정책과_중요도_샘플링"),
    os.path.join(base_dir, "9_6_정리"),
]

build_script_src = os.path.join(base_dir, "build_pptx.py")

for d in subdirs:
    target_script = os.path.join(d, "build_pptx.py")
    if d != base_dir:
        shutil.copy2(build_script_src, target_script)
    
    print(f"=== Building PPTX in: {os.path.basename(d)} ===")
    res = subprocess.run(["python3", "build_pptx.py"], cwd=d, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED in {d}!\nError:\n{res.stderr}")
    else:
        print(res.stdout)

print("=== All 8 Presentations Built! ===")
