import requests
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import asyncio
from typing import Dict, Any
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
        is_square = "square" in url.lower() or "1:1" in url.lower() or "正方" in url.lower()
        shape = "square" if is_square else "16:9"
        job["design_shape"] = shape
        
        # Simulated extraction for kurodot and fu-design
        ex_id = None
        if "fu-design.com" in url.lower():
            # Example: https://www.fu-design.com/api/exhibit?id=123
            fu_id_match = re.search(r"id=([a-zA-Z0-9_-]+)", url)
            if fu_id_match:
                ex_id = fu_id_match.group(1)
        else:
            # Kurodot formats: ex_ID or /exhibition/ID or id=ID
            ex_id_match = re.search(r"ex_([a-zA-Z0-9_-]+)|exhibition/([a-zA-Z0-9_-]+)|id=([a-zA-Z0-9_-]+)", url)
            if ex_id_match:
                ex_id = ex_id_match.group(1) or ex_id_match.group(2) or ex_id_match.group(3)
        
        # If still no ID found, try to treat the whole string as ID if it matches basic patterns
        if not ex_id and len(url) > 5 and "/" not in url and "." not in url:
            ex_id = url.strip()

        # Fallback for empty or unknown
        if not ex_id:
            ex_id = "bauhaus-blueprint-qevdv"
        
        # Clean up ex_id - remove common URL fragments if any
        if ex_id and "?" in ex_id:
            ex_id = ex_id.split("?")[0]
        
        log(f"PM: Analyzing curation source... Found Exhibition ID: {ex_id}")

        ex_data = None
        artworks = []

        if exhibition_data:
            # Case 1: Browser pre-fetched the data
            ex_data = exhibition_data.get("exhibition", exhibition_data)
            artworks = exhibition_data.get("artworks", [])
            log(f"PM: Using pre-fetched data for: {ex_data.get('title', 'Unknown')}")
        else:
            # Case 2: Attempt dynamic fetch with Vercel Bypass Token
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
                elif resp.status_code == 429:
                    log("PM: [429] Server Rate Limited. Client-side fetch is required for this IP.")
                else:
                    log(f"PM: API Error {resp.status_code}.")
            except Exception as e:
                log(f"PM: API Exception: {str(e)}")

        # --- Data Mapping (Centralized) ---
        if ex_data and (ex_data.get("title") or ex_data.get("ex_title")):
            # Support both metadata formats (kurodot vs fu-design)
            ex_title = ex_data.get("title") or ex_data.get("ex_title") or f"Exhibition {ex_id[:5]}"
            ex_subtitle = ex_data.get("subtitle") or ex_data.get("ex_subtitle") or ""
            artist = ex_data.get("artist") or ex_data.get("ex_artist") or "Featured Artist"
            venue = ex_data.get("venue") or ex_data.get("ex_venue") or "Kurodot Virtual Gallery"
            artworks_count = len(artworks) if artworks else ex_data.get("ex_artworks_count", 0)
            ex_description = ex_data.get("description") or ex_data.get("ex_description") or f"Experience an incredible journey featuring {artworks_count} exclusive masterpieces by {artist}."
            
            # Find image
            ex_img_url = None
            # Check for direct field first (fu-design format)
            if ex_data.get("ex_img_url"):
                ex_img_url = ex_data.get("ex_img_url")
            
            if not ex_img_url:
                for key in ["posterUrl", "poster", "cover", "coverImage", "image"]:
                    val = ex_data.get(key)
                    if val and isinstance(val, str) and val.startswith("http") and not any(ext in val.lower() for ext in [".glb", ".gltf"]):
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
            # ERROR STATE: Stop workflow
            log(f"PM: ERROR - Data Missing for ID: {ex_id}.")
            job["status"] = "error"
            job["logs"].append(f"❌ Error: Could not get stable data for ID: {ex_id}. (Vercel 429/403).")
            return

        job["ex_title"] = ex_title
        job["ex_subtitle"] = ex_subtitle
        job["ex_img_url"] = ex_img_url
        job["ex_description"] = ex_description
        job["ex_artist"] = artist
        job["ex_venue"] = venue
        job["ex_artworks_count"] = artworks_count
        job["ex_date"] = "March 2026"  # Static for demo consistency

        await run_agent("project-manager", 2.0, f"PM: API Data Fetched for Exhibition: {ex_id}")
        await run_agent("analyst", 1.5, f"ANALYST: Parsed '{ex_title}' semantics.")
        
        # Simulated analyst results for display
        job["ex_visitors"] = 8900 
        
        job["agents"]["vi-designer"] = "Executing"
        log("DESIGNER: Scaffolding DOM blank layout...")
        job["current_step"] = "designer_white_frame"
        await asyncio.sleep(2)
        
        log("DESIGNER: Integrating background visuals...")
        job["current_step"] = "designer_add_image"
        await asyncio.sleep(1.5)
        job["agents"]["vi-designer"] = "Completed"
        
        job["agents"]["editor"] = "Executing"
        log("EDITOR: Drafting punchy typography...")
        job["current_step"] = "editor_add_text"
        await asyncio.sleep(1.5)
        job["agents"]["editor"] = "Completed"
        
        await run_agent("tech-producer", 1, "TECH: Finalizing CSS alignments and preparing export...")
        
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
