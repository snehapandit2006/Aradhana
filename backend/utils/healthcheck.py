"""
AstroAgent Health Check
=======================
Run this BEFORE starting the full server to verify every external
dependency is wired correctly.

Usage (from the backend/ directory):
    python utils/healthcheck.py

Exit codes:
    0  -- all checks passed
    1  -- one or more checks failed

Checks performed:
    [1] Environment variables     -- required keys present in .env
    [2] ephem chart math          -- compute a known chart, verify real sun sign
    [3] Nominatim geocoding       -- resolve city name, no API key needed
    [4] timezonefinder            -- offline timezone lookup from coordinates
    [5] geocode_place() tool      -- end-to-end geocoding pipeline
    [6] Cohere embeddings         -- embed a string, verify vector shape
    [7] Chroma DB connection      -- open collection, verify document count
    [8] knowledge_lookup RAG      -- end-to-end retrieval query
    [9] Groq API connection       -- minimal prompt, verify text response
   [10] Longitude wraparound math -- unit test 359/1 edge case
"""

import os
import sys
import time
import math
from pathlib import Path
from datetime import datetime

# ── Ensure we can import from backend/ root ───────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(BACKEND_DIR.parent / ".env")

# ── ASCII-safe output helpers (no unicode — Windows console safe) ─────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):   return f"  {GREEN}[PASS]{RESET}  {msg}"
def fail(msg): return f"  {RED}[FAIL]{RESET}  {msg}"
def warn(msg): return f"  {YELLOW}[WARN]{RESET}  {msg}"
def head(msg): return f"\n{BOLD}{CYAN}{msg}{RESET}"

results = []   # list of (name, passed, detail)

def check(name, passed, detail):
    results.append((name, passed, detail))
    print(ok(detail) if passed else fail(detail))


# ═════════════════════════════════════════════════════════════════════════
# [1] Environment variables
# ═════════════════════════════════════════════════════════════════════════
print(head("[1] Environment variables"))

REQUIRED = ["GROQ_API_KEY", "COHERE_API_KEY", "ALLOWED_ORIGIN"]
OPTIONAL = ["GOOGLE_GEOCODING_API_KEY"]   # no longer needed, warn if set

for key in REQUIRED:
    val = os.getenv(key)
    placeholders = (
        "your_groq_api_key_here",
        "your_google_api_key_here",
        "your_cohere_api_key_here",
    )
    if val and val not in placeholders:
        check(key, True, f"{key} is set ({val[:6]}...)")
    else:
        check(key, False, f"{key} is MISSING or still a placeholder -- set it in .env")

for key in OPTIONAL:
    val = os.getenv(key)
    if val:
        print(warn(f"  {key} is set but no longer needed -- "
                   f"project now uses Nominatim (no key required)"))


# ═════════════════════════════════════════════════════════════════════════
# [2] ephem chart math
# Known input:  19 Jan 2006, 22:30 IST, Lucknow (your actual birth details)
# Expected:     Sun in Capricorn (~299 deg)
# Also test:    1990-06-15 08:30 IST Mumbai -> Sun in Gemini (~84 deg)
# ═════════════════════════════════════════════════════════════════════════
print(head("[2] ephem chart math (real ephemeris)"))

