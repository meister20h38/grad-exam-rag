import os
import subprocess
from pathlib import Path

# ==========================================
# 設定
# ==========================================
INPUT_PDF_PATH = "./data/sample_exam.pdf"  # テストしたい過去問のパス
OUTPUT_DIR = "./output_test"               # 結果の保存先

def convert_pdf_to_markdown(pdf_path, output_dir):
    """
    MarkerのCLIコマンドを叩いてPDFをMarkdownに変換するラッパー関数
    """
    pdf_path = Path(pdf_path).resolve()
    output_dir = Path(output_dir).resolve()

    if not pdf_path.exists():
        print(f"Error: ファイルが見つかりません: {pdf_path}")
        return

    # コマンドの構築
    # marker_single [PDFパス] [出力先フォルダ] --batch_multiplier 2 --max_pages 5
    # --langs Japanese を指定すると日本語精度が上がることがあるが、デフォルトでも結構いける
    command = [
        "marker_single",
        str(pdf_path),
        str(output_dir),
    ]

    print(f"Converting {pdf_path.name}...")
    try:
        subprocess.run(command, check=True)
        print("Success! 変換完了")
        print(f"確認してください: {output_dir}/{pdf_path.stem}/{pdf_path.stem}.md")
    except subprocess.CalledProcessError as e:
        print(f"Error: 変換に失敗しました。 {e}")

if __name__ == "__main__":
    # ディレクトリがなければ作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 実行
    convert_pdf_to_markdown(INPUT_PDF_PATH, OUTPUT_DIR)