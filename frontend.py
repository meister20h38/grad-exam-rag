"""
Frontend Application for Grad Exam RAG System
Streamlitを使用したチャットインターフェース。
FastAPIサーバーと通信し、ユーザーの質問に対する回答と参照ドキュメントを表示します。
"""

import streamlit as st
import requests

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/api/chat"
PAGE_TITLE = "院試対策AIチューター"
PAGE_ICON = "🎓"

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)
st.title(f"{PAGE_ICON} {PAGE_TITLE}")

# CSSによるスタイル調整（参照元の見た目を整える）
st.markdown("""
<style>
    .stExpander { border: 1px solid #ddd; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# --- Session State Management ---
# チャット履歴を保持（リロードしても会話が消えないようにする）
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去の会話履歴を画面に描画
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Logic ---
# ユーザーの入力待機
if prompt := st.chat_input("質問を入力してください（例：線形代数の傾向は？）"):
    
    # 1. ユーザーの入力を表示＆保存
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. APIと通信して回答を生成
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"text": prompt},
                    timeout=300  # タイムアウト設定（秒）
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "")
                    sources = data.get("sources", [])

                    # 回答の表示
                    st.markdown(answer)

                    # 参照ドキュメントがある場合はアコーディオンで表示
                    if sources:
                        with st.expander("📚 参照したドキュメント"):
                            for i, src in enumerate(sources, 1):
                                score = src.get('score', 0)
                                file_name = src.get('file_name', 'Unknown')
                                text = src.get('text_preview', 'No content')
                                
                                st.markdown(f"**{i}. {file_name}** (Score: {score:.3f})")
                                st.caption(f"{text}...")
                                # 区切り線（最後以外）
                                if i < len(sources):
                                    st.markdown("---")

                    # アシスタントの回答を履歴に保存
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("通信エラー: バックエンドサーバー(FastAPI)が起動していない可能性があります。")
            except Exception as e:
                st.error(f"予期せぬエラーが発生しました: {e}")
