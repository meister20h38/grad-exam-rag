# tests/test_main.py
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

# クライアントの作成
client = TestClient(app)

class MockNode:
    def __init__(self):
        self.metadata = {"file_name": "test.pdf"}
    
    def get_content(self):
        return "テスト用ドキュメントの中身がここに入ります..."

def test_read_root():
    """ヘルスチェック的なテスト"""
    # エンドポイントがないので、404になるのが正常か、
    # あるいはGET / があるなら200を確認する
    response = client.get("/")
    assert response.status_code in [200, 404]

@patch("app.main.chat_service") # main.pyの中のchat_serviceをモック化
def test_chat_endpoint(mock_chat_service):
    """チャットエンドポイントの正常系テスト"""
    
    # 1. AIからの返答を偽装（Mock）する
    mock_response = MagicMock()
    mock_response.__str__.return_value = "これはテストの回答です。"
    # ソースノードの情報も偽装
    fake_node = MockNode()
    
    mock_node_with_score = MagicMock()
    mock_node_with_score.node = fake_node
    mock_node_with_score.score = 0.95
    
    mock_response.source_nodes = [mock_node_with_score]
    
    # askメソッドが呼ばれたら、この偽装レスポンスを返すように設定
    mock_chat_service.ask.return_value = mock_response

    # 2. 実際にAPIを叩く
    payload = {"text": "テスト質問"}
    response = client.post("/api/chat", json=payload)

    # 3. 検証（Assert）
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "これはテストの回答です。"
    assert len(data["sources"]) == 1
    assert data["sources"][0]["file_name"] == "test.pdf"
    assert "テスト用ドキュメント" in data["sources"][0]["text_preview"]
