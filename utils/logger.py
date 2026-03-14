import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure Standard Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("CurationHub")

class AgentCollaborationHub:
    """
    Agent Collaboration Hub:
    - Acts as a centralized communication channel (Stream) for all agents.
    - Tracks recommendations by ID to prevent duplication.
    - Manages cross-agent task statuses: [start, in-progress, complete]
    - Types: [task, recommendation]
    """
    def __init__(self, state_path: str = "temp/collaboration_state.json"):
        self.state_path = state_path
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        # --- IN-MEMORY DEDUP STRUCTURES (never written to file, always authoritative) ---
        # Tracks every log_id ever emitted this process lifetime — no window limitation
        self._seen_log_ids: set = set()
        # Maps (role, msg, status) → last emit timestamp for content-based dedup
        self._recent_content: Dict[tuple, float] = {}
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
            except Exception:
                self.state = {"recommendations": {}, "history": [], "logs": []}
        else:
            self.state = {"recommendations": {}, "history": [], "logs": []}
        
        if "logs" not in self.state:
            self.state["logs"] = []

        # Rebuild _seen_log_ids from persisted logs so server restarts stay consistent
        for l in self.state.get("logs", []):
            if l.get("log_id"):
                self._seen_log_ids.add(l["log_id"])

    def _save_state(self):
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)

    def emit_log(self, role: str, msg: str, log_type: str = "task", status: str = "in-progress", log_id: str = None):
        """
        Emits a structured log that the frontend UI can interpret as Bubbles/Console messages.
        - log_id: (Optional) Unique identifier to prevent duplicate bubbling.
        Status: start | in-progress | complete
        Type: task | recommendation

        Dedup strategy (in-memory, not file-based):
        1. log_id: tracked in a set — never emits the same ID twice per process lifetime.
        2. content (role+msg+status): tracked with timestamp — suppressed if same content
           was emitted within the last 3 seconds.
        """
        now_ts = datetime.now().timestamp()

        # --- DEDUP 1: by log_id (in-memory set, no window limitation) ---
        if log_id:
            if log_id in self._seen_log_ids:
                logger.info(f"[HUB] Suppressed duplicate log_id for {role}: {log_id}")
                return False
            self._seen_log_ids.add(log_id)

        # --- DEDUP 2: by content within 3 seconds (in-memory dict, fast O(1) lookup) ---
        content_key = (role, msg, status)
        last_ts = self._recent_content.get(content_key)
        if last_ts is not None and (now_ts - last_ts) < 3.0:
            logger.info(f"[HUB] Suppressed duplicate content within 3s for {role}: {msg[:60]}")
            # Undo the log_id registration since we're not emitting
            if log_id:
                self._seen_log_ids.discard(log_id)
            return False
        self._recent_content[content_key] = now_ts

        # Prune stale entries from _recent_content to avoid unbounded growth
        stale = [k for k, ts in self._recent_content.items() if now_ts - ts > 30.0]
        for k in stale:
            del self._recent_content[k]

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "role": role, # analyst, designer, editor, pm, tech
            "message": msg,
            "type": log_type,
            "status": status,
            "log_id": log_id
        }
        self.state["logs"].append(log_entry)
        
        # Consistent string format for existing regex parsing if needed
        status_prefix = "STARTED" if status == "start" else ("COMPLETED" if status == "complete" else "EXECUTING")
        logger.info(f"[{role.upper()}] {status_prefix}: {msg}")
        
        # Limit log history
        if len(self.state["logs"]) > 100:
            self.state["logs"] = self.state["logs"][-100:]
            
        self._save_state()

    def register_recommendation(self, agent_id: str, rec_id: str, content: str):
        """Registers an Analyst recommendation and emits structured logs with ID tracking."""
        if rec_id not in self.state["recommendations"]:
            self.state["recommendations"][rec_id] = {
                "origin": agent_id,
                "content": content,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            # Emit structured logs for the bubble UI (pass rec_id as log_id to avoid dupe)
            self.emit_log(
                role=agent_id, 
                msg=f"Generated suggestion: {content}", 
                log_type="recommendation", 
                status="start", 
                log_id=rec_id
            )
            self._save_state()
            return True
        return False

    def schedule_task(self, role: str, task_type: str, priority: int = 10):
        """
        Schedules a task for a specific agent role.
        - tech: usually requires waiting for 'designer' and 'analyst' to finish.
        """
        if "task_schedule" not in self.state:
            self.state["task_schedule"] = []
            
        task_id = f"task_{int(datetime.now().timestamp() * 1000)}"
        new_task = {
            "id": task_id,
            "role": role,
            "type": task_type,
            "status": "scheduled",
            "priority": priority,
            "created_at": datetime.now().isoformat()
        }
        
        # Tech tasks are special: they often need a "waiting" state if other tasks are active
        if role == "tech":
            new_task["status"] = "waiting"
            new_task["wait_until"] = datetime.now().timestamp() + 2.0  # Default 2s wait
            
        self.state["task_schedule"].append(new_task)
        
        # Emit structured log: TASK START (Assigned by PM)
        self.emit_log("pm", f"Scheduled {task_type} for {role}", log_type="task", status="start")
        
        self._save_state()
        return task_id

    def get_pending_tasks(self, role: str) -> List[Dict[str, Any]]:
        """Returns tasks that are ready to be executed for a given role."""
        if "task_schedule" not in self.state:
            return []
            
        now = datetime.now().timestamp()
        ready_tasks = []
        
        for task in self.state["task_schedule"]:
            if task["role"] == role and task["status"] in ["scheduled", "waiting"]:
                # Check if wait time is over
                if task["status"] == "waiting" and task.get("wait_until", 0) <= now:
                    task["status"] = "scheduled"
                
                if task["status"] == "scheduled":
                    ready_tasks.append(task)
                    
        return ready_tasks

    def update_task_status(self, task_id: str, status: str):
        """Updates the status of a scheduled task (e.g., 'running', 'completed')."""
        if "task_schedule" not in self.state:
            return False
            
        for task in self.state["task_schedule"]:
            if task["id"] == task_id:
                old_status = task.get("status", "unknown")
                task["status"] = status
                task["updated_at"] = datetime.now().isoformat()
                
                # Emit structured log for UI: STATUS CHANGE
                ui_status = "in-progress" if status == "running" else ("complete" if status == "completed" else "in-progress")
                self.emit_log(task["role"], f"Task {task['type']} ({task_id}) updated: {status}", log_type="task", status=ui_status)
                
                self._save_state()
                return True
        return False

    def check_status(self, rec_id: str) -> str:
        """Checks if a recommendation is 'pending' or 'completed'."""
        return self.state["recommendations"].get(rec_id, {}).get("status", "unknown")

    def mark_completed(self, rec_id: str, handled_by: str):
        """Marks a recommendation as applied by another agent and signals UI to dismiss."""
        if rec_id in self.state["recommendations"]:
            rec = self.state["recommendations"][rec_id]
            rec["status"] = "completed"
            rec["applied_by"] = handled_by
            rec["completed_at"] = datetime.now().isoformat()
            
            # Emit structured log: RECOMMENDATION COMPLETE
            self.emit_log(handled_by, f"Applied recommendation: {rec_id}", log_type="recommendation", status="complete")
            
            # Add to a global 'to_dismiss' queue for the frontend to poll
            if "dismiss_queue" not in self.state:
                self.state["dismiss_queue"] = []
            self.state["dismiss_queue"].append(rec_id)
            
            self._save_state()
            return True
        return False

    def get_dismiss_queue(self) -> List[str]:
        """Returns and clears the current dismissal queue."""
        queue = self.state.get("dismiss_queue", [])
        if queue:
            self.state["dismiss_queue"] = []
            self._save_state()
        return queue

    def set_layout_constraint(self, constraint_type: str, value: Any):
        """Sets a physical layout constraint (e.g., max_chars) for other agents to follow."""
        if "constraints" not in self.state:
            self.state["constraints"] = {}
        self.state["constraints"][constraint_type] = value
        logger.info(f"📏 New Layout Constraint [{constraint_type}]: {value}")
        self._save_state()

    def get_constraint(self, constraint_type: str) -> Optional[Any]:
        return self.state.get("constraints", {}).get(constraint_type)

    # ── PM Dispatch Session ──────────────────────────────────────────────────
    def open_pm_session(self, session_id: str, roles: List[str]):
        """PM opens a dispatch session. Records which agent roles were dispatched."""
        if "pm_sessions" not in self.state:
            self.state["pm_sessions"] = {}
        self.state["pm_sessions"][session_id] = {
            "roles": roles,
            "completed": [],
            "celebrated": False,
            "opened_at": datetime.now().isoformat()
        }
        self.emit_log(
            "pm",
            f"PM dispatching to: {', '.join(r.upper() for r in roles)}",
            log_type="task", status="start",
            log_id=f"pm_dispatch_{session_id}"
        )
        self._save_state()

    def close_agent_task(self, session_id: str, role: str) -> bool:
        """
        Mark one agent role as done in the session.
        Returns True (and emits PM celebration) when ALL dispatched agents are done.
        """
        import random
        sessions = self.state.get("pm_sessions", {})
        if session_id not in sessions:
            return False
        session = sessions[session_id]
        if session.get("celebrated"):
            return False
        if role not in session["completed"]:
            session["completed"].append(role)
        if set(session["completed"]) >= set(session["roles"]):
            session["celebrated"] = True
            celebrations = [
                "PM: Great work, team! All tasks completed perfectly! 🎉🥂✨",
                "PM: Outstanding! Everyone nailed it! 🎊🥂",
                "PM: Superb collaboration! The curation looks amazing! 🎉✨",
                "PM: All done! Brilliant team effort! 👏🎉🍾",
            ]
            self.emit_log(
                "pm", random.choice(celebrations),
                log_type="task", status="complete",
                log_id=f"pm_celebrate_{session_id}"
            )
            self._save_state()
            return True
        self._save_state()
        return False

    def get_pm_session(self, session_id: str) -> dict:
        """Returns the current state of a PM dispatch session."""
        return self.state.get("pm_sessions", {}).get(session_id, {})


# Shared Global instance
hub = AgentCollaborationHub()
