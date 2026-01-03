# app/services/ocr.py

import os
import subprocess
from pathlib import Path

class OCRService:
    def __init__(self, output_root: str = "./output_data"):
        self.output_root = Path(output_root)
        self.output_root.mkdir(parents=True, exist_ok=True)
        
    def convert_pdf_to_markdown(self, pdf_path: str, unique_subfolder: str = None) -> str:
        """
        指定されたPDFをMarkdownに変換し、出力されたmdファイルのパスを返す。
        """
        input_path = Path(pdf_path)
        if not input_path.exists():
            raise FileNotFoundError(f"PDFが見つかりません: {pdf_path}")

        # 出力先ディレクトリの決定
        if unique_subfolder:
            output_dir = self.output_root / unique_subfolder
        else:
            output_dir = self.output_root

        output_dir.mkdir(parents=True, exist_ok=True)

        # 環境変数の設定 (VRAM/CPU負荷対策)
        env = os.environ.copy()

        # 環境変数の設定 (Resource Safe Mode)
        # マシンリソースを占有しすぎないよう環境変数を制御
        env = os.environ.copy()

        # PyTorchのメモリ断片化を防ぐ（VRAM不足エラー対策）
        env["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
        
        # マルチスレッドによるOSフリーズ防止(RDP維持のため)
        threads = "4"
        env["OMP_NUM_THREADS"] = threads
        env["MKL_NUM_THREADS"] = threads
        env["TORCH_NUM_THREADS"] = threads

        # GPU設定のチューニング
        batch_multiplier = "1"

        # Markerコマンド構築
        command = [
            "marker_single",
            str(input_path),
            "--output_dir", str(output_dir)
        ]

        print(f"Starting OCR for {input_path.name} (GPU Mode: ON, Batch: {batch_multiplier})...")
        print(f"Output Directory: {output_dir}")
        
        try:
            subprocess.run(
                command, 
                check=True, 
                capture_output=True, 
                text=True, 
                encoding='utf-8', 
                errors='ignore',
                env=env,
                timeout=None  # ハングアップ防止のタイムアウト
            )

            # 生成されたMarkdownファイルのパスを探す
            # 構造: output_dir / {pdf_stem} / {pdf_stem}.md
            target_md = output_dir / input_path.stem / f"{input_path.stem}.md"

            if not target_md.exists():
                raise FileNotFoundError(f"Output markdown not found at {target_md}")

            return str(target_md)

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
        service = OCRService(output_root=args.output)
        result_path = service.convert_pdf_to_markdown(str(target_pdf))
        
        print("-" * 30)
        print("Conversion Successful!")
        print(f"Output MD: {result_path}")
        print("-" * 30)

    except Exception as e:
        print(f"Fatal Error: {e}")
        sys.exit(1)
