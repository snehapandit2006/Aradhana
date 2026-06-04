"""
AstroAgent Health Check
=======================
Run this BEFORE starting the full server to verify every external
dependency is wired correctly.

Usage (from the backend/ directory):
    python utils/healthcheck.py

Exit codes:
    0  — all checks passed
    1  — one or more checks failed

Checks performed:
    [1] Environment variables       — all required keys present in .env
    [2] flatlib chart math          — compute a known chart, verify sun sign
    [3] Google Geocoding API        — resolve "Mumbai, India" to coordinates
    [4] Google Timezone API         — get UTC offset for Mumbai coordinates
    [5] Cohere embeddings           — embed a short string, verify vector shape
    [6] Chroma DB connection        — open collection, verify document count > 0
    [7] knowledge_lookup tool       — end-to-end RAG query, verify non-empty result
    [8] Groq API connection         — send a minimal prompt, verify text response
    [9] Wraparound longitude math   — unit test for the 359°/1° edge case
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# ── Ensure we can import from backend/ root ────────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

# ── Colour helpers (no external deps) ─────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg: str)   -> str: return f"  {GREEN}✓{RESET}  {msg}"
def fail(msg: str) -> str: return f"  {RED}✗{RESET}  {msg}"
def warn(msg: str) -> str: return f"  {YELLOW}!{RESET}  {msg}"
def head(msg: str) -> str: return f"\n{BOLD}{CYAN}{msg}{RESET}"

results: list[tuple[str, bool, str]] = []

def check(name: str, passed: bool, detail: str) -> None:
    results.append((name, passed, detail))
    print(ok(detail) if passed else fail(detail))


# ══════════════════════════════════════════════════════════════════════════
# [1] Environment variables
# ══════════════════════════════════════════════════════════════════════════
print(head("[1] Environment variables"))

required_keys = [
    "GROQ_API_KEY",
    "GOOGLE_GEOCODING_API_KEY",
    "COHERE_API_KEY",
    "ALLOWED_ORIGIN",
]

for key in required_keys:
    val = os.getenv(key)
    if val and val not in ("your_groq_api_key_here",
                           "your_google_api_key_here",
                           "your_cohere_api_key_here"):
        check(key, True, f"{key} is set ({val[:6]}…)")
    else:
        check(key, False, f"{key} is MISSING or still a placeholder — set it in .env")


# ══════════════════════════════════════════════════════════════════════════
# [2] flatlib chart math
# Known input : 1990-06-15, 08:30, Mumbai (UTC+5.5)
# Expected    : Sun in Gemini (~84° ecliptic longitude)
# ══════════════════════════════════════════════════════════════════════════
print(head("[2] flatlib chart math"))

try:
    from flatlib.datetime import Datetime
    from flatlib.geopos import GeoPos
    from flatlib.chart import Chart
    from flatlib import const

    # Mumbai coordinates (positive = N/E)
    dt   = Datetime("1990/06/15", "08:30", "+05:30")
    pos  = GeoPos(19.076, 72.877)
    chart = Chart(dt, pos, IDs=const.LIST_OBJECTS)

    sun       = chart.getObject(const.SUN)
    sun_lon   = sun.lon          # ecliptic longitude 0–360
    sun_sign  = sun.sign         # e.g. 'Gemini'

    expected_sign = "Gemini"
    expected_lon_approx = 84.2
    lon_ok   = abs(sun_lon - expected_lon_approx) < 2.0  # 2° tolerance for this self-test
    sign_ok  = sun_sign == expected_sign

    check("flatlib_sun_sign", sign_ok,
          f"Sun sign = {sun_sign} (expected {expected_sign})")
    check("flatlib_sun_lon", lon_ok,
          f"Sun longitude = {sun_lon:.2f}° (expected ~{expected_lon_approx}°)")

    # Verify GeoPos accepts raw floats (not strings)
    try:
        GeoPos(19.076, 72.877)
        check("flatlib_geopos_floats", True,
              "GeoPos(float, float) accepted — no string conversion needed")
    except Exception as e:
        check("flatlib_geopos_floats", False, f"GeoPos float input failed: {e}")

    # Verify timezone offset as string '+05:30' is accepted by Datetime
    try:
        Datetime("1990/06/15", "08:30", "+05:30")
        check("flatlib_tz_string", True,
              "Datetime accepts '+05:30' timezone string format")
    except Exception as e:
        check("flatlib_tz_string", False,
              f"Datetime timezone string rejected — may need float conversion: {e}")
        print(warn("  If this failed, convert '+05:30' → 5.5 before calling Datetime"))

except ImportError:
    check("flatlib_import", False,
          "flatlib not installed — run: pip install flatlib")
except Exception as e:
    check("flatlib_chart", False, f"Unexpected error in flatlib: {e}")


# ══════════════════════════════════════════════════════════════════════════
# [3] Google Geocoding API
# ══════════════════════════════════════════════════════════════════════════
print(head("[3] Google Geocoding API"))

GOOGLE_KEY = os.getenv("GOOGLE_GEOCODING_API_KEY", "")

try:
    import requests

    resp = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json",
        params={"address": "Mumbai, India", "key": GOOGLE_KEY},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") == "OK":
        loc      = data["results"][0]["geometry"]["location"]
        lat, lon = loc["lat"], loc["lng"]
        lat_ok   = 18.0 < lat < 20.0
        lon_ok   = 72.0 < lon < 74.0

        check("geocoding_status", True,  f"API status = OK")
        check("geocoding_lat",    lat_ok, f"Latitude  = {lat:.4f} (expected ~19.07)")
        check("geocoding_lon",    lon_ok, f"Longitude = {lon:.4f} (expected ~72.88)")
    elif data.get("status") == "REQUEST_DENIED":
        check("geocoding_api_key", False,
              "REQUEST_DENIED — check GOOGLE_GEOCODING_API_KEY and that Geocoding API is enabled in Google Cloud Console")
    else:
        check("geocoding_status", False,
              f"Unexpected status: {data.get('status')} — {data.get('error_message', '')}")

except requests.exceptions.ConnectionError:
    check("geocoding_network", False, "Network error — check internet connection")
except Exception as e:
    check("geocoding_general", False, f"Geocoding check failed: {e}")


# ══════════════════════════════════════════════════════════════════════════
# [4] Google Timezone API
# ══════════════════════════════════════════════════════════════════════════
print(head("[4] Google Timezone API"))

try:
    # Mumbai: UTC+5:30 = 19800 seconds offset
    tz_resp = requests.get(
        "https://maps.googleapis.com/maps/api/timezone/json",
        params={
            "location": "19.076,72.877",
            "timestamp": 646300200,   # 1990-06-15 08:30 UTC approx
            "key": GOOGLE_KEY,
        },
        timeout=10,
    )
    tz_resp.raise_for_status()
    tz_data = tz_resp.json()

    if tz_data.get("status") == "OK":
        offset_secs  = tz_data.get("rawOffset", 0) + tz_data.get("dstOffset", 0)
        offset_hours = offset_secs / 3600
        tz_id        = tz_data.get("timeZoneId", "")
        offset_ok    = abs(offset_hours - 5.5) < 0.1

        check("timezone_status",    True,     f"API status = OK")
        check("timezone_offset",    offset_ok, f"Offset = {offset_hours}h (expected 5.5h for Mumbai)")
        check("timezone_id_present", bool(tz_id), f"Timezone ID = {tz_id}")
    elif tz_data.get("status") == "REQUEST_DENIED":
        check("timezone_api_key", False,
              "REQUEST_DENIED — ensure Timezone API is enabled alongside Geocoding API")
    else:
        check("timezone_status", False,
              f"Status: {tz_data.get('status')} — {tz_data.get('errorMessage', '')}")

except Exception as e:
    check("timezone_general", False, f"Timezone check failed: {e}")


# ══════════════════════════════════════════════════════════════════════════
# [5] Cohere embeddings
# ══════════════════════════════════════════════════════════════════════════
print(head("[5] Cohere embeddings"))

try:
    import cohere

    co   = cohere.Client(os.getenv("COHERE_API_KEY", ""))
    resp = co.embed(
        texts=["Saturn represents discipline and karma in astrology"],
        model="embed-english-v3.0",
        input_type="search_document",
    )

    embedding   = resp.embeddings[0]
    dim         = len(embedding)
    dim_ok      = dim == 1024   # embed-english-v3.0 produces 1024-dim vectors
    nonzero_ok  = any(v != 0.0 for v in embedding[:10])

    check("cohere_request",   True,      f"Cohere API responded without error")
    check("cohere_dimensions", dim_ok,   f"Embedding dimension = {dim} (expected 1024)")
    check("cohere_nonzero",   nonzero_ok, "Embedding values are non-zero")

except cohere.errors.UnauthorizedError:
    check("cohere_auth", False,
          "Unauthorized — check COHERE_API_KEY at dashboard.cohere.com")
except Exception as e:
    check("cohere_general", False, f"Cohere check failed: {e}")


# ══════════════════════════════════════════════════════════════════════════
# [6] Chroma DB connection & document count
# ══════════════════════════════════════════════════════════════════════════
print(head("[6] Chroma DB"))

CHROMA_PATH = BACKEND_DIR / "chroma_db"

try:
    import chromadb

    if not CHROMA_PATH.exists():
        check("chroma_seeded", False,
              f"chroma_db/ not found at {CHROMA_PATH} — run: python rag/seed.py first")
    else:
        client     = chromadb.PersistentClient(path=str(CHROMA_PATH))
        collection = client.get_or_create_collection("astrology_knowledge")
        count      = collection.count()
        count_ok   = count >= 50   # expect at least 50 docs after seeding

        check("chroma_exists",   True,      f"chroma_db/ directory found")
        check("chroma_count",    count_ok,  f"Collection has {count} documents (expected ≥50)")

        if count == 0:
            print(warn("  Collection is empty — run: python rag/seed.py"))
        elif count < 50:
            print(warn(f"  Only {count} docs — seed.py may have run partially. Re-run it."))

except Exception as e:
    check("chroma_general", False, f"Chroma check failed: {e}")


# ══════════════════════════════════════════════════════════════════════════
# [7] knowledge_lookup end-to-end
# ══════════════════════════════════════════════════════════════════════════
print(head("[7] knowledge_lookup end-to-end"))

try:
    # Only run if Chroma has documents
    chroma_ok = any(name == "chroma_count" and passed
                    for name, passed, _ in results)

    if not chroma_ok:
        print(warn("  Skipping — Chroma not seeded. Run seed.py first."))
    else:
        import chromadb
        import cohere

        co         = cohere.Client(os.getenv("COHERE_API_KEY", ""))
        client     = chromadb.PersistentClient(path=str(CHROMA_PATH))
        collection = client.get_or_create_collection("astrology_knowledge")

        query     = "What does Saturn represent in astrology?"
        embed_res = co.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query",
        )
        query_vec = embed_res.embeddings[0]

        results_chroma = collection.query(
            query_embeddings=[query_vec],
            n_results=3,
        )
        docs = results_chroma.get("documents", [[]])[0]

        has_results   = len(docs) > 0
        saturn_in_doc = any("saturn" in doc.lower() or "Saturn" in doc
                            for doc in docs)

        check("rag_returns_results", has_results,
              f"RAG returned {len(docs)} document(s) for Saturn query")
        check("rag_relevance", saturn_in_doc,
              "Top result mentions Saturn (basic relevance check)")

        if has_results:
            snippet = docs[0][:100].replace("\n", " ")
            print(f"  {CYAN}Sample chunk:{RESET} {snippet}…")

except Exception as e:
    check("rag_general", False, f"knowledge_lookup check failed: {e}")


# ══════════════════════════════════════════════════════════════════════════
# [8] Groq API connection
# ══════════════════════════════════════════════════════════════════════════
print(head("[8] Groq API"))

try:
    from groq import Groq

    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
    t0          = time.time()

    resp = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": "Reply with exactly one word: ready"}],
        max_tokens=5,
        temperature=0,
    )
    latency_ms = (time.time() - t0) * 1000
    reply      = resp.choices[0].message.content.strip().lower()

    check("groq_response",  True,             f"Groq responded in {latency_ms:.0f}ms")
    check("groq_model",     True,             f"Model: llama3-70b-8192")
    check("groq_latency",   latency_ms < 8000, f"Latency {latency_ms:.0f}ms (warn if >8000ms)")

    if latency_ms > 8000:
        print(warn("  High latency on Groq free tier — p95 may be slow during eval runs"))

except Exception as e:
    err = str(e)
    if "401" in err or "invalid_api_key" in err.lower():
        check("groq_auth", False,
              "Invalid GROQ_API_KEY — get yours at console.groq.com")
    elif "429" in err:
        check("groq_rate", False,
              "Rate limited — wait 60s and retry (free tier: 30 RPM)")
    else:
        check("groq_general", False, f"Groq check failed: {e}")


# ══════════════════════════════════════════════════════════════════════════
# [9] Longitude wraparound unit test
# This is the edge case in run_evals.py chart_math_tolerance check
# ══════════════════════════════════════════════════════════════════════════
print(head("[9] Longitude wraparound math"))

def lon_distance(a: float, b: float) -> float:
    """Shortest angular distance between two ecliptic longitudes (0–360)."""
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)

cases = [
    (84.2,  84.5,  0.3,   True,  "Normal case: 84.2° vs 84.5°"),
    (359.5,  0.5,  1.0,   True,  "Wraparound: 359.5° vs 0.5° = 1.0° apart"),
    (0.5,  359.5,  1.0,   True,  "Wraparound reversed: 0.5° vs 359.5°"),
    (84.2,  86.5,  2.3,  False,  "Outside tolerance: 84.2° vs 86.5° = 2.3° apart"),
    (180.0, 181.5, 1.5,  False,  "Outside tolerance at 180°"),
]

all_passed = True
for a, b, expected_dist, should_pass, label in cases:
    dist    = lon_distance(a, b)
    correct = abs(dist - expected_dist) < 0.01
    within  = dist <= 1.0
    result  = (within == should_pass) and correct
    all_passed = all_passed and result
    check(f"wraparound_{label[:20]}", result,
          f"{label} → dist={dist:.2f}° {'✓ within 1°' if within else '✗ outside 1°'}")

if not all_passed:
    print(warn("  Update chart_math_tolerance in run_evals.py to use lon_distance()"))
    print(warn("  Replace: abs(computed - reference) <= 1.0"))
    print(warn("  With:    min(abs(diff), 360 - abs(diff)) <= 1.0"))


# ══════════════════════════════════════════════════════════════════════════
# Final scorecard
# ══════════════════════════════════════════════════════════════════════════
passed = sum(1 for _, p, _ in results if p)
failed = sum(1 for _, p, _ in results if not p)
total  = len(results)

print(f"\n{'═' * 54}")
print(f"{BOLD}  Health Check Results{RESET}")
print(f"{'═' * 54}")
print(f"  {GREEN}Passed:{RESET} {passed}/{total}")
if failed:
    print(f"  {RED}Failed:{RESET} {failed}/{total}")
    print(f"\n  {YELLOW}Failed checks:{RESET}")
    for name, passed_flag, detail in results:
        if not passed_flag:
            print(f"    {RED}•{RESET} {detail}")
print(f"{'═' * 54}\n")

if failed == 0:
    print(f"{GREEN}{BOLD}  All checks passed. Safe to run: uvicorn main:app --reload{RESET}\n")
    sys.exit(0)
else:
    print(f"{RED}{BOLD}  Fix the failed checks above before starting the server.{RESET}\n")
    sys.exit(1)
