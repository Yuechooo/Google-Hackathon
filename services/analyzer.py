import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel



def analyze_film(title: str, genre: str, synopsis: str, poster_image_path: str, trailer_url: str = "", director_notes: str = None) -> dict:
    """
    Analyzes a film's inputs alongside its YouTube trailer link to generate an audience DNA profile.
    Returns a Python dictionary with the parsed JSON response.
    """
    load_dotenv()
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "555759232206")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Initialize Vertex AI client
    client = genai.Client(vertexai=True, project=project_id, location=location)
    
    # Load the image
    try:
        image = Image.open(poster_image_path)
    except Exception as e:
        raise ValueError(f"Could not open image at {poster_image_path}: {e}")

    # Create the detailed prompt instructions
    prompt = f"""
    You are an expert film distributor and audience analyst focused on the NYC market. 
    Analyze the provided film poster, along with the following details and the Youtube trailer link provided:
    
    Title: {title}
    Genre: {genre}
    Synopsis: {synopsis}
    Director Notes: {director_notes if director_notes else 'Not provided'}
    Trailer: {trailer_url}
    
    Return ONLY a valid JSON object analyzing the film's Audience DNA. The JSON must exactly match this structure:
    {{
        "primary_demographics": {{
            "age_range": "string",
            "gender_split": "string",
            "interests": ["string"]
        }},
        "community_themes": ["string"],
        "neighborhood_keywords": ["string"],
        "tone": "string"
    }}
    
    - For community_themes: Provide a list of specific NYC community groups, subcultures, or ethnographic intersections this film speaks to.
    - For neighborhood_keywords: Provide demographic keywords or actual specific New York City neighborhoods where this exact organic audience resides.
    - For tone: Provide exactly one sentence describing the film's emotional register.
    """

    print(f"Sending request to Gemini for film: {title}...")
    
    # Call the API using structured outputs
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, image],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.7,
        )
    )
    
    # Parse the returned JSON string into a Python dictionary
    try:
        result_dict = json.loads(response.text)
        return result_dict
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response from Gemini: {e}")
        print("Raw response:", response.text)
        return None

if __name__ == "__main__":
    # Test execution using the poster we already have
    test_result = analyze_film(
        title="Dhurandhar",
        genre="Action / Thriller / Drama",
        synopsis="A gritty tale of power, conspiracy, and survival in the criminal underworld, testing the boundaries of loyalty and moral ambiguity.",
        poster_image_path="/Users/swatisingh/Downloads/Dhurandhar.jpg",
        trailer_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )
    
    print("\n========= AUDIENCE DNA (JSON PARSED) =========")
    print(json.dumps(test_result, indent=2))
    print("==============================================\n")
