import os
from google import genai
from google.genai import types
from utils.logger import hub
import settings

class VIDesignerAgent:
    """
    VI Designer Agent:
    - Personality: "The Muse" 🔴 - Creative, elegant, visual-focused.
    - Animation Style: Fly-In (Elegant Glide & Blur reveal).
    - UI Color: #ce538a (Pink).
    - Font Style: 'Georgia', serif, italic.
    - CRITICAL RULE: Designer manages layout, ratios, and visual styling. NEVER modifies text.
    """
    def __init__(self):
        self.agent_name = settings.AGENT_ROLES["designer"]
        self.personality_emoji = "🎨" # VI Designer's primary emoji for creative tasks
        # Configure Gemini API (google-genai SDK)
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None

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
        """Processes the VI task by using Editorial text to inform layout."""
        # Use a unique log_id for this specific task iteration to prevent double-bubbling
        task_id = f"vi_task_{data_state.get('id', 'default')}_{instruction[:15]}"
        hub.emit_log("vi-designer", f"Starting visual generation for task: {instruction}", status="start", log_id=task_id)
        print(f"[{self.agent_name}] Received task: {instruction}")
        
        # Collaborative Rule: Designer depends on Editorial content from the state
        # instead of reading raw 'overview' from data.
        editor_curatorial = data_state.get("editorial_content", {}).get("en_us", "")
        if editor_curatorial:
            print(f"[{self.agent_name}] Layout inspired by curated text: {editor_curatorial[:60]}...")
        
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
        hub.emit_log("vi-designer", "Visual style generated and safely appended to context state. Love this palette! ❤️", status="complete", log_id=f"{task_id}_done")
        print(f"[{self.agent_name}] Visual style generated and safely appended to context state.")
        return data_state

    def analyze_style(self, image_base64: str, mime_type: str = "image/png") -> dict:
        """Analyzes the visual style of a reference image using Gemini Vision."""
        import base64, json
        if not self.client:
            raise RuntimeError("GEMINI_API_KEY not configured")

        prompt = """You are a professional visual designer. Analyze the visual style of this image and return a JSON object describing the design language so it can be replicated on an art gallery banner.

Return ONLY valid JSON with these exact keys:
{
  \"color_scheme\": \"dark\" | \"light\" | \"vibrant\" | \"monochrome\" | \"pastel\" | \"gradient\",
  \"primary_color\": \"#rrggbb\",
  \"secondary_color\": \"#rrggbb\",
  \"accent_color\": \"#rrggbb\",
  \"background_style\": \"solid\" | \"gradient\" | \"full_image\" | \"textured\",
  \"typography_style\": \"serif\" | \"sans-serif\" | \"display\" | \"minimal\" | \"slab\" | \"monospace\",
  \"layout\": \"centered\" | \"left-aligned\" | \"right-aligned\" | \"split\",
  \"mood\": \"elegant\" | \"bold\" | \"minimalist\" | \"retro\" | \"futuristic\" | \"organic\" | \"editorial\" | \"dramatic\",
  \"font_weight\": \"thin\" | \"regular\" | \"bold\" | \"heavy\",
  \"description\": \"one sentence describing the overall style for the designer agent\",
  \"image_shape\": \"circle\" | \"rectangle\",
  \"decorative_elements\": [
    {
      \"type\": \"star\" | \"circle\" | \"triangle\" | \"rectangle\" | \"dot-grid\" | \"cross\" | \"burst\" | \"zigzag\" | \"arc\" | \"diamond\",
      \"color\": \"#rrggbb\",
      \"opacity\": 0.0-1.0,
      \"size\": \"small\" | \"medium\" | \"large\",
      \"placement\": \"corner\" | \"edge\" | \"scattered\"
    }
  ]
}

For decorative_elements: identify 3-6 recurring geometric/vector decorative motifs visible in the image — things like colored star bursts, dot grids, geometric shapes, corner accents, stripes, or pattern fills. These will be rendered as SVG overlays on the banner to recreate the visual feel of the reference.

Important rules:
- If the background has two or more colors blending (gradient), set background_style to \"gradient\" and color_scheme to \"vibrant\" or \"gradient\"
- Set primary_color to the dominant background color, secondary_color to the second gradient color, accent_color to the most prominent text/highlight color
- If the layout has text on the left side and imagery on the right, use \"left-aligned\"
- If the layout has centered text stacked vertically, use \"centered\"
- Set image_shape to "circle" if the reference uses a circular crop or circular frame for its main photo; otherwise use "rectangle"
- Prioritize capturing the most distinctive visual trait in mood"""

        image_bytes = base64.b64decode(image_base64)
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt
            ]
        )
        raw = response.text.strip()
        print(f"[{self.agent_name}] Style analysis response: {raw[:120]}...")
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())

    def generate_interleaved_story(self, exhibition_info: str) -> dict:
        """
        Creative Storyteller: Generates a mixed curatorial narrative + key visual
        using Gemini interleaved multimodal output (text + image in one response).
        This satisfies the hackathon's Creative Storyteller mandatory tech requirement.
        """
        if not self.client:
            return {"text_parts": ["[Gemini API key not configured]"], "image_data": []}

        prompt = (
            f"You are a creative director for an art exhibition described as: {exhibition_info}. "
            "Generate a short atmospheric curatorial introduction (2-3 sentences), "
            "then generate a key visual image for the exhibition banner. "
            "The image should feel like a professional gallery poster: elegant, modern, high contrast."
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"]
                )
            )
            result = {"text_parts": [], "image_data": []}
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text") and part.text:
                    result["text_parts"].append(part.text)
                elif hasattr(part, "inline_data") and part.inline_data:
                    raw = part.inline_data.data
                    # SDK may return bytes or already-base64 str
                    if isinstance(raw, bytes):
                        import base64
                        raw = base64.b64encode(raw).decode("utf-8")
                    result["image_data"].append(raw)
            hub.emit_log(
                "vi-designer",
                f"Interleaved story generated: {len(result['text_parts'])} text + {len(result['image_data'])} image parts.",
                status="complete", log_id=f"interleaved_{exhibition_info[:20]}"
            )
            return result
        except Exception as e:
            hub.emit_log("vi-designer", f"Interleaved generation failed: {e}", status="complete")
            return {"text_parts": [], "image_data": [], "error": str(e)}
