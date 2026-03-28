import os
import json
from google import genai
from google.genai import types

def generate_marketing_strategies(film_title, audience_dna, nyc_communities):
    """
    Acts as a fractional CMO using Gemini to design localized, actionable go-to-market strategies 
    and a 6-month projected revenue timeline for an independent film based on its audience DNA and target venues.
    """
    try:
        # Initialize the Vertex AI Gemini client
        client = genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", "cinemamatch"),
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        )

        communities_str = ", ".join([org['name'] for org in nyc_communities]) if nyc_communities else "General NYC venues"
        dna_str = json.dumps(audience_dna, indent=2)

        prompt = f"""
        You are an expert film distributor and Chief Marketing Officer (CMO) for an independent production studio.
        Based on the following Audience DNA and specific NYC target venues, develop 2 to 3 highly targeted, actionable marketing campaigns geared specifically towards independent filmmakers aiming to launch this title. Focus on guerrilla, digital, and localized physical execution inside New York City.
        
        FILM TITLE: "{film_title}"
        AUDIENCE DNA: 
        {dna_str}
        
        TARGET NYC VENUES: 
        {communities_str}
        
        Return EXACTLY a valid JSON object matching this schema. NO markdown wrapping, no ```json tags, just the raw JSON:
        {{
          "campaigns": [
            {{
              "title": "Campaign Name",
              "description": "Short, punchy 1-2 sentence description.",
              "execution_steps": ["Step 1", "Step 2", "Step 3"],
              "estimated_cost_usd": 500
            }}
          ],
          "revenue_timeline": [
            {{"month": "Month 1", "revenue": 1200}},
            {{"month": "Month 2", "revenue": 2500}},
            {{"month": "Month 3", "revenue": 3800}},
            {{"month": "Month 4", "revenue": 5000}},
            {{"month": "Month 5", "revenue": 7500}},
            {{"month": "Month 6", "revenue": 9000}}
          ],
          "demographic_engagement": [
            {{"age_group": "18-24", "engagement_score": 85}},
            {{"age_group": "25-34", "engagement_score": 92}},
            {{"age_group": "35-44", "engagement_score": 60}},
            {{"age_group": "45-54", "engagement_score": 30}},
            {{"age_group": "55+", "engagement_score": 15}}
          ],
          "budget_breakdown": [
            {{"category": "Social Media Ads", "percentage": 40}},
            {{"category": "Influencer Partnerships", "percentage": 25}},
            {{"category": "Physical Activations", "percentage": 20}},
            {{"category": "Print/PR", "percentage": 15}}
          ]
        }}
        """

        print(f"Sending request to Gemini for marketing strategies: {film_title}...")
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt],
            config=types.GenerateContentConfig(
                temperature=0.7,
                response_mime_type="application/json"
            )
        )
        
        # Clean the response to ensure it's valid JSON
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        return json.loads(result_text)

    except Exception as e:
        print(f"Error generating marketing strategies: {e}")
        return None

if __name__ == "__main__":
    # Test execution
    test_dna = {"tone": "Suspense", "community_themes": ["Thriller fans", "Indie film aficionados"]}
    test_orgs = [{"name": "Angelika Film Center"}, {"name": "IFC Center"}]
    print(generate_marketing_strategies("The Last Heist", test_dna, test_orgs))
