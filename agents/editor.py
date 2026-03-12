import os
import google.generativeai as genai

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
        
        prompt = f"""
        You are a professional art curator. Given the following data, write a short bilingual (English and Traditional Chinese) curatorial statement.
        Tone: {tone_instruction}
        Data: {raw_data}
        """
        
        # Real API Call Placeholder:
        # response = self.model.generate_content(prompt)
        # return {"zh_tw": ..., "en_us": ...}
        
        return {
            "zh_tw": "這是一個關於數位邊界的沈浸式展覽，探索人與機器的介面...",
            "en_us": "This is an immersive exhibition about digital boundaries, exploring the interface between humans and machines...",
        }

    def process_task(self, instruction: str, data_state: dict):
        """Processes the Editorial task by locking down other contexts."""
        print(f"[{self.agent_name}] Received task: {instruction}")
        
        narrative = self.generate_bilingual_narrative(data_state, instruction)
        
        # Ensure we only write to the text domain constraint
        data_state["editorial_content"] = narrative
        print(f"[{self.agent_name}] Bilingual curatorial narrative generated and safely appended.")
        return data_state
