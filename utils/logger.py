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
    - Manages cross-agent task statuses like a miniature project manager.
    """
    def __init__(self, state_path: str = "temp/collaboration_state.json"):
        self.state_path = state_path
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
            except Exception:
                self.state = {"recommendations": {}, "history": []}
        else:
            self.state = {"recommendations": {}, "history": []}

    def _save_state(self):
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4, ensure_ascii=False)

    def register_recommendation(self, agent_id: str, rec_id: str, content: str):
        """Registers an Analyst recommendation with a unique ID."""
        if rec_id not in self.state["recommendations"]:
            self.state["recommendations"][rec_id] = {
                "origin": agent_id,
                "content": content,
                "status": "pending",
                "created_at": datetime.now().isoformat()
            }
            logger.info(f"📍 New Recommendation [{rec_id}] from {agent_id}: {content}")
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
        logger.info(f"📅 Task Scheduled: {role} -> {task_type} (ID: {task_id}, Status: {new_task['status']})")
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
                task["status"] = status
                task["updated_at"] = datetime.now().isoformat()
                logger.info(f"🔄 Task {task_id} status updated to {status}")
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
            
            # Add to a global 'to_dismiss' queue for the frontend to poll
            if "dismiss_queue" not in self.state:
                self.state["dismiss_queue"] = []
            self.state["dismiss_queue"].append(rec_id)
            
            logger.info(f"✅ Recommendation [{rec_id}] applied by {handled_by}. Queued for dismissal.")
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

# Shared Global instance
hub = AgentCollaborationHub()
