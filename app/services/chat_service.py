import qdrant_client
from llama_index.core import VectorStoreIndex, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

class ChatService:
    """
    Qdrantに保存された過去問データを検索し、Ollama(LLM)を用いて回答を生成するサービスクラス。
    """
    def __init__(self):
        self.llm = Ollama(
			model="qwen2.5:14b",
			request_timeout=1200.0,
			system_prompt="""
                    あなたは大学院入試の過去問分析官です。
                    ユーザーの質問に対し、提供されたコンテキスト（過去問データ）に基づいて回答してください。
                                    
                    【重要なルール】
                    1. 必ず「〇〇年の第X問では～」のように、具体的な年度と問題番号を引用すること。
                    2. 「基本的概念」のような抽象的な言葉は使わず、「固有値」「ポアソン分布」「線形写像の核」のような具体的な数学用語・キーワードを列挙すること。
                    3. 曖昧な要約はせず、事実を箇条書きで提示すること。
                    """
        )

        self.embed_model = HuggingFaceEmbedding(
            model_name="intfloat/multilingual-e5-large",
            device="cpu"
        )
        
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model

        client = qdrant_client.QdrantClient(url="http://localhost:6333")
        vector_store = QdrantVectorStore(
            client=client, 
            collection_name="grad_exam"
        )
        
        self.index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    def ask(self, question: str):
        """
        質問文を受け取り、RAG（検索＋生成）を実行して回答を返す。
        """
        query_engine = self.index.as_query_engine(
            similarity_top_k=10,
        )
        
        print(f"\nThinking... (Question: {question})")
        response = query_engine.query(question)
        return response

if __name__ == "__main__":
    import sys
    
    print("Initializing Chat Service... (This may take time due to model loading)")
    try:
        service = ChatService()
        print("\n" + "="*50)
        print("  AI Tutor Chat Debugger (Type 'exit' to quit)")
        print("="*50 + "\n")

        while True:
            # ユーザー入力を待機
            user_input = input("\nUser > ")
            
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Bye!")
                break
            
            if not user_input.strip():
                continue

            # 回答の生成
            response = service.ask(user_input)

            # 回答の表示
            print(f"\nAI > {str(response)}")
            
            # 【重要】RAGが参照したソース情報の表示
            # 「ハルシネーション」か「事実に基づく回答」かの判断に必要
            print("\n" + "-"*20 + " Source Documents " + "-"*20)
            for i, node in enumerate(response.source_nodes, 1):
                # メタデータ（ファイル名など）と本文の抜粋を表示
                file_name = node.metadata.get('file_name', 'Unknown')
                score = node.score if node.score else 0.0
                content_preview = node.text[:100].replace('\n', ' ') + "..."
                
                print(f"[{i}] {file_name} (Score: {score:.4f})")
                print(f"    Content: {content_preview}")
            print("-"*58)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
