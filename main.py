import requests
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from typing import Dict, Any, List
import settings

app = FastAPI()

class JobRequest(BaseModel):
    url: str
    exhibition_data: Any = None

jobs: Dict[str, Any] = {}

import uuid

# Provide standard agent states: Idle, Received, Executing, Completed

# import agents
from agents.project_manager import ProjectManagerAgent

@app.get("/api/settings")
async def get_settings():
    return {
        "testing_mode": settings.TESTING_MODE,
        "test_url": settings.TEST_URL,
        "test_instruction": settings.TEST_INSTRUCTION
    }

# ── Creative Storyteller: Interleaved text + image endpoint ─────────────────
class InterleavedRequest(BaseModel):
    exhibition_info: str

@app.post("/api/interleaved-story")
async def interleaved_story(req: InterleavedRequest):
    """
    Creative Storyteller endpoint: uses Gemini interleaved output (text + image)
    to generate a curatorial narrative and key visual in a single response.
    Returns text parts and base64 PNG image data.
    """
    from agents.vi_designer import VIDesignerAgent
    designer = VIDesignerAgent()
    result = designer.generate_interleaved_story(req.exhibition_info)
    return JSONResponse(content=result)

@app.post("/api/start_curation")
async def start_curation(req: JobRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "running",
        "current_step": "init",
        "design_shape": "16:9",
        "agents": {
            "analyst": "Idle",
            "editor": "Idle",
            "project-manager": "Idle",
            "tech-producer": "Idle",
            "vi-designer": "Idle"
        },
        "logs": [],
        "result_url": None
    }
    background_tasks.add_task(run_curation_workflow, job_id, req.url, req.exhibition_data)
    return {"job_id": job_id}

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    # Handle manual/standalone tasks that might not be in the 'jobs' dict
    if job_id == "manual-task" and job_id not in jobs:
        from utils.logger import hub
        pending_tasks = []
        for role in ["tech", "vi-designer", "analyst", "editor"]:
            tasks = hub.get_pending_tasks(role)
            if tasks:
                pending_tasks.extend(tasks)
        
        dismissals = hub.get_dismiss_queue()
        return {
            "job_id": "manual-task",
            "pending_tasks": pending_tasks,
            "dismiss_ids": dismissals,
            "agents": {},
            "logs": []
        }

    if job_id not in jobs:
        return {"error": "not found"}
    
    # Bundle dismiss queue and scheduled tasks from Hub into the job status
    from utils.logger import hub
    dismissals = hub.get_dismiss_queue()
    if dismissals:
        if "dismiss_ids" not in jobs[job_id]:
            jobs[job_id]["dismiss_ids"] = []
        jobs[job_id]["dismiss_ids"].extend(dismissals)
        
    # Get pending tasks for all relevant roles to notify the frontend
    pending_tasks = []
    for role in ["tech", "vi-designer", "analyst", "editor"]:
        tasks = hub.get_pending_tasks(role)
        if tasks:
            pending_tasks.extend(tasks)
    
    if pending_tasks:
        jobs[job_id]["pending_tasks"] = pending_tasks
        
    return jobs[job_id]

class TaskRequest(BaseModel):
    role: str
    task_type: str
    priority: int = 10

@app.post("/api/job/{job_id}/schedule")
async def schedule_agent_task(job_id: str, req: TaskRequest):
    if job_id not in jobs:
        return {"error": "not found"}
    
    from utils.logger import hub
    task_id = hub.schedule_task(req.role, req.task_type, req.priority)
    return {"task_id": task_id}

@app.post("/api/job/{job_id}/task/{task_id}/status")
async def update_agent_task_status(job_id: str, task_id: str, status: str):
    if job_id not in jobs:
        return {"error": "not found"}
    
    from utils.logger import hub
    success = hub.update_task_status(task_id, status)
    return {"success": success}


# ── PM Dispatch Session Endpoints ───────────────────────────────────────────

class PMSessionRequest(BaseModel):
    session_id: str
    roles: List[str]

class AgentDoneRequest(BaseModel):
    role: str

@app.post("/api/pm/session")
async def open_pm_session(req: PMSessionRequest):
    from utils.logger import hub
    hub.open_pm_session(req.session_id, req.roles)
    return {"ok": True}

@app.post("/api/pm/session/{session_id}/done")
async def close_agent_task(session_id: str, req: AgentDoneRequest):
    from utils.logger import hub
    all_done = hub.close_agent_task(session_id, req.role)
    return {"all_done": all_done}

@app.get("/api/pm/session/{session_id}")
async def get_pm_session(session_id: str):
    from utils.logger import hub
    return hub.get_pm_session(session_id)


