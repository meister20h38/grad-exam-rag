import os
import subprocess
from pathlib import Path

# ==========================================
# 設定
# ==========================================
INPUT_PDF_PATH = "./data/sample_exam.pdf"
OUTPUT_DIR = "./output_test"

def convert_pdf_safe_mode(pdf_path, output_dir):
    pdf_path = Path(pdf_path).resolve()
    output_dir = Path(output_dir).resolve()
    
    # ---------------------------------------------------------
    # 【重要】 リソース制限設定
    # ---------------------------------------------------------
    my_env = os.environ.copy()
    
    # 1. GPU無効化
    my_env["CUDA_VISIBLE_DEVICES"] = ""
    my_env["TORCH_DEVICE"] = "cpu"
    
    # 2. CPUスレッド数を「2」に制限（ここがRDP落ち防止の肝）
    # デフォルトだと全コア使おうとして死にます
    my_env["OMP_NUM_THREADS"] = "2"
    my_env["MKL_NUM_THREADS"] = "2" 
    my_env["TORCH_NUM_THREADS"] = "2"
    my_env["OPENBLAS_NUM_THREADS"] = "2"
    my_env["VECLIB_MAXIMUM_THREADS"] = "2"
    my_env["NUMEXPR_NUM_THREADS"] = "2"

    # コマンド構築
    command = [
        "marker_single",
        str(pdf_path),
        "--output_dir", str(output_dir)
    ]

    print(f"Running SAFE MODE (Threads=2)...")
    print("変換速度は遅いですが、PCは落ちないはずです。気長にお待ちください。")
    
    try:
        # タイムアウトを設定（例えば10分）。無限フリーズ防止。
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore',
            env=my_env,
            timeout=600 
        )
        print("Success! 変換完了")
        
        # 成果物の確認
        if output_dir.exists():
            files = list(output_dir.glob("**/*.md"))
            if files:
                print(f"Markdown生成成功: {files[0]}")
            else:
                print("フォルダはできましたがmdファイルがありません。")
        else:
            print("出力フォルダが見つかりません。")

    except subprocess.TimeoutExpired:
        print("Error: タイムアウトしました（処理が重すぎます）。")
    except subprocess.CalledProcessError as e:
        print(f"Error: 変換失敗 (Exit Code: {e.returncode})")
        print("--- Error Output ---")
        print(e.stderr)

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    convert_pdf_safe_mode(INPUT_PDF_PATH, OUTPUT_DIR)