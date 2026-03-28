import requests
import re
from typing import List, Dict

def get_borough_name(code: str) -> str:
    """Helper to translate borough codes into human-readable names."""
    mapping = {
        "1": "Manhattan", 
        "2": "Bronx", 
        "3": "Brooklyn", 
        "4": "Queens", 
        "5": "Staten Island"
    }
    # Sometimes it comes in as a string word already, so we default to the original.
    return mapping.get(str(code), code)

def find_nyc_communities(audience_dna: dict) -> List[Dict[str, str]]:
    """
    Takes audience DNA dictionary and hits NYC Open Data to find
    matching real-world organizations focusing primarily on the single
    identified community and their known NYC areas.
    """
    url = "https://data.cityofnewyork.us/resource/fn4k-qyk2.json"
    
    # 1. Extract and normalize multi-faceted keywords from community_themes
    themes = audience_dna.get("community_themes", [])
    theme_text = " ".join(themes).lower()
    
    # Grab meaning-rich words (4 letters or longer)
    keywords = set(re.findall(r'\b[a-z]{4,}\b', theme_text))
    # Exclude basic stop words that don't help uniquely identify communities
    stop_words = {"film", "movie", "audience", "audiences", "with", "that", "this", "from"}
    keywords = keywords - stop_words
    
    nyc_areas = [area.lower() for area in audience_dna.get("neighborhood_keywords", [])]

    # Fetch a broad sample of NYC public property / cultural spaces
    try:
        response = requests.get(url, params={"$limit": 1000})
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching from NYC Open Data: {e}")
        return []

    scored_orgs = []
    
    # Filter and Score the organizations
    for item in data:
        name = item.get("parcel_name", item.get("organization_name", "Unnamed Location"))
        address = item.get("address", item.get("street_name", "No Address Info"))
        borough_code = item.get("borough", "")
        borough_name = get_borough_name(borough_code)
        
        search_text = f"{name} {item.get('excatdesc', '')} {item.get('use_type', '')}".lower()
        location_text = f"{address.lower()} {borough_name.lower()}"
        
        score = 0
        
        # Tally organic theme correlations
        score = sum(2 for kw in keywords if kw in search_text)
            
        # Massive boost if the location intersects with specific neighborhood keywords
        if any(area in location_text for area in nyc_areas):
            score += 5
        
        # P1 Feature: Festival Radar
        # Bonus points if it's explicitly a film festival or a community art event
        if any(word in search_text for word in ['festival', 'filmfest', 'fest']):
            score += 8
        # Give a slight boost if the location is naturally cultural/communal
        if any(word in search_text for word in ['art', 'culture', 'theater', 'museum', 'community', 'center']):
            score += 1

        # Safely extract and format Map coordinates natively supplied by Socrata/NYC Open Data
        try:
            lat = float(item.get("latitude"))
            lon = float(item.get("longitude"))
        except (TypeError, ValueError):
            lat, lon = None, None

        # We keep locations that have at least some relation, or grab random valid ones if none match
        if score > 0 or len(scored_orgs) < 5:
            scored_orgs.append({
                "name": name.title(),
                "borough": borough_name.title(),
                "address": address.title(),
                "latitude": lat,
                "longitude": lon,
                "_score": score
            })
            
    # Sort by the highest score, limit to top 5
    scored_orgs.sort(key=lambda x: x["_score"], reverse=True)
    top_5 = scored_orgs[:5]
    
    # Clean up the internal _score key before returning
    for org in top_5:
        org.pop("_score", None)
        
    return top_5

if __name__ == "__main__":
    # Test the function with dummy data
    test_dna = {
        "community_themes": [
            "South Asian diaspora communities",
            "Urban drama enthusiasts",
            "Art and cultural advocacy groups"
        ],
        "neighborhood_keywords": ["Jackson Heights", "Richmond Hill"]
    }
    
    print("Finding NYC Community connections...")
    orgs = find_nyc_communities(test_dna)
    
    import json
    print(json.dumps(orgs, indent=2))
