import os
import subprocess
from pathlib import Path

class OCRService:
    def __init__(self, output_base_dir: str = "./output_data"):
        self.output_base_dir = Path(output_base_dir).resolve()
        
    def convert_pdf_to_markdown(self, pdf_path: str) -> str:
        """
        指定されたPDFをMarkdownに変換し、出力されたmdファイルのパスを返す。
        
        Note:
            VRAM枯渇およびCPU負荷によるRDP切断を防ぐため、
            意図的にCPUリソース制限モード（Resource Safe Mode）で実行する。
        """
        pdf_path = Path(pdf_path).resolve()
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDFが見つかりません: {pdf_path}")

        os.makedirs(self.output_base_dir, exist_ok=True)

        # 環境変数の設定 (Resource Safe Mode)
        # マシンリソースを占有しすぎないよう環境変数を制御
        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = ""     # GPU無効化
        env["TORCH_DEVICE"] = "cpu"          # CPU強制
        
        # マルチスレッドによるOSフリーズ防止(RDP維持のため)
        threads = "2"
        env["OMP_NUM_THREADS"] = threads
        env["MKL_NUM_THREADS"] = threads
        env["TORCH_NUM_THREADS"] = threads

        # Markerコマンド構築
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
                timeout=600  # ハングアップ防止のタイムアウト
            )
            
            # 生成物のパス解決
            # markerは output_dir/pdf_filename/pdf_filename.md に出力する仕様
            expected_md = self.output_base_dir / pdf_path.stem / f"{pdf_path.stem}.md"
            if expected_md.exists():
                return str(expected_md)
            else:
                raise FileNotFoundError("変換は完了しましたが、ファイルが見当たりません。")

        except subprocess.TimeoutExpired:
            raise RuntimeError("OCR処理がタイムアウトしました。")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"OCR変換失敗: {e.stderr}")

if __name__ == "__main__":
    import argparse
    import sys

    # 引数設定
    parser = argparse.ArgumentParser(
        description="PDFをMarkdownに変換するツール (Resource Safe Mode)"
    )
    parser.add_argument("pdf_path", help="変換対象のPDFファイルのパス")
    parser.add_argument("--output", default="./output_data", help="出力先ディレクトリ")
    
    args = parser.parse_args()

    # パスチェック
    target_pdf = Path(args.pdf_path)
    if not target_pdf.exists():
        print(f"Error: File not found -> {target_pdf}")
        sys.exit(1)

    # 実行
    try:
        service = OCRService(output_base_dir=args.output)
        result_path = service.convert_pdf_to_markdown(str(target_pdf))
        
        print("-" * 30)
        print("Conversion Successful!")
        print(f"Output MD: {result_path}")
        print("-" * 30)

    except Exception as e:
        print(f"Fatal Error: {e}")
        sys.exit(1)
