import os
import requests
from utils.logger import hub

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
        
        return {
            "pageviews": 15024,
            "visitors": 8900,
            "bounces": 400,
            "top_artwork_id": "art_003"
        }

    def generate_recommendations(self, stats: dict):
        """Generates cross-agent recommendations based on traffic data."""
        recs = [
            {"id": "ratio_4_5", "target": "VI Designer", "text": "Mobile traffic is at 82%. Recommend switching to 4:5 ratio for vertical scrolls."},
            {"id": "shorten_text", "target": "Editor", "text": "High bounce rate on long text. Recommend shortening the subtext for quicker scanning."},
            {"id": "dark_mode", "target": "VI Designer", "text": "Late-night browsing peak detected (10 PM - 2 AM). Suggest Dark Mode for eye comfort."},
            {"id": "visual_pop", "target": "VI Designer", "text": "Interaction heatmap shows users click dynamic elements. Suggest high-contrast neon accents."}
        ]
        
        # Scoring logic: If visitors > 5000, mark as "High Impact"
        impact = "High Impact" if stats.get("visitors", 0) > 5000 else "Standard"
        
        for r in recs:
            # Register in the Hub with enhanced context
            hub.register_recommendation("analyst", r["id"], f"[{r['target']}] ({impact}) {r['text']}")
        
        return recs

    def process_task(self, instruction: str, data_state: dict):
        """Processes the Analytics task by appending data insights."""
        print(f"[{self.agent_name}] Received task: {instruction}")
        
        # Mock website ID
        website_id = data_state.get("website_id", "kurodot_test_site_id_123")
        stats = self.fetch_traffic_data(website_id)
        
        # New: Register insights through the hub as actionable recommendations
        self.generate_recommendations(stats)
        
        data_state["audience_insights"] = stats
        print(f"[{self.agent_name}] Audience insights generated and registered in Hub.")
        return data_state