async def run_curation_workflow(job_id: str, url: str, exhibition_data: dict = None):
    job = jobs[job_id]
    
    def log(msg):
        job["logs"].append(msg)
    
    async def run_agent(name, delay=2, msg=""):
        job["agents"][name] = "Received"
        await asyncio.sleep(0.5)
        job["agents"][name] = "Executing"
        log(f"{msg}")
        await asyncio.sleep(delay)
        job["agents"][name] = "Completed"
    
    try:
        import json
        import re
        import os
        import requests
        
        # 1. Shape Analysis
        is_square = any(x in url.lower() for x in ["square", "1:1", "正方"])
        shape = "square" if is_square else "16:9"
        job["design_shape"] = shape
        
        # 2. Exhibition ID Extraction (Robust Regex)
        ex_id = None
        # Pattern covers: /exhibition/ID, ?id=ID, ex_ID, or just the ID at the end of string
        patterns = [
            r"exhibition/([a-zA-Z0-9_-]{10,})",
            r"id=([a-zA-Z0-9_-]{10,})",
            r"ex_([a-zA-Z0-9_-]{10,})",
            r"([a-zA-Z0-9_-]{15,})$" # Catch-all for ID-only or long IDs at end
        ]
        
        for p in patterns:
            match = re.search(p, url)
            if match:
                ex_id = match.group(1)
                break
        
        # Fallback for empty or unknown
        if not ex_id:
            ex_id = "bauhaus-blueprint-qevdv"
            log(f"PM: Could not extract specific ID from prompt. Using default: {ex_id}")
        else:
            log(f"PM: Analyzing curation source... Found Exhibition ID: {ex_id}")

        # 3. Data Retrieval Logic (Chain: Pre-fetched -> API -> Local JSON)
        ex_data = None
        artworks = []
        api_payload = {}

        # Stage A: Check if browser already passed data
        if exhibition_data:
            api_payload = exhibition_data
            ex_data = api_payload.get("exhibition", api_payload)
            artworks = api_payload.get("artworks", [])
            log(f"PM: Using pre-fetched data for: {ex_data.get('title', 'Unknown')}")
        
        # Stage B: Attempt dynamic fetch if no pre-fetched data
        if not ex_data:
            try:
                is_fu = "fu-design.com" in url.lower()
                base_api = "https://www.fu-design.com/api/exhibit" if is_fu else "https://app.kurodot.io/api/exhibit"
                api_url = f"{base_api}?id={ex_id}"
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json",
                    "Referer": "https://app.kurodot.io/" if not is_fu else "https://www.fu-design.com/"
                }
                
                if hasattr(settings, 'VERCEL_BYPASS_TOKEN') and settings.VERCEL_BYPASS_TOKEN:
                    headers["x-vercel-protection-bypass"] = settings.VERCEL_BYPASS_TOKEN
                
                log(f"PM: Server attempting fetch from: {api_url}")
                resp = requests.get(api_url, headers=headers, timeout=8)
                
                if resp.status_code == 200 and 'application/json' in resp.headers.get('content-type', '').lower():
                    api_payload = resp.json()
                    ex_data = api_payload.get("exhibition", api_payload)
                    artworks = api_payload.get("artworks", [])
                    log(f"PM: Successfully retrieved live data for: {ex_data.get('title')}")
                else:
                    log(f"PM: API returned {resp.status_code}. Moving to local fallback.")
            except Exception as e:
                log(f"PM: API Fetch Exception: {str(e)}")

        # Stage C: Local Backup (Mandatory fallback if API fails)
        if not ex_data and ex_id:
            local_path = f"temp/data/{ex_id}.json"
            if os.path.exists(local_path):
                try:
                    log(f"PM: [Fallback] Loading local data from {local_path}...")
                    with open(local_path, "r", encoding="utf-8") as f:
                        api_payload = json.load(f)
                        ex_data = api_payload.get("exhibition", api_payload)
                        artworks = api_payload.get("artworks", [])
                        log(f"PM: Local data loaded successfully for: {ex_data.get('title')}")
                except Exception as e:
                    log(f"PM: Local JSON fallback error: {str(e)}")
            else:
                log(f"PM: No local file found at {local_path}")

        # 4. Standardized Data Mapping
        if ex_data and (ex_data.get("title") or ex_data.get("ex_title")):
            # Extract fields with cross-compat for different API formats
            ex_title = ex_data.get("title") or ex_data.get("ex_title", "Untitled Exhibition")
            ex_subtitle = ex_data.get("subtitle") or ex_data.get("ex_subtitle", "")
            artist = ex_data.get("artist") or ex_data.get("ex_artist", "Kurodot Artist")
            venue = ex_data.get("venue") or ex_data.get("ex_venue", "Kurodot virtual gallery")
            artworks_count = len(artworks) if artworks else ex_data.get("ex_artworks_count", 0)
            
            # Smart Description parsing
            ex_description = ex_data.get("overview") or ex_data.get("description") or ex_data.get("ex_description")
            
            # --- UPDATED CONTENT POLICY: Trust Editor to generate concise text ---
            # We remove the hard truncation logic to avoid cutting sentences mid-word.
            # Instead, we just ensure it's not absolutely massive (e.g. > 1000 chars).
            if ex_description and len(ex_description) > 1000:
                 ex_description = ex_description[:997] + "..."
            
            if not ex_description:
                 ex_description = f"Experience an incredible journey featuring {artworks_count} exclusive masterpieces by {artist}. Join us as we explore the intersection of art and technology across {venue}."
            
            # Select Cover Image
            ex_img_url = None
            image_keys = ["posterUrl", "poster", "cover", "coverImage", "image", "ex_img_url"]
            for key in image_keys:
                val = ex_data.get(key)
                if val and isinstance(val, str) and val.startswith("http") and not any(ext in val.lower() for ext in [".glb", ".gltf", ".mp4"]):
                    ex_img_url = val
                    break
            
            if not ex_img_url and artworks:
                for aw in artworks:
                    for key in ["artworkFile", "file", "image", "thumbnail"]:
                        af = aw.get(key)
                        if af and isinstance(af, str) and af.startswith("http") and not any(ext in af.lower() for ext in [".glb", ".gltf", ".mp4"]):
                            ex_img_url = af
                            break
                    if ex_img_url: break

            if not ex_img_url:
                ex_img_url = "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?auto=format&fit=crop&q=80&w=800"
        else:
            log(f"PM: CRITICAL ERROR - No viable data found for ID: {ex_id}")
            job["status"] = "error"
            job["logs"].append(f"❌ Error: Exhausted all data sources for ID: {ex_id}. Please check the URL.")
            return

        # 5. Populate Job Object (This is what the frontend consumes via 'extra')
        job["ex_title"] = ex_title
        job["ex_subtitle"] = ex_subtitle
        job["ex_img_url"] = ex_img_url
        job["ex_description"] = ex_description
        job["ex_artist"] = artist
        job["ex_venue"] = venue
        job["ex_artworks_count"] = artworks_count
        job["ex_date"] = "March 2026"

        # 6. Kick off Agents in Collaborative Chain
        await run_agent("project-manager", 1.5, f"PM: Source analysis complete for {ex_id}. Orchestrating team... 🤝")
        
        # Collaborative Step 1: Analyst provides context
        await run_agent("analyst", 1.0, f"ANALYST: Processing semantics for '{ex_title}'")
        
        # Collaborative Step 2: Editor writes the content based on PM's brief
        # We explicitly set a shorter placeholder here to show "work in progress"
        job["ex_description"] = "Editor is drafting a concise curatorial statement..." 
        await run_agent("editor", 2.0, "EDITOR: Drafting a 3-4 sentence curatorial statement...")
        
        # SIMULATION: In a real system, we'd call editor_agent.generate() here.
        # For this demo flow, we now update the job description with the "refined" content
        # that fulfills the "3-4 sentences" rule.
        refined_description = (
            f"This exhibition features the signature works of {artist}. "
            f"Each piece invites the viewer into a futuristic dialogue of form and function. "
            f"Experience this incredible journey across {venue} through exclusive masterpieces. "
            f"Chu's visionary designs bridge the gap between imagination and contemporary art."
        )
        job["ex_description"] = refined_description
        job["current_step"] = "editor_add_text"
        
        # Collaborative Step 3: Designer takes Editor's text and applies layout
        await run_agent("vi-designer", 1.5, "DESIGNER: Receiving Editor's copy. Scaffolding canvas...")
        job["current_step"] = "designer_white_frame"
        
        await run_agent("vi-designer", 1.5, "DESIGNER: Aligning visual assets to the new narrative. Love the flow! ❤️")
        job["current_step"] = "designer_add_image"
        
        await run_agent("tech-producer", 1, "TECH: Optimizing layout delivery and preparing export...")
        
        # Collaborative Step 4: Editor follow-up suggestion (Japanese Localization)
        # We manually trigger this specifically for the demo flow after tech is done
        from utils.logger import hub
        hub.register_recommendation(
            agent_id="editor", 
            rec_id="editor_japanese_localization", 
            content="Editorial Insight: 30% of visitors are from Tokyo. Recommend adding a Japanese version for better local reach?"
        )
        
        # Ensure the recommendation is immediately visible in the logs for the UI to pick up
        log("EDITOR: Generated suggestion: Editorial Insight: 30% of visitors are from Tokyo. Recommend adding a Japanese version?")
        
        log("PM: Workflow completed successfully! Well done team! 👏")
        job["status"] = "finished"
    except Exception as e:
        job["status"] = "error"
        job["logs"].append(f"Error: {e}")

from fastapi.responses import HTMLResponse, FileResponse
import os

# Tracking modification time for live-reload
LAST_MODIFIED_TIME = os.path.getmtime("opencanvas.html")

@app.get("/api/check_updates")
async def check_updates():
    global LAST_MODIFIED_TIME
    try:
        current_mtime = os.path.getmtime("opencanvas.html")
        if current_mtime > LAST_MODIFIED_TIME:
            # We don't update LAST_MODIFIED_TIME here to allow all clients to see the update
            return {"updated": True, "time": current_mtime}
    except Exception as e:
        pass
    return {"updated": False}

@app.get("/")
def read_root():
    global LAST_MODIFIED_TIME
    LAST_MODIFIED_TIME = os.path.getmtime("opencanvas.html")
    with open("opencanvas.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content, headers={
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    })

@app.get("/booklet.html")
def read_booklet():
    return FileResponse("booklet.html")
