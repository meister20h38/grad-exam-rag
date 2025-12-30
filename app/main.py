from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.chat_service import ChatService
from typing import List, Optional

# ソース情報の定義
class SourceInfo(BaseModel):
    file_name: str
    score: float
    text_preview: str

# レスポンスにソースリストを追加
class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceInfo] = []

# アプリケーションの定義
app = FastAPI(
    title="Grad Exam RAG API",
    description="大学院入試の過去問を学習したAIに対する質問API",
    version="1.0.0"
)

# グローバル変数としてサービスを保持
chat_service = None

@app.on_event("startup")
async def startup_event():
    global chat_service
    print("Initializing Chat Service (Loading Models)...")
    chat_service = ChatService()
    print("Chat Service Ready!")

# リクエスト・レスポンスの定義
class QuestionRequest(BaseModel):
    text: str

class AnswerResponse(BaseModel):
    question: str
    answer: str

@app.post("/api/chat", response_model=AnswerResponse)
def chat_endpoint(request: QuestionRequest):
    """
    質問を受け取り、RAGを使って回答を生成する。
    LLMの推論処理が重いため、同期関数としてスレッドプールで実行させる。
    """
    if not chat_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # AIに聞く
        answer_result = chat_service.ask(request.text)

        # LlamaIndexのResponseオブジェクトを文字列に変換
        answer_text = str(answer_result)

		# ソース情報の抽出
        source_list = []
        if hasattr(answer_result, "source_nodes"):
            for node in answer_result.source_nodes:
                source_list.append(SourceInfo(
                    file_name=node.metadata.get("file_name", "Unknown"),
                    score=node.score if node.score else 0.0,
                    text_preview=node.text[:100]
                ))

        return AnswerResponse(
            question=request.text, 
            answer=answer_text,
            sources=source_list
        )

    except Exception as e:
        print(f"Server Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    """
    ヘルスチェック用エンドポイント
    """
    return {"status": "ok", "message": "Go to /docs to use Swagger UI"}

if __name__ == "__main__":
    import uvicorn
    
    # 開発用サーバーの起動
    # アクセスを意識してhost="0.0.0.0" にしておく
    print("Starting FastAPI Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
