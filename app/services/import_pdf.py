# app/services/import_pdf.py 

import sys
import os
from pathlib import Path
from app.services.ocr import OCRService
from app.services.ingestion import IngestionService

def import_pipeline(pdf_path_str: str):
    pdf_path = Path(pdf_path_str).resolve()
    if not pdf_path.exists():
        print(f"Error: ファイルが見つかりません -> {pdf_path}")
        return

    # フォルダ階層からメタデータを推測する
    # 期待する構造: data/{university}/{year}/{filename}.pdf
    # 例: data/(大学名)/2023/hissu.pdf
    try:
        parts = pdf_path.parts
        # 後ろから数えて、ファイル名(-1), 年度(-2), 大学(-3) を取得
        year = parts[-2]
        university = parts[-3]
        
        # ファイル名から「区分」をざっくり推測
        filename = pdf_path.stem # 拡張子なしファイル名
        exam_type = "general"
        if "hissu" in filename or "common" in filename:
            exam_type = "compulsory" # 必須
        elif "sentaku" in filename or "select" in filename:
            exam_type = "elective"   # 選択
        
        metadata = {
            "university": university,
            "year": year,
            "type": exam_type
        }
        print(f"抽出されたメタデータ: {metadata}")

    except Exception:
        print("警告: フォルダ構成が data/{uni}/{year}/.. ではありません。メタデータは空になります。")
        metadata = {}

    unique_id = "unknown"
    if metadata:
        unique_id = f"{metadata.get('university', 'univ')}_{metadata.get('year', 'year')}"

    print(f"=== 1. OCR開始: {pdf_path.name} ===")
    ocr_service = OCRService()
    try:
        md_file_path = ocr_service.convert_pdf_to_markdown(str(pdf_path), unique_subfolder=unique_id)
        print(f"OCR完了: {md_file_path}")
    except Exception as e:
        print(f"OCR失敗: {e}")
        return

    print(f"\n=== 2. ベクトルDB格納開始 (メタデータ付き) ===")
    ingestion_service = IngestionService()
    try:
        # メタデータを渡す！
        ingestion_service.ingest_markdown_file(md_file_path, extra_metadata=metadata)
        print("DB格納完了！")
    except Exception as e:
        print(f"DB格納失敗: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.services.import_pdf [PDF_PATH]")
    else:
        import_pipeline(sys.argv[1])
