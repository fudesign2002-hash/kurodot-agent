# Configuration for the agent environment
# Set TESTING_MODE = 1 to automatically spawn a test note on startup
# Set TESTING_MODE = 0 for production/manual mode

TESTING_MODE = 1
TEST_URL = "https://app.kurodot.io/exhibition/bauhaus-blueprint-qevdv"
TEST_INSTRUCTION = "Create a 3:2 banner from this exhibition"

# UI Background
# Set SHOW_BACKGROUND = 1 for the dot-grid background (default)
# Set SHOW_BACKGROUND = 0 for a clean white background (good for screen recordings)
SHOW_BACKGROUND = 1

# Agent Constants
AGENT_ROLES = {
    "pm": "Project Manager",
    "designer": "VI Designer",
    "editor": "Editor",
    "analyst": "Data Analyst",
    "tech": "Tech Producer"
}
