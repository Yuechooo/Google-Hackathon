import os
import json
import subprocess
from dotenv import load_dotenv
from google import genai
from google.genai import types
from gtts import gTTS
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

def generate_marketing_video(film_title: str, audience_dna: dict, nyc_communities: list) -> str:
    """
    Final Pipeline:
    1. Gemini: Generates a 12-second hype script and Imagen visual prompt.
    2. Imagen: Generates a professional 8k cinematic marketing poster.
    3. gTTS: Synthesizes the hype script into audio.
    4. FFmpeg: Merges the still image and audio into a high-quality MP4 video.
    Returns the path to the generated marketing_ad.mp4.
    """
    load_dotenv()
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "cinemamatch")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Initialize Clients
    client = genai.Client(vertexai=True, project=project_id, location=location)
    vertexai.init(project=project_id, location=location)
    
    # 1. Generate Ad Script and Visual Prompt
    dna_str = json.dumps(audience_dna, indent=2)
    prompt = f"""
    You are a high-energy cinematic trailer scriptwriter. 
    Write a 12-second marketing pitch for the film "{film_title}" targeting its Audience DNA: {dna_str}.
    
    Return a JSON object with:
    - 'script': The 12-second hype pitch for an AI narrator.
    - 'visual_prompt': A detailed 8k cinematic prompt for Imagen 3 to create a stunning movie marketing poster with dramatic vibes.
    """
    
    print("Generating marketing script and visual prompt...")
    resp = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt],
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    data = json.loads(resp.text)
    script = data.get("script", "")
    visual_prompt = data.get("visual_prompt", "")
    
    # 2. Generate Cinematic Image using Vertex AI Imagen
    print(f"Generating cinematic visual: {visual_prompt[:50]}...")
    image_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
    images = image_model.generate_images(
        prompt=visual_prompt,
        number_of_images=1,
        language="en",
        aspect_ratio="1:1"
    )
    
    output_dir = "assets"
    os.makedirs(output_dir, exist_ok=True)
    img_path = os.path.join(output_dir, "marketing_poster.png")
    images[0].save(location=img_path, include_generation_parameters=False)
    
    # 3. Generate Audio Narrative using gTTS
    print("Generating marketing voiceover...")
    audio_path = os.path.join(output_dir, "marketing_audio.mp3")
    tts = gTTS(text=script, lang='en')
    tts.save(audio_path)
    
    # 4. Stitch Video with FFmpeg
    print("Stitching AI assets into final MP4 video...")
    video_path = os.path.join(output_dir, "marketing_ad.mp4")
    # Using ffmpeg to loop the static image for the duration of the audio
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", img_path,
        "-i", audio_path,
        "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p", "-shortest",
        video_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    
    return video_path

if __name__ == "__main__":
    # Test data
    sample_dna = {"tone": "Gritty NYC Action", "themes": ["Underworld", "Mystery"]}
    video = generate_marketing_video("Dhurandhar", sample_dna, [])
    print(f"Success! Video generated at: {video}")