try:
    import ephem

    def ephem_sun_lon(date_utc_str):
        """Return Sun ecliptic longitude for a UTC datetime string."""
        sun = ephem.Sun()
        sun.compute(date_utc_str, epoch=ephem.J2000)
        ecl = ephem.Ecliptic(sun, epoch=ephem.J2000)
        return math.degrees(float(ecl.lon)) % 360

    SIGNS = [
        "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
        "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
    ]

    def lon_to_sign(lon):
        return SIGNS[int(lon // 30) % 12]

    # Test case 1: your birth  2006-01-19 22:30 IST = 2006-01-19 17:00 UTC
    lon_2006 = ephem_sun_lon("2006/01/19 17:00:00")
    sign_2006 = lon_to_sign(lon_2006)
    check("ephem_2006_sign", sign_2006 == "Capricorn",
          f"2006-01-19: Sun = {lon_2006:.2f} deg = {sign_2006} (expected Capricorn)")

    # Test case 2: Mumbai 1990-06-15 08:30 IST = 1990-06-15 03:00 UTC
    lon_1990 = ephem_sun_lon("1990/06/15 03:00:00")
    sign_1990 = lon_to_sign(lon_1990)
    check("ephem_1990_sign", sign_1990 == "Gemini",
          f"1990-06-15: Sun = {lon_1990:.2f} deg = {sign_1990} (expected Gemini)")

    # Verify outer planets for 2006 -- these MUST NOT be in Cancer/Gemini/Libra
    neptune = ephem.Neptune()
    neptune.compute("2006/01/19 17:00:00", epoch=ephem.J2000)
    nep_ecl = ephem.Ecliptic(neptune, epoch=ephem.J2000)
    nep_lon = math.degrees(float(nep_ecl.lon)) % 360
    nep_sign = lon_to_sign(nep_lon)

    pluto = ephem.Pluto()
    pluto.compute("2006/01/19 17:00:00", epoch=ephem.J2000)
    plu_ecl = ephem.Ecliptic(pluto, epoch=ephem.J2000)
    plu_lon = math.degrees(float(plu_ecl.lon)) % 360
    plu_sign = lon_to_sign(plu_lon)

    check("ephem_neptune_2006",
          nep_sign == "Aquarius",
          f"2006 Neptune = {nep_lon:.1f} deg = {nep_sign} (expected Aquarius, NOT Cancer)")
    check("ephem_pluto_2006",
          plu_sign == "Sagittarius",
          f"2006 Pluto   = {plu_lon:.1f} deg = {plu_sign} (expected Sagittarius, NOT Gemini)")

    if nep_sign == "Aquarius" and plu_sign == "Sagittarius":
        print(f"  {GREEN}Real ephemeris confirmed -- outer planets correct for 2006 birth{RESET}")

except ImportError:
    check("ephem_import", False,
          "ephem not installed -- run: pip install ephem")
except Exception as e:
    check("ephem_general", False, f"ephem error: {e}")


# ═════════════════════════════════════════════════════════════════════════
# [3] Nominatim geocoding (OpenStreetMap, no API key)
# ═════════════════════════════════════════════════════════════════════════
print(head("[3] Nominatim geocoding (no API key needed)"))

try:
    from geopy.geocoders import Nominatim
    import time as _time

    geolocator = Nominatim(user_agent="astroagent_healthcheck_v1")

    # Test with Lucknow (your birth city)
    location = geolocator.geocode("Lucknow, India", timeout=10)
    _time.sleep(1)   # Nominatim rate limit: 1 req/sec

    if location:
        lat, lon = location.latitude, location.longitude
        lat_ok = 26.0 < lat < 27.5
        lon_ok = 80.0 < lon < 82.0
        check("nominatim_status",  True,    "Nominatim responded for 'Lucknow, India'")
        check("nominatim_lat",     lat_ok,  f"Latitude  = {lat:.4f} (expected ~26.85)")
        check("nominatim_lon",     lon_ok,  f"Longitude = {lon:.4f} (expected ~80.95)")
    else:
        check("nominatim_result", False,
              "No result for 'Lucknow, India' -- check internet connection")

    # Test Mumbai too (used in golden set)
    location2 = geolocator.geocode("Mumbai, India", timeout=10)
    _time.sleep(1)
    if location2:
        check("nominatim_mumbai", True,
              f"Mumbai resolved: {location2.latitude:.3f}, {location2.longitude:.3f}")
    else:
        check("nominatim_mumbai", False, "Mumbai geocoding failed")

except ImportError:
    check("geopy_import", False,
          "geopy not installed -- run: pip install geopy")
except Exception as e:
    check("nominatim_general", False, f"Nominatim error: {e}")


# ═════════════════════════════════════════════════════════════════════════
# [4] timezonefinder (offline, no API key)
# ═════════════════════════════════════════════════════════════════════════
print(head("[4] timezonefinder (offline timezone lookup)"))

try:
    from timezonefinder import TimezoneFinder
    import pytz

    tf = TimezoneFinder()

    # Lucknow
    tz_name = tf.timezone_at(lat=26.8467, lng=80.9462)
    tz_ok = tz_name == "Asia/Kolkata"
    check("tzfinder_lucknow", tz_ok,
          f"Lucknow timezone = {tz_name} (expected Asia/Kolkata)")

    # Verify offset
    if tz_name:
        tz = pytz.timezone(tz_name)
        offset = tz.utcoffset(datetime.now()).total_seconds() / 3600
        offset_ok = abs(offset - 5.5) < 0.1
        check("tzfinder_offset", offset_ok,
              f"IST offset = {offset}h (expected 5.5h)")

    # Tokyo (tests non-Indian timezone)
    tz_tokyo = tf.timezone_at(lat=35.6762, lng=139.6503)
    check("tzfinder_tokyo", tz_tokyo == "Asia/Tokyo",
          f"Tokyo timezone = {tz_tokyo} (expected Asia/Tokyo)")

except ImportError:
    check("tzfinder_import", False,
          "timezonefinder not installed -- run: pip install timezonefinder pytz")
except Exception as e:
    check("tzfinder_general", False, f"timezonefinder error: {e}")


# ═════════════════════════════════════════════════════════════════════════
# [5] geocode_place() end-to-end pipeline
# ═════════════════════════════════════════════════════════════════════════
print(head("[5] geocode_place() tool end-to-end"))

try:
    # Simulate what tools.py does
    from geopy.geocoders import Nominatim
    from timezonefinder import TimezoneFinder
    import pytz, time as _time
    from datetime import timedelta

    def geocode_place_test(place_name):
        geo  = Nominatim(user_agent="astroagent_healthcheck_v1")
        loc  = geo.geocode(place_name, timeout=10)
        _time.sleep(1)
        if not loc:
            raise ValueError(f"Could not geocode '{place_name}'")
        lat, lon = loc.latitude, loc.longitude
        tf2  = TimezoneFinder()
        tz_n = tf2.timezone_at(lat=lat, lng=lon)
        tz   = pytz.timezone(tz_n)
        off  = tz.utcoffset(datetime.now()).total_seconds() / 3600
        sign = "+" if off >= 0 else "-"
        h, m = int(abs(off)), int(round((abs(off) % 1) * 60))
        return {
            "lat": lat, "lon": lon,
            "timezone_id": tz_n,
            "offset_hours": off,
            "offset_str": f"{sign}{h:02d}:{m:02d}",
            "formatted_address": loc.address,
        }

    result = geocode_place_test("Lucknow, Uttar Pradesh, India")
    check("geocode_pipeline_lat",     26.0 < result["lat"] < 27.5,
          f"Lat = {result['lat']:.4f}")
    check("geocode_pipeline_tz",      result["timezone_id"] == "Asia/Kolkata",
          f"TZ  = {result['timezone_id']}")
    check("geocode_pipeline_offset",  result["offset_str"] == "+05:30",
          f"Offset string = {result['offset_str']} (expected +05:30)")

except Exception as e:
    check("geocode_pipeline", False, f"geocode_place pipeline failed: {e}")


# ═════════════════════════════════════════════════════════════════════════
# [6] Cohere embeddings
# ═════════════════════════════════════════════════════════════════════════
print(head("[6] Cohere embeddings"))

try:
    import cohere

    co   = cohere.Client(os.getenv("COHERE_API_KEY", ""))
    resp = co.embed(
        texts=["Saturn represents discipline and karma in astrology"],
        model="embed-english-v3.0",
        input_type="search_document",
    )
    embedding = resp.embeddings[0]
    dim       = len(embedding)

    check("cohere_response",    True,       "Cohere API responded without error")
    check("cohere_dim",         dim == 1024, f"Embedding dimension = {dim} (expected 1024)")
    check("cohere_nonzero",     any(v != 0 for v in embedding[:10]),
          "Embedding values are non-zero")

except Exception as e:
    err = str(e)
    if "401" in err or "unauthorized" in err.lower():
        check("cohere_auth", False,
              "Unauthorized -- check COHERE_API_KEY at dashboard.cohere.com")
    else:
        check("cohere_general", False, f"Cohere error: {e}")


# ═════════════════════════════════════════════════════════════════════════
# [7] Chroma DB
# ═════════════════════════════════════════════════════════════════════════
print(head("[7] Chroma DB"))

CHROMA_PATH = BACKEND_DIR / "chroma_db"

try:
    import chromadb

    if not CHROMA_PATH.exists():
        check("chroma_seeded", False,
              f"chroma_db/ not found -- run: python rag/seed.py")
    else:
        client     = chromadb.PersistentClient(path=str(CHROMA_PATH))
        collection = client.get_or_create_collection("astrology_knowledge")
        count      = collection.count()
        check("chroma_exists", True,     "chroma_db/ directory found")
        check("chroma_count",  count >= 40,
              f"Collection has {count} documents (expected >= 40)")
        if count < 100:
            print(warn(f"  Only {count} docs -- consider expanding to 150+ for better RAG quality"))

except Exception as e:
    check("chroma_general", False, f"Chroma error: {e}")


# ═════════════════════════════════════════════════════════════════════════
# [8] knowledge_lookup end-to-end
# ═════════════════════════════════════════════════════════════════════════
print(head("[8] knowledge_lookup RAG (end-to-end)"))

try:
    chroma_ok = any(n == "chroma_count" and p for n, p, _ in results)

    if not chroma_ok:
        print(warn("  Skipping -- Chroma not seeded. Run: python rag/seed.py"))
    else:
        import cohere, chromadb

        co2        = cohere.Client(os.getenv("COHERE_API_KEY", ""))
        client2    = chromadb.PersistentClient(path=str(CHROMA_PATH))
        coll2      = client2.get_or_create_collection("astrology_knowledge")

        query      = "What does Neptune in Aquarius mean for a 2006 birth?"
        embed_resp = co2.embed(texts=[query], model="embed-english-v3.0",
                               input_type="search_query")
        qvec       = embed_resp.embeddings[0]
        hits       = coll2.query(query_embeddings=[qvec], n_results=3)
        docs       = hits.get("documents", [[]])[0]

        check("rag_returns_results", len(docs) > 0,
              f"RAG returned {len(docs)} document(s)")
        check("rag_nonzero_content",
              any(len(d) > 20 for d in docs),
              "Documents have meaningful content (>20 chars)")

        if docs:
            snippet = docs[0][:100].replace("\n", " ")
            print(f"  {CYAN}Sample:{RESET} {snippet}...")

except Exception as e:
    check("rag_general", False, f"RAG error: {e}")


# ═════════════════════════════════════════════════════════════════════════
# [9] Groq API
# ═════════════════════════════════════════════════════════════════════════
print(head("[9] Groq API"))

try:
    from groq import Groq

    client3 = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
    t0      = time.time()
    resp3   = client3.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Reply with exactly one word: ready"}],
        max_tokens=5,
        temperature=0,
    )
    latency = (time.time() - t0) * 1000
    check("groq_response",  True,           f"Groq responded in {latency:.0f}ms")
    check("groq_model",     True,           "Model: llama-3.3-70b-versatile")
    check("groq_latency",   latency < 8000, f"Latency {latency:.0f}ms (warn if >8000ms)")

    if latency > 8000:
        print(warn("  High latency -- may affect eval p95 scores"))

except Exception as e:
    err = str(e)
    if "401" in err or "invalid_api_key" in err.lower():
        check("groq_auth", False,
              "Invalid GROQ_API_KEY -- get yours at console.groq.com")
    elif "429" in err:
        check("groq_rate", False,
              "Rate limited -- wait 60s and retry (free tier: 30 RPM)")
    else:
        check("groq_general", False, f"Groq error: {e}")


# ═════════════════════════════════════════════════════════════════════════
# [10] Longitude wraparound unit test
# ═════════════════════════════════════════════════════════════════════════
print(head("[10] Longitude wraparound math"))

def lon_dist(a, b):
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)

