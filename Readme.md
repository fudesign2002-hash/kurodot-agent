# Kurodot AI

Kurodot AI is a multi-agent curatorial orchestrator that turns exhibition content into polished, export-ready visual banners in real time.

Built for the Gemini Live Agent Challenge under the Creative Storyteller category.

Live demo:
https://kurodot-agent-1063202705342.us-central1.run.app

## Overview

The system combines five specialized agents:

| Agent | Responsibility | Model / System |
|---|---|---|
| Project Manager | Orchestration, task routing, session flow | Hub only |
| VI Designer | Layout, aspect ratio, background, image composition | `gemini-2.5-flash-image` |
| Editor | Translation and copy revision | `gemini-2.0-flash-001` |
| Data Analyst | Traffic insight and recommendation support | External API + Hub |
| Tech Producer | Export and output packaging | Browser export + GCS |

## Core Capabilities

- Convert exhibition URLs into visual banners.
- Support one-shot commands such as `Create a 3:2 banner from https://...`.
- Let agents revise design and copy through sticky-note commands.
- Export final output as JPG, PNG, and PDF.
- Run locally with FastAPI and deploy to Google Cloud Run.

## Architecture

```text
User
  -> opencanvas.html
  -> FastAPI (main.py)
  -> Agent orchestration
     -> Project Manager
     -> VI Designer
     -> Editor
     -> Data Analyst
     -> Tech Producer
```

Main API routes:

- `POST /api/start_curation`
- `GET /api/job/{id}`
- `POST /api/interleaved-story`
- `POST /api/translate`
- `POST /api/pm/session`
- `POST /api/pm/session/{id}/done`

## Technology Stack

### Google / GCP

| Technology | Usage |
|---|---|
| `google-genai` | Gemini API integration |
| Gemini 2.5 Flash Image | Interleaved text and image generation |
| Gemini 2.0 Flash 001 | Translation and editorial generation |
| Cloud Run | Backend hosting |
| Cloud Build | Container builds |
| Artifact Registry / container image storage | Deployment image source |
| Cloud Storage | Export uploads |

### Application

| Technology | Usage |
|---|---|
| Python 3.11 in container / 3.9 local | Runtime |
| FastAPI + Uvicorn | API server |
| Vanilla JS + HTML5 Canvas | Frontend SPA |
| Firebase Admin / Pyrebase4 | Exhibition data |
| Umami API | Analytics lookups |

## Project Structure

```text
kurodot-agent/
├── main.py
├── opencanvas.html
├── settings.py
├── requirements.txt
├── Dockerfile
├── deploy.sh
├── infra/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
├── agents/
│   ├── project_manager.py
│   ├── vi_designer.py
│   ├── editor.py
│   ├── analyst.py
│   └── tech_producer.py
└── utils/
    └── logger.py
```

## Local Development

```bash
git clone https://github.com/YOUR_USERNAME/kurodot-agent.git
cd kurodot-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GEMINI_API_KEY="your_key_here"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open:

`http://localhost:8000`

Supported URL formats:

- `https://app.kurodot.io/exhibition/bauhaus-blueprint-qevdv`
- `https://www.fu-design.com/exhibition/bauhaus-blueprint-qevdv`

## Manual Deployment

Deploy directly with `gcloud`:

```bash
export PATH="$HOME/google-cloud-sdk/bin:$PATH"
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

CLOUDSDK_PYTHON=/usr/local/bin/python3.11 gcloud run deploy kurodot-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

Or use the helper script:

```bash
./deploy.sh
```

## Infrastructure as Code

Terraform in `infra/` manages the deployment infrastructure.

| Resource | Purpose |
|---|---|
| Cloud Run service | Hosts the backend |
| Cloud Run IAM | Public access |
| GCS bucket | Export storage |
| GCS IAM | Public download access |

First-time setup:

```bash
brew install terraform
gcloud auth application-default login
cd infra
cp terraform.tfvars.example terraform.tfvars
```

Deploy or update:

```bash
cd infra
terraform init
terraform plan
terraform apply
```

Notes:

- `infra/terraform.tfvars` contains secrets.
- Do not commit `terraform.tfvars`.
- It is already ignored by git.

## GitHub Actions CI/CD

Workflow file:

`.github/workflows/deploy.yml`

Pipeline flow:

1. Check out the repository.
2. Install `gcloud` on the runner.
3. Decode the base64 service account key and authenticate.
4. Submit Cloud Build asynchronously.
5. Poll Cloud Build status until success.
6. Deploy the built image to Cloud Run.
7. Print the live service URL.

Required repository secrets:

| Secret | Description |
|---|---|
| `GCP_PROJECT_ID` | GCP project ID |
| `GCP_SA_KEY` | Base64-encoded service account JSON key |
| `GEMINI_API_KEY` | Gemini API key injected into Cloud Run |

Required service account roles:

- `roles/run.admin`
- `roles/iam.serviceAccountUser`
- `roles/cloudbuild.builds.editor`
- `roles/storage.admin`
- `roles/artifactregistry.reader`

Additional runtime permission:

- The Cloud Run service agent also needs `roles/artifactregistry.reader` so it can pull the deployed image.

After the secrets are configured, every push to `main` triggers an automatic deployment.

## Creative Storyteller API

Endpoint:

`POST /api/interleaved-story`

Example:

```bash
curl -s -X POST https://kurodot-agent-1063202705342.us-central1.run.app/api/interleaved-story \
  -H "Content-Type: application/json" \
  -d '{"exhibition_info": "Bauhaus Blueprint: geometric forms, primary colours, industrial design"}'
```

The response includes:

- `text_parts`
- `image_data`

Both are generated in a single `gemini-2.5-flash-image` call.

## Development Rules

- All agent behavior stays in the existing `.py` files.
- Do not create extra files for agent role logic.
- Designer must keep text readable, padded correctly, and inside bounds.
- Editor can change text only, not layout.
- PM can assign tasks.
- Tech Producer can export JPG, PNG, PDF, and SVG.
- UI text should stay in English.
- After each update, record the new version or commit.
- Check and fix syntax errors before shipping.
- Keep the UI centered around sticky notes, agent controls, status bar, and canvas.

