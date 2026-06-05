import os
import json
import asyncio
import time
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Set up paths relative to workspace root
import sys
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(WORKSPACE_ROOT, "backend"))

from agent.tools import geocode_place, compute_birth_chart
from agent.graph import app as agent_app
from langchain_core.messages import HumanMessage, AIMessage

EVALS_FILE = os.path.join(WORKSPACE_ROOT, "evals", "golden_set.jsonl")

def run_coordinate_assertion(birth_data, expected_lat, expected_lon, tolerance):
    """Asserts geocoding output coordinates fall within a tolerance range."""
    place = birth_data["place"]
    try:
        time.sleep(1.0)
        res = geocode_place(place)
        lat_diff = abs(res["lat"] - expected_lat)
        lon_diff = abs(res["lon"] - expected_lon)
        passed = lat_diff <= tolerance and lon_diff <= tolerance
        details = f"Geocoded: ({res['lat']:.4f}, {res['lon']:.4f}) vs Expected: ({expected_lat}, {expected_lon})"
        return passed, details
    except Exception as e:
        return False, f"Geocoding failed: {str(e)}"

def run_chart_math_assertion(birth_data, assertion):
    """Computes birth chart and checks planetary longitudes match expected within tolerance."""
    try:
        time.sleep(1.0)
        chart = compute_birth_chart(
            date=birth_data["date"],
            time=birth_data.get("time"),
            place=birth_data["place"],
            time_unknown=birth_data.get("time_unknown", False)
        )
        planets_expected = assertion.get("planets", {})
        tolerance = assertion.get("tolerance", 1.0)
        computed_planets = chart.get("planets", {})
        failed_details = []

        for planet, expected_lon in planets_expected.items():
            if planet not in computed_planets:
                failed_details.append(f"Planet {planet} missing from computed chart")
                continue
            computed_lon = computed_planets[planet]["longitude"]
            diff = abs(computed_lon - expected_lon)
            wrap_diff = min(diff, 360 - diff)
            if wrap_diff > tolerance:
                failed_details.append(
                    f"{planet}: expected {expected_lon}°, got {computed_lon}° (diff: {wrap_diff:.2f}° > {tolerance}°)"
                )

        if failed_details:
            return False, f"Chart math mismatch: {', '.join(failed_details)}"
        return True, "Chart math matched within tolerance."
    except Exception as e:
        return False, f"Chart calculation failed during eval: {str(e)}"

async def run_chat_assertions(message, assertions):
    """Invokes the agent workflow and runs text checks on the final response."""
    initial_state = {
        "messages": [HumanMessage(content=message)],
        "birth_data": None,
        "chart_data": None,
        "intent": None,
        "tool_outputs": [],
        "step_count": 0
    }

    try:
        res = await agent_app.ainvoke(initial_state)
        messages = res.get("messages", [])
        if not messages:
            return False, "Agent returned no messages."

        response_text = messages[-1].content
        passed = True
        failed_details = []

        for ass in assertions:
            ass_type = ass["type"]

            if ass_type == "contains_disclaimer":
                if "Disclaimer:" not in response_text:
                    passed = False
                    failed_details.append("Disclaimer was missing.")

            elif ass_type == "no_absolute_certainty_promises":
                certainty_words = ["definitely", "guaranteed", "100%", "undoubtedly", "promise"]
                found_words = [w for w in certainty_words if w in response_text.lower()]
                if found_words:
                    passed = False
                    failed_details.append(f"Found certainty promises: {found_words}")

            elif ass_type == "contains_redirect_or_refusal":
                keywords = [
                    "astrologer", "journey", "guidance", "stars", "horoscope", "chart",
                    "off-topic", "topic", "astrolog", "cannot", "can't", "invalid", "birth"
                ]
                if not any(k in response_text.lower() for k in keywords):
                    passed = False
                    failed_details.append("Response did not redirect or mention astrology limits.")

            elif ass_type == "contains_substrings":
                for sub in ass.get("substrings", []):
                    if sub.lower() not in response_text.lower():
                        passed = False
                        failed_details.append(f"Missing expected substring: '{sub}'")

        snippet = response_text[:120].replace("\n", " ")
        details = (
            f"Response: {snippet}..."
            if passed
            else f"Failed: {', '.join(failed_details)}. Response: {snippet}..."
        )
        return passed, details

    except Exception as e:
        return False, f"Agent invocation crashed: {str(e)}"

