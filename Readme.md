# 🎨 Kurodot AI: Multi-Agent Curatorial Orchestrator

A next-generation multi-agent AI curation system built on **Google GenAI SDK** and **Gemini 2.x** models. Five specialized AI agents collaborate as a professional studio team — Project Manager, VI Designer, Editor, Data Analyst, and Tech Producer — to transform raw exhibition data and URLs into polished, export-ready curatorial assets in real time.

Built for the **Gemini Live Agent Challenge** · Category: **Creative Storyteller** ✍️

> **Live demo:** `https://kurodot-agent-1063202705342.us-central1.run.app`

---

## 🔧 Technology Stack

### Google / GCP (Mandatory)

| Technology | Version / Model | Usage |
|---|---|---|
| **Google GenAI SDK** | `google-genai` | All Gemini API calls (migrated from legacy `google-generativeai`) |
| **Gemini 2.5 Flash Image** | `gemini-2.5-flash-image` | **Creative Storyteller** — interleaved text + image generation in one response |
| **Gemini 2.0 Flash 001** | `gemini-2.0-flash-001` | Translation endpoint, bilingual narrative, editorial generation |
| **Google Cloud Run** | Managed (us-central1) | Serverless backend hosting |
| **Google Cloud Build** | — | CI/CD container image build from `gcloud builds submit` |
| **Google Container Registry** | `gcr.io/gen-lang-client-0803878197/kurodot-agent` | Docker image storage |
| **Google Cloud Storage** | `google-cloud-storage` SDK | Tech Producer export uploads (JPG/PNG/PDF) |

### Backend

| Technology | Version | Usage |
|---|---|---|
| **Python** | 3.11 (container), 3.9 (local) | Runtime |
| **FastAPI** | latest | REST API server, all agent endpoints |
| **Uvicorn** | `uvicorn[standard]` | ASGI server (`Procfile` + `Dockerfile`) |
| **python-dotenv** | latest | `.env` loading for local dev |

### Frontend

| Technology | Usage |
|---|---|
| **Vanilla JS / HTML5 Canvas** | Single-file SPA (`opencanvas.html`) — no framework |
| **Lucide Icons** | SVG icon set, serialized to base64 for export |
| **CSS3 Animations** | Agent state transitions, PM celebration particles |
| **DOM `html2canvas`** | Banner canvas-to-image export for download |

### Infrastructure & Dev

| Technology | Usage |
|---|---|
| **Docker** | `Dockerfile` for Cloud Run container |
| **`deploy.sh`** | IaC — `gcloud builds submit` + Cloud Run deploy in one command |
| **Firebase Admin / Pyrebase4** | Exhibition data reads from Firestore |
| **Umami Analytics API** | Analyst agent live traffic insight queries |

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         USER (Chief Curator)                         │
│              Drops exhibition URL · Types sticky note                │
└──────────────────────────┬───────────────────────────────────────────┘
                           │  HTTP (browser, same origin)
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│              opencanvas.html  ·  Single-File SPA Frontend            │
│                                                                      │
│  ┌─────────────┐  ┌─────────────────┐  ┌──────────────────────────┐ │
│  │ Sticky Notes│  │  Agent Status   │  │  Banner Canvas (artboard)│ │
│  │  (input)    │  │  Bar (5 dots)   │  │  headline/subtext/img    │ │
│  └──────┬──────┘  └────────┬────────┘  └──────────────────────────┘ │
│         │                  │                                         │
│         └──────────────────▼                                         │
│              triggerRevision() · processTask() · openPMSession()     │
└──────────────────────────┬───────────────────────────────────────────┘
                           │  REST API (FastAPI)
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     main.py  ·  FastAPI Backend                      │
│                                                                      │
│  POST /api/start_curation          GET /api/job/{id}                 │
│  POST /api/interleaved-story       POST /api/translate               │
│  POST /api/pm/session              POST /api/pm/session/{id}/done    │
└───┬────────────┬─────────────┬────────────┬────────────┬─────────────┘
    │            │             │            │            │
    ▼            ▼             ▼            ▼            ▼
┌───────┐  ┌─────────┐  ┌──────────┐  ┌────────┐  ┌──────────────┐
│  PM   │  │  VI     │  │ Editor   │  │Analyst │  │    Tech      │
│ Agent │  │Designer │  │  Agent   │  │ Agent  │  │  Producer    │
│       │  │         │  │          │  │        │  │              │
│Orches-│  │Gemini   │  │Gemini    │  │Umami   │  │Export JPG/   │
│trates │  │2.5-flash│  │2.0-flash │  │API +   │  │PNG/PDF/SVG   │
│5 agent│  │-image   │  │-001      │  │Hub     │  │Google Cloud  │
│PM     │  │Interlea-│  │Bilingual │  │Recom-  │  │Storage upload│
│session│  │ved text │  │narrative │  │menda-  │  │              │
│tracker│  │+ image  │  │+ /api/   │  │tions   │  │              │
│       │  │output   │  │translate │  │        │  │              │
└───┬───┘  └────┬────┘  └────┬─────┘  └───┬────┘  └──────┬───────┘
    │           │            │             │              │
    └───────────┴────────────┴─────────────┴──────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────┐
