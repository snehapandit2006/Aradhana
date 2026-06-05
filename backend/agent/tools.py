import os
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

# Import RAG retriever helper
from rag.retriever import retrieve

# Import ephem-based calculations
from astro.ephemeris import compute_chart, compute_transits

def geocode_place(place_name: str) -> dict:
    """
    Resolve place name to coordinates and timezone.
    Uses Nominatim (OpenStreetMap) + timezonefinder — no API key needed.
    """
    geolocator = Nominatim(user_agent="astroagent_v1")
    location = geolocator.geocode(place_name, timeout=10)

    if not location:
        raise ValueError(
            f"Could not geocode '{place_name}'. "
            "Try a more specific name e.g. 'Lucknow, India'."
        )

    lat = location.latitude
    lon = location.longitude

    # Timezone from coordinates — fully offline
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon)

    if not tz_name:
        raise ValueError(f"Could not determine timezone for {place_name}")

    # Get UTC offset as float (e.g. 5.5 for IST)
    tz = pytz.timezone(tz_name)
    offset_seconds = tz.utcoffset(datetime.now()).total_seconds()
    offset_hours = offset_seconds / 3600

    # Format as '+05:30' string
    sign = "+" if offset_hours >= 0 else "-"
    abs_hours = abs(offset_hours)
    hours = int(abs_hours)
    minutes = int((abs_hours - hours) * 60)
    offset_str = f"{sign}{hours:02d}:{minutes:02d}"

    return {
        "lat": lat,
        "lon": lon,
        "timezone_id": tz_name,
        "timezone_offset_hours": offset_hours,
        "timezone_offset": offset_str,
        "formatted_address": location.address
    }

def compute_birth_chart(date: str, time: Optional[str], place: str, time_unknown: bool = False) -> dict:
    """
    Computes birth chart planetary positions and houses using real ephemeris.
    date: YYYY-MM-DD
    time: HH:MM
    place: City/Town name
    """
    try:
        # Resolve place to lat, lon, timezone
        geo_data = geocode_place(place)
        lat = geo_data["lat"]
        lon = geo_data["lon"]
        offset_hours = geo_data["timezone_offset_hours"]
        offset_str = geo_data["timezone_offset"]
        
        # Handle unknown birth time by defaulting to noon
        time_str = "12:00" if (time_unknown or not time) else time
        
        # Compute using ephemeris module
        ephem_chart = compute_chart(date, time_str, lat, lon, offset_hours)
        
        # Convert houses to expected format
        houses_data = {}
        from astro.ephemeris import longitude_to_sign
        for i in range(1, 13):
            h_lon = float(ephem_chart["houses"][str(i)])
            h_sign, h_deg = longitude_to_sign(h_lon)
            houses_data[f"House{i}"] = {
                "sign": h_sign,
                "degree": round(h_deg, 2),
                "longitude": round(h_lon, 2)
            }
            
        return {
            "formatted_address": geo_data["formatted_address"],
            "coordinates": {"lat": lat, "lon": lon},
            "timezone_offset": offset_str,
            "timezone_offset_hours": offset_hours,
            "planets": ephem_chart["planets"],
            "ascendant": ephem_chart["ascendant"],
            "houses": houses_data
        }
    except Exception as e:
        import traceback
        print(f"[compute_birth_chart ERROR] {e}")
        traceback.print_exc()
        return {"error": str(e)}


def get_daily_transits(natal_chart: dict, date: str) -> dict:
    """
    Computes transit alignments for a specific date relative to a natal chart.
    natal_chart: Calculated chart dict from compute_birth_chart.
    date: YYYY-MM-DD
    """
    coords = natal_chart.get("coordinates", {"lat": 0.0, "lon": 0.0})
    lat = coords["lat"]
    lon = coords["lon"]
    
    transit_res = compute_transits(natal_chart, date, lat, lon)
    
    active_transits = []
    for asp in transit_res.get("aspects", []):
        t_name = asp["transit_planet"]
        asp_name = asp["aspect"]
        n_name = asp["natal_planet"]
        orb = asp["orb"]
        interpretation_hint = f"Transiting {t_name} forms a {asp_name} with natal {n_name} (orb: {orb:.2f}°)."
        active_transits.append({
            "transit_planet": t_name,
            "aspect": asp_name,
            "natal_planet": n_name,
            "orb": orb,
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
