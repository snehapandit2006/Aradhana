import os
import json
import asyncio
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
    """Asserts that geocoding output coordinates fall within a tolerance range."""
    place = birth_data["place"]
    try:
        res = geocode_place(place)
        lat_diff = abs(res["lat"] - expected_lat)
        lon_diff = abs(res["lon"] - expected_lon)
        passed = lat_diff <= tolerance and lon_diff <= tolerance
        details = f"Geocoded: ({res['lat']:.4f}, {res['lon']:.4f}) vs Expected: ({expected_lat}, {expected_lon})"
        return passed, details
    except Exception as e:
        return False, f"Geocoding failed: {str(e)}"

def run_chart_math_assertion(birth_data, assertion):
    """Computes birth chart and asserts planetary longitudes match expected within tolerance, handling wraparounds."""
    try:
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
                failed_details.append(f"{planet}: expected {expected_lon}°, got {computed_lon}° (diff: {wrap_diff:.2f}° > {tolerance}°)")
                
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
        # Run compiled LangGraph synchronously (invoking)
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
                # Check if it guides the user back or refuses/guides
                keywords = ["astrologer", "journey", "guidance", "stars", "horoscope", "chart", "off-topic", "topic"]
                if not any(k in response_text.lower() for k in keywords):
                    passed = False
                    failed_details.append("Response did not redirect or mention astrology limits.")

            elif ass_type == "contains_substrings":
                for sub in ass.get("substrings", []):
                    if sub.lower() not in response_text.lower():
                        passed = False
                        failed_details.append(f"Missing expected substring: '{sub}'")

        details = f"Response: {response_text[:120]}..." if passed else f"Failed: {', '.join(failed_details)}. Response: {response_text[:120]}..."
        return passed, details

    except Exception as e:
        return False, f"Agent invocation crashed: {str(e)}"

async def execute_evals():
    """Main function loading and running all test evaluations."""
    print("=== ASTROAGENT EVALUATION HARNESS ===")
    
    # Check for keys
    if not os.getenv("GROQ_API_KEY") or not os.getenv("GOOGLE_GEOCODING_API_KEY"):
        print("WARNING: API keys are not configured. Assertions involving live APIs may fail.")

    if not os.path.exists(EVALS_FILE):
        print(f"Error: Golden set file not found at {EVALS_FILE}")
        return

    test_cases = []
    with open(EVALS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                test_cases.append(json.loads(line.strip()))

    passed_count = 0
    total_count = len(test_cases)

    for i, tc in enumerate(test_cases):
        tc_id = tc["id"]
        tc_name = tc["name"]
        input_type = tc["input_type"]
        
        print(f"\n[{i+1}/{total_count}] Running: {tc_name} ({tc_id})...")
        
        if input_type == "birth_data":
            # Process multiple assertions if present
            assertions = tc.get("assertions", [])
            passed = True
            details_list = []
            for ass in assertions:
                ass_type = ass["type"]
                if ass_type == "coordinate_within_tolerance":
                    lat = ass["lat"]
                    lon = ass["lon"]
                    tol = ass["tolerance"]
                    p, d = run_coordinate_assertion(tc["input"], lat, lon, tol)
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
            message = tc["input"]["message"]
            passed, details = await run_chat_assertions(message, tc["assertions"])
        else:
            passed, details = False, "Unknown test input type."

        if passed:
            passed_count += 1
            print(f"  --> PASS: {details}")
        else:
            print(f"  --> FAIL: {details}")

    print("\n=== EVALUATION REPORT SUMMARY ===")
    print(f"Total Tests Executed: {total_count}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {total_count - passed_count}")
    success_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
    print(f"Success Rate: {success_rate:.2f}%")
    print("=================================")

if __name__ == "__main__":
    asyncio.run(execute_evals())
