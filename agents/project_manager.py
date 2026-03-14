import re
import pyrebase
from firebase_admin import credentials, initialize_app, firestore
import os
import settings

class ProjectManagerAgent:
    """
    Project Manager (PM) Agent:
    - Personality: "The Hype" 🟠 - High energy, orchestrates the workflow.
    - Animation Style: Bouncy / Floating (Keynote-style energetic bounce).
    - UI Color: #f1a456 (Orange).
    - Behavior: Parses URLs, dispatches tasks, and celebrates success.
    """
    def __init__(self):
        # Initialize Firebase (placeholder configuration)
        # credentials_path = os.getenv("FIREBASE_CREDENTIALS", "path/to/firebase-key.json")
        # if not firebase_admin._apps:
        #     cred = credentials.Certificate(credentials_path)
        #     initialize_app(cred)
        self.agent_name = settings.AGENT_ROLES["pm"]
        self.personality_emoji = "👍" # Project Manager strictly uses gestures

    def extract_id_from_url(self, url: str) -> str:
        """Extract ID from URLs like https://kurodot.io/exhibition/12345"""
        match = re.search(r'exhibition/([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(1)
        raise ValueError("Invalid Kurodot URL provided.")

    def fetch_exhibition_data(self, exhibition_id: str) -> dict:
        """Fetch raw JSON from Firebase"""
        print(f"[{self.agent_name}] Fetching data from Firebase for ID: {exhibition_id}...")
        
        # --- Real Firebase API Call placeholder ---
        # doc_ref = self.db.collection("exhibitions").document(exhibition_id)
        # doc = doc_ref.get()
        # if doc.exists:
        #     return doc.to_dict()
        # ------------------------------------------

        # Simulated response for now
        return {
            "id": exhibition_id,
            "title": "Default Exhibition",
            "curator": "Chief Curator",
            "artworks": []
        }

    def process_task(self, instruction_or_url: str):
        from utils.logger import hub
        hub.emit_log("pm", f"Orchestrating Curation Workflow (URL: {instruction_or_url})", status="start")
        print(f"[{self.agent_name}] Orchestrating Curation Workflow (URL: {instruction_or_url})")
        
        # Proactive: Determine if we need to fetch data or if this is a design tweak
        is_url = "http" in instruction_or_url
        
        if is_url:
            exhibition_id = self.extract_id_from_url(instruction_or_url)
            data = self.fetch_exhibition_data(exhibition_id)
            hub.emit_log("pm", f"Data retrieval complete for {exhibition_id}. Love the progress! ❤️", status="complete")
            print(f"[{self.agent_name}] Data retrieval complete. Notifying Analyst and VI Designer.")
            return {
                "action": "full_curation",
                "data": data,
                "next_agent": "analyst",
                "priority": "high"
            }
        else:
            print(f"[{self.agent_name}] Interpret instruction as a design modification.")
            return {
                "action": "tweak",
                "instruction": instruction_or_url,
                "next_agent": "vi-designer",
                "priority": "medium"
            }

