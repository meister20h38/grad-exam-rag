from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

client = TestClient(app)

def test_read_root():
    """ルートパスのテスト（404 or 200）"""
    response = client.get("/")
    assert response.status_code in [200, 404]

@patch("app.main.chat_service")
def test_chat_endpoint(mock_chat_service):
    """チャットエンドポイントの正常系テスト"""
    
    # 1. AIからの返答全体をMock化
    mock_response = MagicMock()
    mock_response.__str__.return_value = "これはテストの回答です。"

    # 2. ソースノード(参照元)のMockを作成
    mock_node_item = MagicMock()
    
    # テスト用の本物のデータ（辞書と文字列）を用意
    test_metadata = {"file_name": "test.pdf"}
    test_content = "テスト用ドキュメントの中身..."
    
    # アプリ側が node.metadata にアクセスしても、node.node.metadata にアクセスしても
    # 大丈夫なように、両方に本物のデータをセットしておく
    mock_node_item.metadata = test_metadata
    mock_node_item.get_content.return_value = test_content
    mock_node_item.score = 0.95
    
    mock_node_item.node.metadata = test_metadata
    mock_node_item.node.get_content.return_value = test_content

    # レスポンスにセット
    mock_response.source_nodes = [mock_node_item]
    
    # askメソッドが呼ばれたら、このレスポンスを返す
    mock_chat_service.ask.return_value = mock_response

    # 3. 実際にAPIを叩く
    payload = {"text": "テスト質問"}
    response = client.post("/api/chat", json=payload)

    # 4. 検証（Assert）
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "これはテストの回答です。"
    
    # ソース情報の検証
    assert len(data["sources"]) == 1
    assert data["sources"][0]["file_name"] == "test.pdf"
