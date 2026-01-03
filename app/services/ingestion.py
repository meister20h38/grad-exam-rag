# app/services/ingestion.py

import os
import argparse
from pathlib import Path
import qdrant_client
from llama_index.core import Document, VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import MarkdownNodeParser

class IngestionService:
    """
    Markdown形式の過去問データをベクトル化し、Qdrantデータベースへ格納するサービス。
    """
    def __init__(self):
		# 日本語と専門用語（数式等）に強い 'multilingual-e5-large' を採用
        # VRAM節約のため、推論時はCPUを使用する設定も考慮可能
        self.embed_model = HuggingFaceEmbedding(
            model_name="intfloat/multilingual-e5-large",
            device="cuda"
        )
        
		# グローバル設定: Ingestion処理ではLLMによる生成は不要なためNoneに設定
        Settings.embed_model = self.embed_model
        Settings.llm = None

        self.client = qdrant_client.QdrantClient(
            url="http://localhost:6333",
            timeout=300.0
        )

    def ingest_markdown_file(self, md_path: str, collection_name: str = "grad_exam", extra_metadata: dict = None):
        """
        指定されたMarkdownファイルを読み込み、チャンク分割してインデックスを作成する。

        Args:
            md_path (str): Markdownファイルのパス
            collection_name (str): Qdrantのコレクション名
        """
        file_path = Path(md_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {md_path}")
    
        print(f"Reading file: {file_path.name}")
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # メタデータの作成
        metadata = {"file_name": file_path.name}
        if extra_metadata:
            metadata.update(extra_metadata) # 渡されたメタデータを結合

        # Documentにメタデータをセット
        doc = Document(
            text=text,
            metadata=metadata
        )

	    # 【重要】単純な文字数分割ではなく、Markdownの見出し構造に基づいて分割する
        # これにより、数式や問題文のコンテキスト分断を防ぐ
        parser = MarkdownNodeParser()
        nodes = parser.get_nodes_from_documents([doc])
        print(f"Split into {len(nodes)} chunks.")

        vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            batch_size=32
        )
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        print("Embedding and Indexing...")
        VectorStoreIndex(
            nodes,
            storage_context=storage_context,
        )
        print("Success! Data stored in Qdrant.")

if __name__ == "__main__":
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description="MarkdownファイルをQdrantにIngestするツール")
    parser.add_argument("file_path", help="読み込むMarkdownファイルのパス")
    parser.add_argument("--collection", default="grad_exam", help="Qdrantのコレクション名 (デフォルト: grad_exam)")
    
    args = parser.parse_args()

    # 引数で渡されたパスを使用
    target_file = Path(args.file_path)
    
    if target_file.exists():
        try:
            print(f"Start ingesting: {target_file}")
            service = IngestionService()
            service.ingest_markdown_file(str(target_file), collection_name=args.collection)
            print("Done.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Error: File not found -> {target_file}")
