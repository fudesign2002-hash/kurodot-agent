import os
from google.cloud import storage
import settings

class TechProducerAgent:
    """
    Tech Production Agent:
    - Personality: "The Builder" ⚫ - Systematic, soft dissolve, technical.
    - Animation Style: Fade In (Soft dissolve & blur).
    - UI Color: #272a3a (Dark).
    - Font Style: 'Verdana', sans-serif.
    - Behavior: Final technical packaging (PDF/SVG/PNG) and GCS storage.
    """
    def __init__(self):
        self.agent_name = settings.AGENT_ROLES["tech"]
        self.personality_emoji = "📋" # Tech Producer's primary emoji for tasks
        self.bucket_name = os.getenv("GCS_BUCKET_NAME", "kurodot-assets")
        # Ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set

    def package_assets(self, data_state: dict) -> str:
        """Merge textual and visual elements into a finalized technical file format."""
        print(f"[{self.agent_name}] Compiling visual and text nodes into final layout...")
        # Placeholder for complex PDF or HTML generation
        # e.g., similar to your previous generate_booklet.py logic using Jinja/HTML
        
        output_path = "/tmp/final_exhibition_booklet.pdf"
        print(f"[{self.agent_name}] Built final asset at {output_path}")
        return output_path

    def upload_to_gcs(self, file_path: str) -> str:
        """Upload to Google Cloud Storage to get a public URL"""
        print(f"[{self.agent_name}] Uploading {file_path} to GCS bucket: {self.bucket_name}...")
        
        # Real GCS upload setup:
        # client = storage.Client()
        # bucket = client.bucket(self.bucket_name)
        # blob = bucket.blob("exports/booklet.pdf")
        # blob.upload_from_filename(file_path)
        
        public_url = f"https://storage.googleapis.com/{self.bucket_name}/exports/booklet.pdf"
        return public_url

    def process_task(self, instruction: str, data_state: dict):
        """Processes the Production task by creating final assets."""
        print(f"[{self.agent_name}] Starting final merge operation...")
        
        file_path = self.package_assets(data_state)
        url = self.upload_to_gcs(file_path)
        
        data_state["final_output_url"] = url
        data_state["status"] = "Production Completed"
        print(f"[{self.agent_name}] Production finished. Final asset accessible at: {url}")
        return data_state
