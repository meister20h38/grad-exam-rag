# batch_import.py
from pathlib import Path
from app.services.import_pdf import import_pipeline

# PDFが入っているフォルダ
DATA_DIR = Path("./data")

def main():
    # dataフォルダ以下のすべての .pdf ファイルを再帰的に探す
    pdf_files = list(DATA_DIR.rglob("*.pdf"))
    
    if not pdf_files:
        print("PDFファイルが見つかりません。dataフォルダを確認してください。")
        return

    print(f"=== {len(pdf_files)} 個のPDFファイルが見つかりました。処理を開始します... ===")

    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file}")
        try:
            # 既存のパイプラインを呼び出す
            import_pipeline(str(pdf_file))
        except Exception as e:
            print(f"Error importing {pdf_file.name}: {e}")
            # エラーが出ても止まらず次へ行く
            continue
    
    print("\n=== 全ての処理が完了しました！ ===")

if __name__ == "__main__":
    main()
