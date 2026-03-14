import os
import google.generativeai as genai
from utils.logger import hub

class EditorialSpecialistAgent:
    """
    Editorial Specialist Agent:
    - Transforms JSON data into smooth curatorial statements.
    - Provides high-quality bilingual (EN/ZH) translations via Gemini.
    """
    def __init__(self):
        self.agent_name = "Editorial Specialist"
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    def generate_bilingual_narrative(self, raw_data: dict, tone_instruction: str) -> dict:
        """Calls Gemini to expand raw string data into a beautifully written curatorial."""
        print(f"[{self.agent_name}] Drafting narrative with tone: {tone_instruction}")
        
        # Check if we should apply recommendations from the Hub
        if hub.check_status("shorten_text") == "pending":
            hub.mark_completed("shorten_text", self.agent_name)
            tone_instruction += " (STRICT CONSTRAINT: Shorten text by 30% for high engagement)"
            print(f"[{self.agent_name}] Applying Hub Recommendation: Shorten Text")

        # Check for layout constraints from Designer
        max_chars = hub.get_constraint("MAX_CHAR_COUNT")
        if max_chars:
            tone_instruction += f" (STRICT LENGTH: Under {max_chars} characters total. Fit the {hub.get_constraint('LAYOUT_RATIO')} layout.)"
            print(f"[{self.agent_name}] Applying Layout Constraint: Max {max_chars} chars.")

        artist_name = raw_data.get("exhibition", {}).get("artist", "Featured Artist")
        
        prompt = f"""
        You are a professional art curator. Given the following data, write a short bilingual (English and Traditional Chinese) curatorial statement.
        
        CRITICAL CONSTRAINTS (non-negotiable):
        1. NEVER translate, romanize, or alter any artist name. The artist name "{artist_name}" must appear EXACTLY as-is in ALL languages.
        2. This applies to ALL people's names in the data — keep every name in its original form.
        3. Ensure the tone is {tone_instruction}.
        
        Data: {raw_data}
        """
        
        # Real API Call Placeholder:
        # response = self.model.generate_content(prompt)
        # return {"zh_tw": ..., "en_us": ...}
        
        return {
            "zh_tw": f"這是一個展現 {artist_name} 藝術遠見的沈浸式展覽，探索人與機器的介面...",
            "en_us": f"This is an immersive exhibition showcasing the artistic vision of {artist_name}, exploring the interface between humans and machines...",
        }

    def process_task(self, instruction: str, data_state: dict):
        """Processes the Editorial task by locking down other contexts."""
        print(f"[{self.agent_name}] Received task: {instruction}")
        
        narrative = self.generate_bilingual_narrative(data_state, instruction)
        
        # Ensure we only write to the text domain constraint
        data_state["editorial_content"] = narrative
        print(f"[{self.agent_name}] Bilingual curatorial narrative generated and safely appended.")
        return data_state
