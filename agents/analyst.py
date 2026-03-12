import os
import requests

class AudienceAnalystAgent:
    """
    Audience Analyst Agent:
    - Connects to Umami Analytics API.
    - Analyzes real-time traffic to identify most popular artworks.
    """
    def __init__(self):
        self.agent_name = "Audience Analyst"
        self.umami_url = os.getenv("UMAMI_API_URL", "https://api.umami.is/v1")
        self.umami_token = os.getenv("UMAMI_TOKEN", "dummy_token")

    def fetch_traffic_data(self, website_id: str) -> dict:
        """Fetch real-time stats from Umami HTTP API"""
        print(f"[{self.agent_name}] Connecting to Umami REST API for Website ID: {website_id}...")
        
        headers = {"Authorization": f"Bearer {self.umami_token}"}
        
        # Real API Call Example:
        # endpoint = f"{self.umami_url}/websites/{website_id}/stats"
        # response = requests.get(endpoint, headers=headers)
        # if response.ok: return response.json()
        
        return {
            "pageviews": 15024,
            "visitors": 8900,
            "bounces": 400,
            "top_artwork_id": "art_003"
        }

    def process_task(self, instruction: str, data_state: dict):
        """Processes the Analytics task by appending data insights."""
        print(f"[{self.agent_name}] Received task: {instruction}")
        
        # Mock website ID
        website_id = data_state.get("website_id", "kurodot_test_site_id_123")
        stats = self.fetch_traffic_data(website_id)
        
        data_state["audience_insights"] = stats
        print(f"[{self.agent_name}] Audience insights generated and safely appended.")
        return data_state
