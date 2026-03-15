# 🎨 Kurodot AI: Multi-Agent Curatorial Orchestrator

Five specialized AI agents collaborate as a professional studio team to transform exhibition URLs into polished, export-ready curatorial banners in real time.

Built for the **Gemini Live Agent Challenge** · Category: **Creative Storyteller** ✍️

> **Live demo:** https://kurodot-agent-1063202705342.us-central1.run.app

> 🏆 **Bonus — Infrastructure as Code:** All GCP resources (Cloud Run, IAM, GCS) are fully defined in Terraform (`infra/`). A GitHub Actions workflow (`.github/workflows/deploy.yml`) automates build → push → deploy on every push to `main`. See [Infrastructure as Code](#️-infrastructure-as-code-terraform) for details.

---

## 🤖 Agent Roster

| Color | Agent | Role | Gemini Model |
|-------|-------|------|--------------|
| 🟠 `#f1a456` | Project Manager | Orchestrates all agents, session tracking, celebration | Hub only |
| 🔴 `#ce538a` | VI Designer | Layout, dark mode, aspect ratio, interleaved text + image | `gemini-2.5-flash-image` |
| 🩵 `#6bcdcf` | Editor | Bilingual narrative, real-time translation | `gemini-2.0-flash-001` |
| 🔵 `#5062c8` | Data Analyst | Traffic insights from Umami API, recommendations | External API + Hub |
| ⚫ `#272a3a` | Tech Producer | Export JPG/PNG/PDF/SVG, Google Cloud Storage upload | `google-cloud-storage` SDK |

---

## 🔧 Technology Stack

### Google / GCP

| Technology | Usage |
|---|---|
| **Google GenAI SDK** (`google-genai`) | All Gemini API calls |
| **Gemini 2.5 Flash Image** | Creative Storyteller — interleaved text + image in one response |
| **Gemini 2.0 Flash 001** | Editorial generation, bilingual narrative, translation |
| **Google Cloud Run** (us-central1) | Serverless backend hosting |
| **Google Cloud Build** | Container image build via `gcloud builds submit` |
| **Google Container Registry** | Docker image storage |
| **Google Cloud Storage** | Tech Producer export uploads |

### Backend & Frontend

| Technology | Usage |
|---|---|
| Python 3.11 (container) / 3.9 (local) | Runtime |
| FastAPI + Uvicorn | REST API server |
| Vanilla JS / HTML5 Canvas | Single-file SPA (`opencanvas.html`) — no framework |
| Firebase Admin / Pyrebase4 | Exhibition data from Firestore |
| Umami Analytics API | Analyst agent live traffic queries |

---

## 🏗️ System Architecture

```
User (Chief Curator)
  │  drops exhibition URL · types sticky note
  ▼
opencanvas.html  (Single-File SPA)
  Sticky Notes · Agent Status Bar · Banner Canvas
  triggerRevision() · processTask() · openPMSession()
  │  REST API
  ▼
main.py  (FastAPI)
  POST /api/start_curation      GET /api/job/{id}
  POST /api/interleaved-story   POST /api/translate
  POST /api/pm/session          POST /api/pm/session/{id}/done
  │
  ├── PM Agent       → orchestrates, session tracking
  ├── VI Designer    → Gemini 2.5-flash-image, interleaved text+image
  ├── Editor         → Gemini 2.0-flash-001, bilingual narrative
  ├── Analyst        → Umami API, recommendations
  └── Tech Producer  → export packaging, GCS upload
  │
  ▼
utils/logger.py  (AgentCollaborationHub)
  emit_log() · open_pm_session() · close_agent_task()
  In-memory dedup · PM dispatch tracking · celebration trigger
```

---

## ✨ Creative Storyteller — Interleaved Text + Image

**Endpoint:** `POST /api/interleaved-story`

```bash
curl -s -X POST https://kurodot-agent-1063202705342.us-central1.run.app/api/interleaved-story \
  -H "Content-Type: application/json" \
  -d '{"exhibition_info": "Bauhaus Blueprint: geometric forms, primary colours, industrial design"}'
```

Returns `text_parts` (curatorial narrative) and `image_data` (base64 PNG key visual) in a **single** `gemini-2.5-flash-image` API call using `response_modalities=["TEXT", "IMAGE"]`.

---

## 📁 Project Structure

```
kurodot-agent/
├── main.py                  # FastAPI backend + all API routes
├── opencanvas.html          # Single-file frontend SPA
├── settings.py              # Agent roles, test config
├── requirements.txt
├── Dockerfile               # Cloud Run container (Python 3.11-slim)
├── deploy.sh                # Quick gcloud CLI deploy script
├── infra/                   # Terraform IaC (bonus: Infrastructure as Code)
│   ├── main.tf              # Cloud Run service + IAM + GCS bucket
│   ├── variables.tf         # Input variables
│   ├── outputs.tf           # Service URL output
│   └── terraform.tfvars.example
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

## 🚀 Quick Start (Local)

```bash
git clone https://github.com/YOUR_USERNAME/kurodot-agent.git
cd kurodot-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export GEMINI_API_KEY="your_key_here"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open http://localhost:8000 and drop an exhibition URL onto a sticky note.

Supported URL formats:
- `https://app.kurodot.io/exhibition/bauhaus-blueprint-qevdv`
- `https://www.fu-design.com/exhibition/bauhaus-blueprint-qevdv`

---

## ☁️ Deploy to Google Cloud Run

```bash
# One-time setup
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Deploy (Python 3.11 required for local gcloud compat)
CLOUDSDK_PYTHON=/usr/local/bin/python3.11 gcloud run deploy kurodot-agent \
  --source . --region us-central1 --allow-unauthenticated
```

---

## 🏗️ Infrastructure as Code (Terraform)

> All GCP resources are **100% code-defined** — no manual Console clicks required. Running `terraform apply` provisions or updates the entire stack from scratch.

### What Terraform manages

| Resource | Terraform ID | Purpose |
|---|---|---|
| **Cloud Run v2 Service** | `google_cloud_run_v2_service.kurodot_agent` | Serverless backend, auto-scaled 0 → `max_instances` |
| **Cloud Run IAM** | `google_cloud_run_v2_service_iam_member.public_invoker` | `allUsers` → `roles/run.invoker` (public access) |
| **GCS Bucket** | `google_storage_bucket.exports` | Tech Producer canvas export uploads |
| **GCS IAM** | `google_storage_bucket_iam_member.public_read` | `allUsers` → `roles/storage.objectViewer` (public downloads) |

### Files

```
infra/
├── main.tf                    # Cloud Run service + IAM + GCS bucket
├── variables.tf               # Input variables (project, region, secrets)
├── outputs.tf                 # Service URL output
└── terraform.tfvars.example   # Copy → terraform.tfvars, fill in values
```

### First-time setup

```bash
# 1. Install Terraform  (https://developer.hashicorp.com/terraform/downloads)
brew install terraform          # macOS

# 2. Authenticate to GCP
gcloud auth application-default login

# 3. Configure variables
cd infra
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your project_id, GEMINI_API_KEY, etc.
```

### Deploy / update infrastructure

```bash
cd infra
terraform init       # download Google provider (~first run)
terraform plan       # preview changes
terraform apply      # provision / update resources
```

After `terraform apply`, the live service URL is printed:

```
Outputs:
  service_url = "https://kurodot-agent-<hash>.us-central1.run.app"
```

> **Note:** `terraform.tfvars` contains secrets — it is listed in `.gitignore` and must never be committed.

---

## 🤖 Automated Deployment — GitHub Actions

A CI/CD pipeline (`.github/workflows/deploy.yml`) runs on every push to `main`:

```
push to main
  │
  ├─ 1. Checkout code
  ├─ 2. Authenticate to GCP  (Workload Identity / service account key)
  ├─ 3. gcloud builds submit  (Cloud Build → Container Registry)
  └─ 4. gcloud run deploy     (Cloud Run — zero-downtime rolling update)
```

### One-time setup (GitHub Secrets)

| Secret | Value |
|---|---|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_SA_KEY` | Base64-encoded service account JSON key with `roles/run.admin`, `roles/storage.admin`, `roles/cloudbuild.builds.editor` |

After adding the secrets, every `git push origin main` triggers a full redeploy automatically.

---

## 開發規則

- 所有角色的 agent 功能只寫在自己的 `.py` 檔裡面，不能開新檔案
- Designer 確保所有文字顯示正常，不超出外框，有正確 padding
- Editor 只能改文字，不能改 design
- PM 可以分派任務
- Tech 可以輸出 jpg、png、pdf、svg
- UI 全英文
- 每次完成更新告訴我新的版本號碼
- 自動檢查並修好語法錯誤
- UI 佈局：sticky note · agent 按鈕列 · agent 狀態列 · 畫布（畫面中央）
