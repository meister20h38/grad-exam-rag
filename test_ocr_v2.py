import os
import subprocess
from pathlib import Path

# ==========================================
# 設定
# ==========================================
INPUT_PDF_PATH = "./data/sample_exam.pdf"

def convert_pdf_to_markdown_cpu(pdf_path):
    pdf_path = Path(pdf_path).resolve()
    
    # ---------------------------------------------------------
    # 【重要】 GPUを隠して CPU強制モードにする設定
    # ---------------------------------------------------------
    my_env = os.environ.copy()
    my_env["CUDA_VISIBLE_DEVICES"] = ""  # 空にすることでGPUがない振りをさせる
    my_env["TORCH_DEVICE"] = "cpu"       # 明示的にCPU指定

    # コマンド (シンプル版)
    command = [
        "marker_single",
        str(pdf_path)
    ]

    print(f"Running command on CPU... (安全運転モード)")
    
    try:
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            errors='ignore',
            env=my_env  # ここで環境変数を渡す
        )
        print("Success! 変換完了")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: 変換失敗 (Exit Code: {e.returncode})")
        print(e.stderr)

if __name__ == "__main__":
    convert_pdf_to_markdown_cpu(INPUT_PDF_PATH)