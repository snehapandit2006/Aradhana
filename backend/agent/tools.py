import os
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from flatlib import aspects

# Import RAG retriever helper
from rag.retriever import retrieve

GOOGLE_API_KEY = os.getenv("GOOGLE_GEOCODING_API_KEY")

def geocode_place(place_name: str) -> dict:
    """
    Geocodes a place name using Google Geocoding API and retrieves its timezone offset using Google Timezone API.
    Returns: { 'lat': float, 'lon': float, 'timezone_offset': str, 'formatted_address': str }
    """
    if not GOOGLE_API_KEY or GOOGLE_API_KEY.strip() == "" or GOOGLE_API_KEY == "your_google_api_key_here":
        print(f"Warning: GOOGLE_GEOCODING_API_KEY is not set. Using fallback coordinates for '{place_name}'.")
        if "mumbai" in place_name.lower():
            return {
                "lat": 19.0760,
                "lon": 72.8770,
                "timezone_offset": "+05:30",
                "timezone_offset_hours": 5.5,
                "formatted_address": "Mumbai, Maharashtra, India"
            }
        return {
            "lat": 28.6139,
            "lon": 77.2090,
            "timezone_offset": "+05:30",
            "timezone_offset_hours": 5.5,
            "formatted_address": "New Delhi, Delhi, India"
        }

    # 1. Get Lat/Lon
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    geo_params = {"address": place_name, "key": GOOGLE_API_KEY}
    
    try:
        response = requests.get(geocode_url, params=geo_params, timeout=10)
        res_json = response.json()
    except Exception as e:
        raise ValueError(f"Failed to connect to Google Geocoding API: {e}")

    if res_json.get("status") != "OK" or not res_json.get("results"):
        raise ValueError(f"Geocoding failed for '{place_name}': {res_json.get('status', 'Unknown error')}")

    result = res_json["results"][0]
    lat = result["geometry"]["location"]["lat"]
    lon = result["geometry"]["location"]["lng"]
    formatted_address = result["formatted_address"]

    # 2. Get Timezone Offset
    timezone_url = "https://maps.googleapis.com/maps/api/timezone/json"
    now_ts = int(datetime.utcnow().timestamp())
    tz_params = {"location": f"{lat},{lon}", "timestamp": now_ts, "key": GOOGLE_API_KEY}

    try:
        tz_response = requests.get(timezone_url, params=tz_params, timeout=10)
        tz_json = tz_response.json()
    except Exception as e:
        raise ValueError(f"Failed to connect to Google Timezone API: {e}")

    if tz_json.get("status") != "OK":
        raise ValueError(f"Timezone resolution failed: {tz_json.get('status', 'Unknown error')}")

    raw_offset = tz_json.get("rawOffset", 0)
    dst_offset = tz_json.get("dstOffset", 0)
    total_offset_seconds = raw_offset + dst_offset

    # Convert total offset to +/-HH:MM string format
    sign = "+" if total_offset_seconds >= 0 else "-"
    abs_seconds = abs(total_offset_seconds)
    hours = int(abs_seconds // 3600)
    minutes = int((abs_seconds % 3600) // 60)
    offset_str = f"{sign}{hours:02d}:{minutes:02d}"
    offset_hours = total_offset_seconds / 3600.0

    return {
        "lat": lat,
        "lon": lon,
        "timezone_offset": offset_str,
        "timezone_offset_hours": offset_hours,
        "formatted_address": formatted_address
    }

def find_planet_house(chart: Chart, planet_obj) -> int:
    """
    Robust helper to identify which house a planet is in.
    First tries flatlib's built-in inHouse boundary checks.
    Falls back to a manual cusp longitude-range comparison.
    """
    for i in range(1, 13):
        h = chart.get(f"House{i}")
        if h.inHouse(planet_obj):
            return i
            
    # Fallback range calculation (especially for edge crossings at 0/360 degrees)
    p_lon = planet_obj.lon
    cusps = [chart.get(f"House{i}").lon for i in range(1, 13)]
    for i in range(12):
        c1 = cusps[i]
        c2 = cusps[(i + 1) % 12]
        if c1 <= c2:
            if c1 <= p_lon < c2:
                return i + 1
        else: # Crosses Aries point (0 degrees)
            if p_lon >= c1 or p_lon < c2:
                return i + 1
                
    return 1  # Default fallback if boundary checks mismatch

def compute_birth_chart(date: str, time: Optional[str], place: str, time_unknown: bool = False) -> dict:
    """
    Computes birth chart planetary positions and houses using flatlib.
    date: YYYY-MM-DD
    time: HH:MM
    place: City/Town name
    """
    # Resolve place to lat, lon, timezone
    geo_data = geocode_place(place)
    lat = geo_data["lat"]
    lon = geo_data["lon"]
    offset_hours = geo_data["timezone_offset_hours"]
    offset_str = geo_data["timezone_offset"]
    
    # Handle unknown birth time by defaulting to noon
    time_str = "12:00" if (time_unknown or not time) else time
    
    # Format date to flatlib expected YYYY/MM/DD
    date_formatted = date.replace("-", "/")
    
    # Create flatlib DateTime and GeoPos objects
    flat_date = Datetime(date_formatted, time_str, offset_hours)
    flat_pos = GeoPos(lat, lon)
    
    # Compute Chart
    chart = Chart(flat_date, flat_pos)
    
    # Extract Planets
    planets_to_extract = [
        (const.SUN, "Sun"),
        (const.MOON, "Moon"),
        (const.MERCURY, "Mercury"),
        (const.VENUS, "Venus"),
        (const.MARS, "Mars"),
        (const.JUPITER, "Jupiter"),
        (const.SATURN, "Saturn"),
        (const.URANUS, "Uranus"),
        (const.NEPTUNE, "Neptune"),
        (const.PLUTO, "Pluto")
    ]
    
    planets_data = {}
    for const_id, name in planets_to_extract:
        p_obj = chart.get(const_id)
        house_num = find_planet_house(chart, p_obj)
        planets_data[name] = {
            "sign": p_obj.sign,
            "degree": round(p_obj.signlon, 2),
            "longitude": round(p_obj.lon, 2),
            "house": house_num
        }
        
    # Extract Ascendant
    asc_obj = chart.get(const.ASC)
    asc_data = {
        "sign": asc_obj.sign,
        "degree": round(asc_obj.signlon, 2),
        "longitude": round(asc_obj.lon, 2)
    }
    
    # Extract Houses
    houses_data = {}
    for i in range(1, 13):
        h_obj = chart.get(f"House{i}")
        houses_data[f"House{i}"] = {
            "sign": h_obj.sign,
            "degree": round(h_obj.signlon, 2),
            "longitude": round(h_obj.lon, 2)
        }
        
    return {
        "formatted_address": geo_data["formatted_address"],
        "coordinates": {"lat": lat, "lon": lon},
        "timezone_offset": offset_str,
        "timezone_offset_hours": offset_hours,
        "planets": planets_data,
        "ascendant": asc_data,
        "houses": houses_data
    }

def get_daily_transits(natal_chart: dict, date: str) -> dict:
    """
    Computes transit alignments for a specific date relative to a natal chart.
    natal_chart: Calculated chart dict from compute_birth_chart.
    date: YYYY-MM-DD
    """
    # 1. Resolve transit positions on date
    # Standard location: use the user's birth location coordinates to calculate local transit alignments
    coords = natal_chart.get("coordinates", {"lat": 0.0, "lon": 0.0})
    lat = coords["lat"]
    lon = coords["lon"]
    offset_hours = natal_chart.get("timezone_offset_hours", 0.0)
    
    date_formatted = date.replace("-", "/")
    flat_date = Datetime(date_formatted, "12:00", offset_hours)  # Noon transits
    flat_pos = GeoPos(lat, lon)
    
    transit_chart = Chart(flat_date, flat_pos)
    
    planets_to_extract = [
        (const.SUN, "Sun"),
        (const.MOON, "Moon"),
        (const.MERCURY, "Mercury"),
        (const.VENUS, "Venus"),
        (const.MARS, "Mars"),
        (const.JUPITER, "Jupiter"),
        (const.SATURN, "Saturn"),
        (const.URANUS, "Uranus"),
        (const.NEPTUNE, "Neptune"),
        (const.PLUTO, "Pluto")
    ]
    
    transit_planets = {}
    for const_id, name in planets_to_extract:
        p_obj = transit_chart.get(const_id)
        transit_planets[name] = p_obj.lon
        
    # 2. Compare transits to natal longitudes mathematically to find aspects
    natal_planets = natal_chart.get("planets", {})
    
    aspects_to_check = {
        0: "Conjunction",
        60: "Sextile",
        90: "Square",
        120: "Trine",
        180: "Opposition"
    }
    
    active_transits = []
    
    for t_name, t_lon in transit_planets.items():
        for n_name, n_data in natal_planets.items():
            n_lon = n_data.get("longitude")
            if n_lon is None:
                continue
                
            # Compute angular separation
            diff = abs(t_lon - n_lon)
            if diff > 180:
                diff = 360 - diff
                
            # Check major aspects (within 8 degree orb)
            for angle, asp_name in aspects_to_check.items():
                orb = abs(diff - angle)
                if orb <= 8.0:
                    # Provide interpretation hint based on standard astrology
                    interpretation_hint = f"Transiting {t_name} forms a {asp_name} with natal {n_name} (orb: {orb:.2f}°)."
                    active_transits.append({
                        "transit_planet": t_name,
                        "aspect": asp_name,
                        "natal_planet": n_name,
                        "orb": round(orb, 2),
                        "interpretation_hint": interpretation_hint
                    })
                    
    return {"date": date, "transits": active_transits}

def knowledge_lookup(query: str) -> str:
    """
    RAG retriever tool query. Resolves context from vector database.
    """
    try:
        results = retrieve(query, top_k=3)
        if not results:
            return "No matching astrological notes found in the knowledge base."
        return "\n\n---\n\n".join(results)
    except Exception as e:
        return f"Knowledge base lookup unavailable: {str(e)}"