cases = [
    (84.2,  84.5,  0.3,   True,  "Normal: 84.2 vs 84.5 = 0.3 deg apart"),
    (359.5,  0.5,  1.0,   True,  "Wrap:   359.5 vs 0.5 = 1.0 deg apart"),
    (0.5,  359.5,  1.0,   True,  "Wrap:   0.5 vs 359.5 = 1.0 deg apart"),
    (84.2,  86.5,  2.3,  False,  "Outside tolerance: 84.2 vs 86.5 = 2.3 deg"),
    (180.0, 181.5, 1.5,  False,  "Outside tolerance: 180.0 vs 181.5 = 1.5 deg"),
]

for a, b, exp_dist, should_pass, label in cases:
    dist   = lon_dist(a, b)
    within = dist <= 1.0
    result = (within == should_pass) and abs(dist - exp_dist) < 0.01
    status = "within 1 deg" if within else "outside 1 deg"
    check(f"lon_{label[:15]}", result, f"{label} -> dist={dist:.2f} [{status}]")


# ═════════════════════════════════════════════════════════════════════════
# Final scorecard
# ═════════════════════════════════════════════════════════════════════════
passed = sum(1 for _, p, _ in results if p)
failed = sum(1 for _, p, _ in results if not p)
total  = len(results)

print(f"\n{'=' * 56}")
print(f"  Health Check Results")
print(f"{'=' * 56}")
print(f"  Passed: {passed}/{total}")

if failed:
    print(f"  Failed: {failed}/{total}")
    print(f"\n  Failed checks:")
    for name, p, detail in results:
        if not p:
            print(f"    - {detail}")

print(f"{'=' * 56}\n")

if failed == 0:
    print(f"  All checks passed. Safe to start: uvicorn main:app --reload\n")
    sys.exit(0)
else:
    print(f"  Fix the failed checks above before starting the server.\n")
    sys.exit(1)
