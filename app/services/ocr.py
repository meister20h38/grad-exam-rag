import os
import subprocess
from pathlib import Path

class OCRService:
    def __init__(self, output_base_dir: str = "./output_data"):
        self.output_base_dir = Path(output_base_dir).resolve()
        
    def convert_pdf_to_markdown(self, pdf_path: str) -> str:
        """
        指定されたPDFをMarkdownに変換し、出力されたmdファイルのパスを返す。
        RDP落ち防止のため、CPUリソース制限モードで実行する。
        """
        pdf_path = Path(pdf_path).resolve()
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDFが見つかりません: {pdf_path}")

        # 出力ディレクトリの準備
        os.makedirs(self.output_base_dir, exist_ok=True)

        # 環境変数の設定 (Resource Safe Mode)
        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = ""     # GPU無効化
        env["TORCH_DEVICE"] = "cpu"          # CPU強制
        # スレッド制限 (RDP維持のため)
        threads = "2"
        env["OMP_NUM_THREADS"] = threads
        env["MKL_NUM_THREADS"] = threads
        env["TORCH_NUM_THREADS"] = threads

        # コマンド構築
        # output_dirを指定すると、その中にサブフォルダが作られる仕様に対応
        command = [
            "marker_single",
            str(pdf_path),
            "--output_dir", str(self.output_base_dir)
        ]

        print(f"Starting OCR for {pdf_path.name} (Safe Mode)...")
        
        try:
            subprocess.run(
                command, 
                check=True, 
                capture_output=True, 
                text=True, 
                encoding='utf-8', 
                errors='ignore',
                env=env,
                timeout=600  # 10分タイムアウト
            )
            
            # 生成されたファイルのパスを特定して返す
            # markerは output_dir/pdf_filename/pdf_filename.md を作る
            expected_md = self.output_base_dir / pdf_path.stem / f"{pdf_path.stem}.md"
            if expected_md.exists():
                return str(expected_md)
            else:
                raise FileNotFoundError("変換は完了しましたが、ファイルが見当たりません。")

        except subprocess.TimeoutExpired:
            raise RuntimeError("OCR処理がタイムアウトしました。")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"OCR変換失敗: {e.stderr}")

# テスト実行用 ( python -m app.services.ocr で動く)
if __name__ == "__main__":
    service = OCRService(output_base_dir="./output_test")
    # dataフォルダがある前提
    try:
        result = service.convert_pdf_to_markdown("./data/sample_exam.pdf")
        print(f"Success! Output: {result}")
    except Exception as e:
        print(f"Error: {e}")
