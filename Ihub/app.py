import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig

# Import both schemas
from models.route_schema import RouteAnalysis, ClassifiedRequirement # Your final output schema
from models.input_schema import RouteInput                         # Your new input parsing schema

# Load environment variables
load_dotenv()

def get_gemini_client():
    """Initializes and returns the Gemini client."""
    try:
        return genai.Client()
    except Exception as e:
        raise ConnectionError(f"Error initializing Gemini client: {e}. Check your GEMINI_API_KEY.")


def robustly_parse_input(client: genai.Client, user_input_line: str) -> RouteInput:
    """
    Uses Gemini's structured output capability to extract locations and requirements 
    from any natural language input.
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
        response_schema=RouteInput, # <-- Using the INPUT schema here
        temperature=0.0
    )

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=config,
    )
    
    # The SDK parses the JSON response directly into a Pydantic object
    return response.parsed


def generate_route_analysis(client: genai.Client, route_input: RouteInput):
    """
    Generates the final classified route analysis using the cleaned-up input.
    """
    
    # Unpack the cleaned-up input
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
        response_schema=RouteAnalysis, # <-- Using the FINAL OUTPUT schema here
        temperature=0.0
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt,
            config=config,
        )
        return response.parsed
    except Exception as e:
        return f"Gemini API Error during analysis: {e}"

# --- Main Execution (The Only Part You Need to Change) ---
if __name__ == "__main__":
    
    try:
        # 🚨 THE NEW LINE: PROMPT THE USER FOR INPUT
        user_input_line = input("Enter your route request (e.g., 'From NYC to LA, I want hotels and greenery'):\n> ")
        
        client = get_gemini_client()

        print(f"\n--- 1. Parsing User Input ---")
        
        # Step 1: Robustly parse the input
        route_input = robustly_parse_input(client, user_input_line)
        
        print("\n✅ Extracted Input:")
        print(f"   Origin: {route_input.current_location}")
        print(f"   Dest.:  {route_input.destination}")
        print(f"   Reqs:   {', '.join(route_input.requirements)}\n")

        print("--- 2. Generating Route Analysis ---")
        
        # Step 2: Generate the final analysis
        analysis_result = generate_route_analysis(client, route_input)

        # 3. Process and Display Output
        if isinstance(analysis_result, RouteAnalysis):
            print("\n✅ Final Structured Route Analysis (JSON):")
            print(analysis_result.model_dump_json(indent=2))
            
        else:
            print(f"\n❌ Analysis Error: {analysis_result}")
            
    except (ConnectionError, Exception) as e:
        print(f"\n❌ Fatal Error: {e}")