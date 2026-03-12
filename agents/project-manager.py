import re
import pyrebase
from firebase_admin import credentials, initialize_app, firestore
import os

class ProjectManagerAgent:
    """
    Project Manager (PM) Agent:
    - Parses kurodot.io URLs to extract exhibition IDs.
    - Connects to Firebase to retrieve raw exhibition JSON data.
    - Prepares the data state for downstream orchestration.
    """
    def __init__(self):
        # Initialize Firebase (placeholder configuration)
        # credentials_path = os.getenv("FIREBASE_CREDENTIALS", "path/to/firebase-key.json")
        # if not firebase_admin._apps:
        #     cred = credentials.Certificate(credentials_path)
        #     initialize_app(cred)
        # self.db = firestore.client()
        self.agent_name = "Project Manager"

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
        print(f"[{self.agent_name}] Processing Start (URL: {instruction_or_url})")
        exhibition_id = self.extract_id_from_url(instruction_or_url)
        data = self.fetch_exhibition_data(exhibition_id)
        print(f"[{self.agent_name}] Task Handled. Data State initialised.")
        return data

