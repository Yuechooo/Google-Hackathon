import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

def generate_discovery_story(film_title: str, audience_dna: dict, nyc_communities: list) -> str:
    """
    Takes the film's generated Audience DNA and the matched NYC community 
    organizations, and uses Gemini 2.5 Flash to synthesize a 3-paragraph 
    narrative story for the filmmaker.
    """
    load_dotenv()
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "555759232206")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Initialize Vertex AI client
    client = genai.Client(vertexai=True, project=project_id, location=location)
    
    communities_str = json.dumps(nyc_communities, indent=2)
    dna_str = json.dumps(audience_dna, indent=2)
    
    prompt = f"""
    You are an expert film distributor speaking directly to an independent filmmaker.
    Write a short, punchy 2-paragraph cinematic discovery story explaining how their film "{film_title}" 
    finds its audience in New York City.
    
    FILM AUDIENCE DNA:
    {dna_str}
    
    MATCHED NYC COMMUNITY VENUES/ORGANIZATIONS:
    {communities_str}
    
    Constraints and Requirements:
    1. The summary MUST be short and punchy. Return a JSON object with two fields: 'story' (the 2-paragraph narrative) and 'visual_prompt' (a detailed 1-sentence prompt for an AI image generator to create a vivid, cinematic scene of the NYC community described).
    2. Write in the second person ("you", "your film").
    3. You must specifically call out the provided New York City neighborhoods.
    4. You must explicitly reference the matched community organizations by name, painting a picture of a screening or audience outreach happening there.
    5. The tone should be inspirational, grounded, and practical, encouraging the filmmaker about their real-world core audience.
    """
    
    print(f"Generating discovery story and visual prompt for '{film_title}'...")
    
    # Generate the synthesized story text
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt],
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json"
        )
    )
    
    # Parse the JSON response
    result = json.loads(response.text.strip())
    return result.get("story", ""), result.get("visual_prompt", "")

if __name__ == "__main__":
    # Test data passed in manually simulating the previous outputs
    sample_dna = {
      "primary_demographics": {
        "age_range": "18-45",
        "gender_split": "Male-leaning",
        "interests": ["Crime dramas", "Action thrillers", "Gritty realism"]
      },
      "community_themes": ["Urban drama enthusiasts", "South Asian diaspora communities"],
      "neighborhood_keywords": ["Jackson Heights", "Flushing", "Lower East Side", "Bushwick"]
    }
    
    sample_orgs = [
      {"name": "Roy Wilkins Southern Queens Park", "borough": "Queens", "address": "116 Avenue"},
      {"name": "Taqwa Community Farm", "borough": "Bronx", "address": "90 West 164 Street"},
      {"name": "Urban Strategies Dcc Playground", "borough": "Brooklyn", "address": "441 Sheffield Avenue"}
    ]
    
    story = generate_discovery_story("Dhurandhar", sample_dna, sample_orgs)
    
    print("\n========= DISCOVERY STORY =========")
    print(story)
    print("===================================\n")
