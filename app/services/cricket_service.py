import requests
from datetime import datetime
from app.config import CRICKETDATA_API_KEY, CRICKETDATA_BASE_URL
from app.logger import logger

def fetch_current_matches():
    """
    Fetch current cricket matches using CricketData API
    """
    try:
        if not CRICKETDATA_API_KEY:
            return "Cricket API key not configured. Please set CRICKETDATA_API_KEY in your .env file."
        
        url = f"{CRICKETDATA_BASE_URL}/currentMatches"
        params = {
            "apikey": CRICKETDATA_API_KEY,
            "offset": 0
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") != "success":
                return f"API Error: {data.get('status', 'Unknown error')}"
            
            matches = data.get("data", [])
            
            if not matches:
                return "No current matches found."
            
            matches_info = []
            
            for match in matches[:10]:  # Get top 10 matches
                match_type = match.get("matchType", "Unknown")
                name = match.get("name", "Unknown Match")
                status = match.get("status", "Unknown")
                venue = match.get("venue", "Unknown Venue")
                score = match.get("score", [])
                
                match_info = f"📍 Match: {name}\n"
                match_info += f"   Type: {match_type}\n"
                match_info += f"   Venue: {venue}\n"
                match_info += f"   Status: {status}\n"
                
                if score:
                    match_info += "   Scores:\n"
                    for s in score:
                        inning = s.get("inning", "")
                        runs = s.get("r", "")
                        wickets = s.get("w", "")
                        overs = s.get("o", "")
                        match_info += f"      {inning}: {runs}/{wickets} ({overs} overs)\n"
                
                matches_info.append(match_info)
            
            return "\n".join(matches_info) if matches_info else "No detailed match information available."
        
        else:
            return f"Failed to fetch current matches. Status code: {response.status_code}"
            
    except Exception as e:
        logger.error(f"Error fetching current matches: {str(e)}")
        return f"Unable to fetch current matches. Error: {str(e)}"

def fetch_matches():
    """
    Fetch all available matches (recent and upcoming) using CricketData API
    """
    try:
        if not CRICKETDATA_API_KEY:
            return "Cricket API key not configured."
        
        url = f"{CRICKETDATA_BASE_URL}/matches"
        params = {
            "apikey": CRICKETDATA_API_KEY,
            "offset": 0
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") != "success":
                return f"API Error: {data.get('status', 'Unknown error')}"
            
            matches = data.get("data", [])
            if not matches:
                return "No matches found in the general list."
            
            matches_info = []
            for match in matches[:25]:  # Get top 25 matches for broader context
                name = match.get("name", "Unknown Match")
                status = match.get("status", "Unknown")
                date = match.get("date", "Unknown Date")
                ms = match.get("ms", "N/A") # Match Status (e.g., result)
                matches_info.append(f"📅 {date}: {name} - Status: {status} ({ms})")
            
            return "\n".join(matches_info)
        
        return "Match list not available."
        
    except Exception as e:
        logger.error(f"Error fetching matches list: {str(e)}")
        return "Unable to fetch match list."

def fetch_match_info(match_id):
    """
    Fetch detailed match information by match ID
    """
    try:
        if not CRICKETDATA_API_KEY:
            return "Cricket API key not configured."
        
        url = f"{CRICKETDATA_BASE_URL}/match_info"
        params = {
            "apikey": CRICKETDATA_API_KEY,
            "id": match_id
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return str(data.get("data", {}))
        
        return "Match details not available."
        
    except Exception as e:
        logger.error(f"Error fetching match details: {str(e)}")
        return "Unable to fetch match details."

def fetch_series():
    """
    Fetch current series list using CricketData API
    """
    try:
        if not CRICKETDATA_API_KEY:
            return "Cricket API key not configured."
        
        url = f"{CRICKETDATA_BASE_URL}/series"
        params = {
            "apikey": CRICKETDATA_API_KEY,
            "offset": 0
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") != "success":
                return f"API Error: {data.get('status', 'Unknown error')}"
            
            series_list = data.get("data", [])
            if not series_list:
                return "No current series found."
            
            series_info = []
            for series in series_list[:30]:  # Increase to 30 for better tournament distinction
                name = series.get("name", "Unknown Series")
                start_date = series.get("startDate", "Unknown")
                end_date = series.get("endDate", "Unknown")
                matches = series.get("matches", "N/A")
                series_info.append(f"🏆 {name} ({start_date} to {end_date}) - {matches} matches")
            
            return "\n".join(series_info)
        
        return "Series details not available."
        
    except Exception as e:
        logger.error(f"Error fetching series details: {str(e)}")
        return "Unable to fetch series details."

def get_cricket_context():
    """
    Fetch comprehensive cricket data to provide as context to LLM
    """
    context_parts = []
    
    # Get current LIVE matches
    current_matches = fetch_current_matches()
    context_parts.append(f"=== LIVE & ACTIVE MATCHES ===\n{current_matches}")
    
    # Get broader match list (past results and future schedules)
    all_matches = fetch_matches()
    context_parts.append(f"\n=== ALL RECENT & UPCOMING MATCHES (USE FOR HISTORICAL RESULTS & FUTURE SCHEDULES) ===\n{all_matches}")
    
    # Get current series
    series_data = fetch_series()
    context_parts.append(f"\n=== CURRENT & UPCOMING SERIES / TOURNAMENTS ===\n{series_data}")
    
    # Add current date for temporal context
    today = datetime.now().strftime("%Y-%m-%d %A")
    context_parts.append(f"\n=== TODAY'S CURRENT DATE ===\n{today}")
    
    return "\n\n".join(context_parts)
