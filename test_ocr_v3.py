import os
import subprocess
from pathlib import Path

# ==========================================
# 設定
# ==========================================
INPUT_PDF_PATH = "./data/sample_exam.pdf"
OUTPUT_DIR = "./output_test"  # ここに出したい

def convert_pdf_final(pdf_path, output_dir):
    pdf_path = Path(pdf_path).resolve()
    output_dir = Path(output_dir).resolve()
    
    # CPU強制モード (必須)
    my_env = os.environ.copy()
    my_env["CUDA_VISIBLE_DEVICES"] = ""
    my_env["TORCH_DEVICE"] = "cpu"

    # コマンド構築
    # --output_dir オプションを使って出力先を明示する
    command = [
        "marker_single",
        str(pdf_path),
        "--output_dir", str(output_dir)
    ]

    print(f"Running command: {' '.join(command)}")
    print("Converting... (CPU処理のため、数分かかることがあります)")
    
    try:
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore',
            env=my_env
        )
        print("Success! 変換完了")
        # 成功したら、出力フォルダの中身を表示してみる
        print(f"\n--- {OUTPUT_DIR} の中身 ---")
        for item in output_dir.glob("**/*"):
             print(f"- {item.name}")
             
    except subprocess.CalledProcessError as e:
        print(f"Error: 変換失敗 (Exit Code: {e.returncode})")
        print("--- Error Output ---")
        print(e.stderr)

if __name__ == "__main__":
    # 出力フォルダはツールが作ってくれることが多いが、念のため親を作っておく
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    convert_pdf_final(INPUT_PDF_PATH, OUTPUT_DIR)