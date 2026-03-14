# 🎨 Kurodot AI: Multi-Agent Curatorial Orchestrator

A next-generation multi-agent AI curation system built on **Gemini 1.5 Pro** and the **Google GenAI SDK**. Five specialized AI agents collaborate as a professional studio team — Project Manager, VI Designer, Editor, Data Analyst, and Tech Producer — to transform raw exhibition data and URLs into polished, export-ready curatorial assets in real time.

Built for the **Gemini Live Agent Challenge** · Category: **Creative Storyteller** ✍️

---

## 🚀 Quick Start (Local)

### Prerequisites

- Python 3.10+
- A [Google AI Studio](https://aistudio.google.com/) API key with access to `gemini-1.5-pro` and `gemini-2.0-flash-preview-image-generation`
- (Optional) A Google Cloud project with Cloud Storage enabled for export uploads

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/kurodot-agent.git
cd kurodot-agent
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file in the project root (never commit this):

```dotenv
GEMINI_API_KEY=your_google_ai_studio_api_key_here
GCS_BUCKET_NAME=your_gcs_bucket_name          # optional, for Tech Producer uploads
UMAMI_API_URL=https://api.umami.is/v1         # optional, for Analyst live traffic
UMAMI_TOKEN=your_umami_token                  # optional
```

Or export them directly:

```bash
export GEMINI_API_KEY="your_key_here"
```

### 4. Run the backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Open the UI

Navigate to [http://localhost:8000](http://localhost:8000) in your browser.

The canvas loads automatically. Drop an exhibition URL (e.g. `https://app.kurodot.io/exhibition/bauhaus-blueprint-qevdv`) onto a sticky note to start the curation pipeline.

---

## ☁️ Deploy to Google Cloud Run

Requires [`gcloud` CLI](https://cloud.google.com/sdk/docs/install) authenticated and a GCP project configured.

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
export GEMINI_API_KEY="your_key_here"
export GCS_BUCKET_NAME="your_bucket"
chmod +x deploy.sh && ./deploy.sh
```

`deploy.sh` runs `gcloud builds submit` + `gcloud run deploy` in one step. The live service URL is printed on completion.

---

## 🧪 Test the Creative Storyteller Endpoint

Once the server is running, trigger the **interleaved text + image generation** (the Creative Storyteller mandatory feature):

```bash
curl -s -X POST http://localhost:8000/api/interleaved-story \
  -H "Content-Type: application/json" \
  -d '{"exhibition_info": {"title": "Bauhaus Blueprint", "artist": "Keng Fu Chu", "venue": "Kurodot"}}' \
  | python3 -m json.tool
```

Returns `text_parts` (curatorial narrative) and `image_data` (base64 PNG key visual) in a single Gemini response.

---

## 🏗️ System Architecture

```
User (Chief Curator)
        │  sticky note / URL
        ▼
┌─────────────────────────────────┐
│   opencanvas.html  (Frontend)   │
│   Canvas · Sticky Notes · UI    │
└────────────┬────────────────────┘
             │ REST (FastAPI)
             ▼
┌─────────────────────────────────────────────────────┐
│                  main.py  (FastAPI)                  │
│  /api/start_curation   /api/interleaved-story        │
│  /api/pm/session       /api/job/{id}                 │
└───┬──────────┬────────────┬─────────────┬────────────┘
    │          │            │             │
    ▼          ▼            ▼             ▼
 PM Agent   VI Designer  Editor       Analyst / Tech
 (orchestr)  (Gemini     (Gemini      (Umami API /
             GenAI SDK   GenAI SDK     GCS upload)
             interleaved  generate)
             text+image)
                │                          │
                ▼                          ▼
        ┌───────────────┐        ┌─────────────────┐
        │  Google Cloud │        │  Google Cloud   │
        │  Run (backend)│        │  Storage (assets)│
        └───────────────┘        └─────────────────┘
                │
        AgentCollaborationHub
        (utils/logger.py)
        PM dispatch sessions,
        dedup logs, celebration
```

---

## 🤖 Agent Roster

| Color | Agent | Role | Gemini Feature Used |
|-------|-------|------|---------------------|
| 🟠 `#f1a456` | Project Manager | Orchestrates, dispatches, celebrates | PM session tracking |
| 🔴 `#ce538a` | VI Designer | Layout, dark mode, ratio, key visual | **Interleaved text + image output** |
| 🩵 `#6bcdcf` | Editor | Bilingual narrative, translation | `gemini-1.5-pro` generate |
| 🔵 `#5062c8` | Data Analyst | Traffic insights, recommendations | Umami API + Hub |
| ⚫ `#272a3a` | Tech Producer | Export JPG/PNG/PDF, GCS upload | `google-cloud-storage` |

---

## 🌟 Technical Highlights

* **Google GenAI SDK** — all Gemini calls use `google-genai` (not the legacy `google-generativeai`)
* **Creative Storyteller** — `POST /api/interleaved-story` uses `gemini-2.0-flash-preview-image-generation` with `response_modalities=["TEXT","IMAGE"]` to produce a mixed narrative + key visual in a single response stream
* **Prompt Sharding** — each agent has strict boundary constraints; Editor cannot change design, Designer cannot change text
* **PM Dispatch Sessions** — logger.py tracks which agents were dispatched per task; PM celebrates with floating emoji when all complete
* **Cloud Run ready** — `Dockerfile` + `deploy.sh` IaC for one-command deployment

---

## 📁 Project Structure

```
kurodot-agent/
├── main.py                  # FastAPI backend + all API routes
├── opencanvas.html          # Single-file frontend SPA
├── settings.py              # Agent roles, test config
├── requirements.txt
├── Dockerfile               # Cloud Run container
├── deploy.sh                # Cloud Run deploy script (IaC)
├── agents/
│   ├── project_manager.py   # PM: orchestration, URL parsing
│   ├── vi_designer.py       # VI: layout, interleaved Gemini output
│   ├── editor.py            # Editorial: bilingual narrative
│   ├── analyst.py           # Data: Umami traffic + recommendations
│   └── tech_producer.py     # Tech: export packaging, GCS upload
└── utils/
    └── logger.py            # AgentCollaborationHub: dedup, PM sessions
```

---

開發指令!!!!!重要, 絕對遵守
所有角色的agent的功能只寫在自己的.py檔裡面, 不能開新檔案
designer要確保所有文字顯示正常, 不能超出外匡, 有正確的padding,
editor只能改文字不能改design
pm要可以分派任務
tech要可以輸出不同格式檔案 jpg,png,pdf, svg
每次完成更新告訴我新的版本號碼我可以知道有沒有讀到舊的
ui 全英文
自動檢查不可以出現錯誤, 有就修好(index):762 Uncaught SyntaxError: Unexpected token '}' (at (index):762:9)


整理ui非常簡單,
有sticky note
agent按鈕列
agent狀態列
畫布 在畫面中央