async def execute_evals():
    """Main evaluation harness — loads golden set and runs all tests with scorecard output."""
    print("=" * 50)
    print("  ASTROAGENT EVALUATION HARNESS")
    print("=" * 50)

    # Check for API keys
    missing = []
    if not os.getenv("GROQ_API_KEY"):
        missing.append("GROQ_API_KEY")
    if not os.getenv("COHERE_API_KEY"):
        missing.append("COHERE_API_KEY")
    if missing:
        print(f"WARNING: Missing API keys: {', '.join(missing)}. Some assertions may fail.\n")

    if not os.path.exists(EVALS_FILE):
        print(f"Error: Golden set not found at {EVALS_FILE}")
        return

    test_cases = []
    with open(EVALS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                test_cases.append(json.loads(line.strip()))

    passed_count = 0
    total_count = len(test_cases)
    total_tool_calls = 0
    latencies = []
    results = []

    for i, tc in enumerate(test_cases):
        tc_id = tc["id"]
        tc_name = tc["name"]
        input_type = tc["input_type"]

        print(f"\n[{i+1}/{total_count}] Running: {tc_name} ({tc_id})...")

        t_start = time.perf_counter()

        if input_type == "birth_data":
            assertions = tc.get("assertions", [])
            passed = True
            details_list = []
            for ass in assertions:
                ass_type = ass["type"]
                if ass_type == "coordinate_within_tolerance":
                    p, d = run_coordinate_assertion(
                        tc["input"], ass["lat"], ass["lon"], ass["tolerance"]
                    )
                    if not p:
                        passed = False
                    details_list.append(d)
                elif ass_type == "chart_math_tolerance":
                    p, d = run_chart_math_assertion(tc["input"], ass)
                    if not p:
                        passed = False
                    details_list.append(d)
            details = "; ".join(details_list)

        elif input_type == "chat":
            # Sleep to stagger API requests and avoid 429 rate limit
            await asyncio.sleep(2.0)
            message = tc["input"]["message"]
            passed, details = await run_chat_assertions(message, tc["assertions"])

            # Count tool calls found in output (proxy metric)
            if "Executing tool call:" in details or "knowledge_lookup" in details:
                total_tool_calls += 1
        else:
            passed, details = False, "Unknown test input type."

        elapsed = time.perf_counter() - t_start
        latencies.append(elapsed)

        if passed:
            passed_count += 1
            print(f"  --> PASS [{elapsed:.1f}s]: {details}")
        else:
            print(f"  --> FAIL [{elapsed:.1f}s]: {details}")

        results.append({
            "id": tc_id,
            "name": tc_name,
            "passed": passed,
            "latency_s": round(elapsed, 2)
        })

    # --- Scorecard ---
    failed_count = total_count - passed_count
    accuracy = (passed_count / total_count * 100) if total_count > 0 else 0
    failure_rate = (failed_count / total_count * 100) if total_count > 0 else 0

    sorted_lat = sorted(latencies)
    p50_idx = int(len(sorted_lat) * 0.50)
    p95_idx = int(len(sorted_lat) * 0.95)
    p50 = sorted_lat[p50_idx] if sorted_lat else 0
    p95 = sorted_lat[min(p95_idx, len(sorted_lat) - 1)] if sorted_lat else 0

    print("\n" + "=" * 50)
    print("  EVALUATION SCORECARD")
    print("=" * 50)
    print(f"  {'Metric':<25} {'Value'}")
    print(f"  {'-'*40}")
    print(f"  {'Accuracy':<25} {accuracy:.1f}%  ({passed_count}/{total_count} passed)")
    print(f"  {'Failure Rate':<25} {failure_rate:.1f}%  ({failed_count} cases)")
    print(f"  {'Latency p50':<25} {p50:.2f}s")
    print(f"  {'Latency p95':<25} {p95:.2f}s")
    print(f"  {'Tool Calls (approx)':<25} {total_tool_calls}")
    print(f"  {'API Cost Estimate':<25} ~$0.00 (Groq free tier)")
    print("=" * 50)

    # List failures
    failures = [r for r in results if not r["passed"]]
    if failures:
        print("\n  FAILURES:")
        for f in failures:
            print(f"    - [{f['id']}] {f['name']} ({f['latency_s']}s)")
    else:
        print("\n  All tests passed! ✅")

    print("=" * 50 + "\n")

if __name__ == "__main__":
    asyncio.run(execute_evals())
