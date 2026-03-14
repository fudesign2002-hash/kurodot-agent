import os
import google.generativeai as genai
from utils.logger import hub

class VIDesignerAgent:
    """
    VI Designer Agent:
    - Reads visual reference semantics.
    - Uses Imagen 3 (via Gemini API) to generate main visuals and color schemes.
    """
    def __init__(self):
        self.agent_name = "VI Designer"
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)

    def generate_visual_style(self, theme_keywords: list, exhibition_info: dict = None, audience_insights: dict = None, artwork_count: int = 0, instructions: str = "") -> dict:
        """Generate a color scheme and prompt for main visual with exhibition metadata."""
        print(f"[{self.agent_name}] Generating style based on: {theme_keywords}")
        
        # Determine ratio from instructions or default
        ratio = 0.8 if "4:5" in instructions or "portrait" in instructions.lower() else 1.77
        
        # Check if we should apply recommendations from the Hub
        if hub.check_status("visual_pop") == "pending":
            hub.mark_completed("visual_pop", self.agent_name)
            visual_prompt += " Add high-contrast neon accents for interactive focus."
            print(f"[{self.agent_name}] Applying Hub Recommendation: High-Contrast Accents")

        # Extract metadata for a richer visual prompt
        artist = exhibition_info.get("artist", "Unknown Artist") if exhibition_info else "Featured Artist"
        venue = exhibition_info.get("venue", "Gallery") if exhibition_info else "Kurodot"
        visitors = audience_insights.get("visitors", 0) if audience_insights else 0
        
        # Color Theory: Deterministic palette based on theme
        colors = {
            "modern": ["#000000", "#FFFFFF", "#FF3E00"], # Bauhaus Red
            "classic": ["#FDFBF7", "#2C3E50", "#D4AF37"], # Gold
            "digital": ["#0A0A0A", "#00F5FF", "#BC13FE"]  # Cyberpunk
        }
        theme_palette = colors.get(theme_keywords[0], ["#1A1A1A", "#F5F5F5", "#888888"])

        # Define composition based on data
        visual_prompt = (
            f"A professional gallery poster, style: {', '.join(theme_keywords)}. "
            f"Color palette: {', '.join(theme_palette)}. Artist: {artist}. "
            f"Venue: {venue}. {artwork_count} works featured."
        )
        
        if ratio < 1:
            # Portrait (e.g., 4:5)
            hub.set_layout_constraint("MAX_CHAR_COUNT", 150)
            hub.set_layout_constraint("LAYOUT_RATIO", "portrait")
            hub.set_layout_constraint("SPACING_MODEL", "compressed")
            print(f"[{self.agent_name}] Layout constraint set: MAX 150 chars, Compressed Spacing.")
        else:
            hub.set_layout_constraint("MAX_CHAR_COUNT", 250)
            hub.set_layout_constraint("LAYOUT_RATIO", "landscape")
            hub.set_layout_constraint("SPACING_MODEL", "airy")
            print(f"[{self.agent_name}] Layout constraint set: MAX 250 chars, Airy Spacing.")

        return {
            "primary_color": theme_palette[0],
            "secondary_color": theme_palette[1],
            "accent_color": theme_palette[2],
            "key_visual_prompt": visual_prompt,
            "artist_name": artist,
            "venue_name": venue,
            "artwork_count": artwork_count,
            "visitor_count": visitors,
            "layout_ratio_value": ratio,
            "status": "completed"
        }

    def process_task(self, instruction: str, data_state: dict):
        """Processes the VI task by locking down other contexts."""
        print(f"[{self.agent_name}] Received task: {instruction}")
        
        # Log event to hub
        hub.log_event("vi-designer", f"Starting visual generation for task: {instruction}")
        
        # Get exhibition and audience data from state
        exhibition_info = data_state.get("exhibition", {})
        artworks = data_state.get("artworks", [])
        artwork_count = len(artworks)
        audience_insights = data_state.get("audience_insights", {})
        
        # Example dummy execution with real data
        result = self.generate_visual_style(
            ["modern", "abstract", "digital"],
            exhibition_info=exhibition_info,
            audience_insights=audience_insights,
            artwork_count=artwork_count,
            instructions=instruction
        )
        
        # Merge visual assets to state branch without touching text
        data_state["visual_assets"] = result
        print(f"[{self.agent_name}] Visual style generated and safely appended to context state.")
        return data_state