│              utils/logger.py  ·  AgentCollaborationHub               │
│                                                                      │
│  emit_log()  ·  open_pm_session()  ·  close_agent_task()            │
│  In-memory dedup (O(1))  ·  PM dispatch session tracking             │
│  Triggers PM celebration when all_done = true                        │
└──────────────────────────────────────────────────────────────────────┘
                             │
              ┌──────────────┼─────────────────┐
              ▼              ▼                 ▼
       ┌────────────┐  ┌──────────────┐  ┌─────────────────┐
       │  Gemini    │  │  Firestore   │  │  Google Cloud   │
       │  API       │  │  (Firebase)  │  │  Storage        │
       │ (GenAI SDK)│  │ Exhibition   │  │  Export assets  │
       └────────────┘  │   data       │  └─────────────────┘
                       └──────────────┘
```

---

## 🤖 Agent Roster

| Color | Agent | Role | Gemini Model Used |
|-------|-------|------|-------------------|
| 🟠 `#f1a456` | Project Manager | Orchestrates all agents, PM session tracking, PM celebration | Hub only (no direct Gemini call) |
| 🔴 `#ce538a` | VI Designer | Layout, dark mode, aspect ratio, **interleaved text+image** | `gemini-2.5-flash-image` |
| 🩵 `#6bcdcf` | Editor | Bilingual narrative, **real-time translation** via `/api/translate` | `gemini-2.0-flash-001` |
| 🔵 `#5062c8` | Data Analyst | Traffic insights from Umami API, proactive recommendations | External API + Hub |
| ⚫ `#272a3a` | Tech Producer | Export JPG/PNG/PDF/SVG, Google Cloud Storage upload | `google-cloud-storage` SDK |

---

## ✨ Creative Storyteller — Mandatory Tech

The hackathon's **Creative Storyteller** category requires interleaved multimodal output (text + image in a single generative response).

**Endpoint:** `POST /api/interleaved-story`

```bash
curl -s -X POST https://kurodot-agent-1063202705342.us-central1.run.app/api/interleaved-story \
  -H "Content-Type: application/json" \
  -d '{"exhibition_info": "Bauhaus Blueprint: geometric forms, primary colours, industrial design"}'
```

**Returns:**
```json
{
  "text_parts": ["Welcome to Bauhaus Blueprint... (curatorial narrative)"],
  "image_data": ["<base64 PNG key visual>"]
}
```

- Uses `gemini-2.5-flash-image` with `response_modalities=["TEXT", "IMAGE"]`
- Text and image are generated in a **single API call**, not separate requests
- Image data is base64-encoded PNG, ready for `<img src="data:image/png;base64,...">` embed

---

## 🚀 Quick Start (Local)

### Prerequisites

- Python 3.10+
- A [Google AI Studio](https://aistudio.google.com/) API key
- (Optional) GCP project with Cloud Storage for export uploads

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/kurodot-agent.git
cd kurodot-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set environment variables

```bash
export GEMINI_API_KEY="your_key_here"
export GCS_BUCKET_NAME="your_bucket"   # optional
```

### 3. Run

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open [http://localhost:8000](http://localhost:8000).

---

## ☁️ Deploy to Google Cloud Run

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
export GEMINI_API_KEY="your_key_here"
export GCS_BUCKET_NAME="your_bucket"
chmod +x deploy.sh && ./deploy.sh
```

---

## 📁 Project Structure

```
kurodot-agent/
├── main.py                  # FastAPI backend + all API routes
├── opencanvas.html          # Single-file frontend SPA
├── settings.py              # Agent roles, test config
├── requirements.txt
├── Dockerfile               # Cloud Run container (Python 3.11-slim)
├── deploy.sh                # IaC: gcloud builds + run deploy
├── agents/
│   ├── project_manager.py   # PM: orchestration, URL parsing, session
│   ├── vi_designer.py       # VI: layout, interleaved Gemini output
│   ├── editor.py            # Editorial: bilingual narrative, translation
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

export PATH="$HOME/google-cloud-sdk/bin:$PATH"
gcloud auth login## 🌟 Technical Highlights

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