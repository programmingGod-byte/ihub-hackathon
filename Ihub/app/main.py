from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig
from models.input_schema import RouteInput
from models.route_schema import RouteAnalysis
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Route Analyzer API", version="1.0.0")

# --- Helper functions ---
class UserRequest(BaseModel):
    text: str  # single-line input

def get_gemini_client():
    """
    Initializes the Gemini client with API key from .env
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY missing in .env")
        return genai.Client(api_key=api_key)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing Gemini client: {e}"
        )


def robustly_parse_input(client: genai.Client, user_input_line: str) -> RouteInput:
    """
    Uses Gemini to extract locations and requirements from any natural language input.
    """
    system_instruction = (
        "You are a sophisticated text extractor. Your sole job is to read the user's "
        "natural language travel request and extract the current location, the destination, "
        "and a clean list of all desired path requirements. The output MUST strictly "
        "adhere to the provided JSON schema. If a requirement is not clearly defined, use the user's exact phrase."
    )
    
    prompt = f"The user wants to travel. Please extract the required information from this text: '{user_input_line}'"
    
    config = GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=RouteInput,
        temperature=0.0
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=config,
    )
    return response.parsed


def generate_route_analysis(client: genai.Client, route_input: RouteInput):
    current_loc = route_input.current_location
    destination = route_input.destination
    requirements = route_input.requirements
    
    requirements_str = ", ".join(requirements)
    
    # In app.py, inside the generate_route_analysis function:

    # In app.py, inside the generate_route_analysis function:

    system_instruction = """
    You are an intelligent route classification assistant. 
    Your job is to interpret a user's natural-language travel request 
    and return a structured JSON response describing:
    - the origin
    - the destination
    - a list of classified requirements

    Each requirement must include:
    - "name": the user’s exact phrase (e.g., "bird watching", "wheelchair accessible")
    - "classified_concept": a standardized concept label from the predefined list
    - "difficulty": how challenging it is to satisfy that request along a typical route ("easy" / "medium" / "hard")

    ---

    ## 🔍 Classification Guide

    You must classify each requirement into **one of the following 15 standardized concept categories**.  
    If something does not match exactly, choose the **closest practical category**.

    | Category | Example Phrases |
    |-----------|----------------|
    | **Greenery ** | greenery, forests, trees, parks, bird watching, wildlife, botanical gardens, lakes, rivers, mountains, nature photography |
    | **Greenery** | scenic route, beautiful views, photography, sunsets, coastal drives, sightseeing, mountain passes |
    | **Accessibility & Inclusivity** | wheelchair accessible, elderly friendly, gender-neutral rest stops, step-free paths, disabled access |
    | **Cultural & Local Life** | traditional markets, local cuisine, street food, cultural festivals, local art, community events |
    | **Lodging & Rest Stops** | hotels, rest houses, clean restrooms, budget stays, hostels, motels, resorts |
    | **Adventure & Sports** | trekking, camping, hiking, biking, rafting, kayaking, paragliding, rock climbing |
    | **Historical & Heritage** | monuments, forts, temples, museums, palaces, heritage walks, UNESCO sites |
    | **Safety & Security** | safe roads, low traffic, street lighting, police presence, emergency services |
    | **Technology & Connectivity** | good mobile network, EV charging, WiFi hotspots, GPS coverage |
    | **Environment & Cleanliness** | eco-friendly, clean air, plastic-free, sustainable route, low pollution |
    | **Health & Wellness** | meditation centers, hospitals nearby, calm routes, yoga retreats, pharmacies |
    | **Food & Refreshments** | restaurants, cafes, dhabas, tea stalls, snack bars, vegetarian food options |
    | **Cost & Budget Efficiency** | avoid tolls, cheap route, low fuel consumption, budget-friendly travel |
    | **Family & Pet Friendly** | pet stops, playgrounds, baby rest zones, picnic areas, family rest zones |
    | **Maintenance & Road Quality** | smooth roads, new highways, proper signage, no potholes, well-maintained lanes |

    If a user request implies multiple ideas (e.g., “quiet nature trails”), 
    split it into multiple requirements and classify each separately.

    ---

    ## ⚙️ Output Rules

    - Always output **valid JSON** matching the given schema.
    - Every requirement must include all three fields: `"name"`, `"classified_concept"`, and `"difficulty"`.
    - `"classified_concept"` must be one of the 15 categories above.
    - `"difficulty"` must be `"easy"`, `"medium"`, or `"hard"`.
    - `"name"` must exactly preserve the user’s wording.
    - Do not include extra commentary, text, or fields beyond the JSON.

    ---

    ## 💡 Example Input
    "Can you give me the best route from Kolkata to Hyderabad? My main hobby is bird watching, so if there are any natural parks or scenic reserves on the way, I would love that. Also, the route must be wheelchair accessible."

    ## ✅ Example Output
    {
    "current_location": "Kolkata",
    "destination": "Hyderabad",
    "classified_requirements": [
        {
        "name": "bird watching",
        "classified_concept": "Greenery & Nature",
        "difficulty": "medium"
        },
        {
        "name": "natural parks",
        "classified_concept": "Greenery & Nature",
        "difficulty": "medium"
        },
        {
        "name": "scenic reserves",
        "classified_concept": "Scenic & Aesthetic Routes",
        "difficulty": "medium"
        },
        {
        "name": "wheelchair accessible",
        "classified_concept": "Accessibility & Inclusivity",
        "difficulty": "hard"
        }
    ]
    }
    """

    
    # ... rest of the function remains the same
    prompt = f"""
    The user is traveling from **{current_loc}** to **{destination}**.
    
    The user's desired path requirements are: **{requirements_str}**.
    
    Please provide the structured analysis.
    """
    config = GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=RouteAnalysis,
        temperature=0.0
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=config,
    )
    return response.parsed

# --- API Routes ---
@app.post("/analyze", response_model=RouteAnalysis)
async def analyze_route(request: UserRequest):
    """
    Analyze a user's route request from a single-line text input.
    """
    try:
        client = get_gemini_client()
        parsed_input = robustly_parse_input(client, request.text)
        analysis = generate_route_analysis(client, parsed_input)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.get("/")
def home():
    return {"message": "Route Analyzer API is running 🚀"}


