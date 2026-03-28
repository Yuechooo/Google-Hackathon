import os
import sys
from dotenv import load_dotenv
from google import genai
from PIL import Image

def analyze_film_poster(image_path):
    # Load environment variables
    load_dotenv()
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "555759232206")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    try:
        # Initialize Vertex AI client
        client = genai.Client(vertexai=True, project=project_id, location=location)
        
        print(f"Loading image from: {image_path}")
        image = Image.open(image_path)
        
        prompt = "Describe the mood, themes, and likely audience of this film based on the poster"
        
        print("Sending request to Gemini Vision API (gemini-2.5-flash)...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, image]
        )
        
        print("\n" + "="*50)
        print("🎬 GEMINI POSTER ANALYSIS RESULTS")
        print("="*50 + "\n")
        print(response.text)
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"Error during API call or image processing: {e}")

if __name__ == "__main__":
    # If a path was provided as an argument, use it. Otherwise default to 'poster.jpg'
    poster_path = sys.argv[1] if len(sys.argv) > 1 else "poster.jpg"
    
    if not os.path.exists(poster_path):
        print(f"Error: Could not find image at '{poster_path}'")
        print("Please provide the path to your poster image as an argument:")
        print("Example: python analyze_poster.py /path/to/your/image.jpg")
    else:
        analyze_film_poster(poster_path)
