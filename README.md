# Grad-Exam-Hack (WIP)

大学院入試（情報系）の過去問対策を効率化するための、ローカル完結型RAG（Retrieval-Augmented Generation）システム。

## 特徴

* **数式対応OCR:** * 一般的なOCRでは崩れてしまう数学・物理の数式（LaTeX形式）を、`marker-pdf` を用いて高精度にMarkdown化。
* **ローカルLLM推論:**
  * 機密性の高い過去問データを外部に出さず、ローカルGPU環境（RTX 3060）で安全に処理。
* **リソース最適化:**
  * VRAM 12GBの制約下で安定動作させるため、OCR処理と推論処理のリソース管理（CPU/GPUオフロード）を厳密に制御。

## 技術スタック

* **Language:** Python 3.10+
* **OCR:** Marker (with PyTorch)
* **LLM:** Ollama (Qwen 2.5)
* **Vector DB:** Qdrant
* **Backend:** FastAPI (Planned)

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run OCR Test (Safe Mode)
python -m app.services.ocr
