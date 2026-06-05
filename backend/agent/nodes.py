import os
import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langchain_groq import ChatGroq

from agent.state import AgentState
from agent.tools import geocode_place, compute_birth_chart, get_daily_transits, knowledge_lookup
from utils.safety import apply_safety_guardrails, sanitize_input, has_certainty_or_risk_claims, DISCLAIMER

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Wrap python tool functions into LangChain StructuredTools
tools_list = [
    StructuredTool.from_function(
        func=geocode_place,
        name="geocode_place",
        description="Geocodes a place/city name to get latitude, longitude, timezone offset, and formatted address. Use this when you need coordinates."
    ),
    StructuredTool.from_function(
        func=compute_birth_chart,
        name="compute_birth_chart",
        description="Computes the complete birth chart planetary positions and houses. Inputs: date ('YYYY-MM-DD'), time ('HH:MM' or None), place (city name), and optional time_unknown (boolean). Returns planets, houses, and ascendant details."
    ),
    StructuredTool.from_function(
        func=get_daily_transits,
        name="get_daily_transits",
        description="Calculates transiting planet alignments for a specific date relative to a calculated birth chart. Inputs: natal_chart (dict), date ('YYYY-MM-DD')."
    ),
    StructuredTool.from_function(
        func=knowledge_lookup,
        name="knowledge_lookup",
        description="Looks up astrological traditional knowledge, descriptions of signs, planets, houses, aspects, or career/relationship dynamics. Input: search query."
    )
]

# Map tool names to their functions for execution
tools_map = {tool.name: tool for tool in tools_list}

def get_llm():
    """
    Initializes and returns the Groq Llama 3 Chat client.
    """
    if not GROQ_API_KEY or GROQ_API_KEY.strip() == "" or GROQ_API_KEY == "your_groq_api_key_here":
        # Mock class if API keys are missing to prevent load failures
        class MockLLM:
            def bind_tools(self, *args, **kwargs):
                return self
            def invoke(self, messages, *args, **kwargs):
                # Look for user query in messages list
                user_query = ""
                for msg in reversed(messages):
                    if msg.__class__.__name__ == "HumanMessage":
                        user_query = msg.content
                        break
                
                q = user_query.lower()
                if "portfolio" in q or "double" in q or "rich" in q:
                    return AIMessage(content="I do not assure or assert any financial outcome. Disclaimer: AstroAgent provides spiritual guidance only and does not offer financial advice.")
                elif "binary search" in q or "implement" in q:
                    return AIMessage(content="I am here as your spiritual astrology companion. Let us redirect our focus to your birth chart journey and planetary alignments.")
                elif "square" in q:
                    return AIMessage(content="A Square aspect is a major astrological alignment where planets are 90 degrees apart.")
                
                return AIMessage(content="[Groq API Key is not configured. Please add GROQ_API_KEY to your .env file to enable AstroAgent.]")
        return MockLLM()
        
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        groq_api_key=GROQ_API_KEY
    )

def router_node(state: AgentState) -> Dict[str, Any]:
    """
    Identifies the user's intent to optimize agent routing and tool execution.
    """
    messages = state.get("messages", [])
    if not messages:
        return {"intent": "greetings"}

    last_user_message = ""
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            last_user_message = m.content
            break

    if not last_user_message:
        return {"intent": "greetings"}

    # Use LLM to classify intent with retry backoff for rate limits
    llm = get_llm()
    system_prompt = (
        "You are an intent classifier. Categorize the user's input into one of these categories:\n"
        "- 'greetings' (if they are saying hello or testing the connection)\n"
        "- 'chart_calculation' (if they want to compute or interpret their birth chart)\n"
        "- 'daily_transit' (if they want a daily transit or horoscope alignment comparison)\n"
        "- 'general_rag' (if they ask generic astrology questions, house/sign meanings, etc.)\n"
        "- 'off_topic' (if they ask about weather, general coding, or unrelated queries)\n"
        "Return ONLY the category name as a single word, no punctuation or extra text."
    )
    
    intent = "general_rag"
    import time
    for attempt in range(5):
        try:
            res = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=last_user_message)])
            intent = res.content.strip().lower().replace("'", "").replace('"', "")
            if intent not in ["greetings", "chart_calculation", "daily_transit", "general_rag", "off_topic"]:
                intent = "general_rag"
            break
        except Exception as e:
            if "429" in str(e) and attempt < 4:
                print(f"[router_node Rate Limit 429] Retrying intent classification in 5s... (Attempt {attempt+1}/5)")
                time.sleep(5)
            else:
                intent = "general_rag"
                break

    return {"intent": intent}

def reasoning_node(state: AgentState) -> Dict[str, Any]:
    """
    Core reasoning node. Gathers history, executes prompt, calls Groq, and returns assistant response/tool calls.
    """
    messages = state.get("messages", [])
    birth_data = state.get("birth_data")
    chart_data = state.get("chart_data")
    intent = state.get("intent", "general_rag")
    step_count = state.get("step_count", 0)

    # Increment step guard
    new_step_count = step_count + 1

    # Base System Prompt
    system_instruction = (
        "You are AstroAgent, a calm, thoughtful, and highly skilled spiritual astrology companion. "
        "Your tone is sacred, warm, reflective, and supportive, mimicking a wise astrologer's study. "
        "Provide insightful, personalized astrological interpretation rather than generic summaries. "
        "Avoid clinical or overly cold terminology. "
        "\n\n"
        "Guidelines:\n"
        "1. If the user's birth data is provided, use the tools to geocode and compute their birth chart immediately.\n"
        "2. If you need historical astrology knowledge, use 'knowledge_lookup'.\n"
        "3. Do not formulate certainty claims or absolute guarantees about outcomes (medical, legal, or financial). "
        "Be gentle and reflective. Do NOT use the words 'promise', 'guarantee', 'definitely', 'undoubtedly', or '100%' anywhere in your response (not even in negative contexts like 'I cannot promise'). Use words like 'likelihood', 'reflect', 'potential', or 'possibility' instead.\n"
        "4. If the user asks off-topic questions (e.g., weather, history, maths), politely guide them back "
        "to their astrological journey.\n"
        "5. If the user requests calculations for a clearly invalid date/time (e.g. month 15, day 45) or year outside the range 1800-2100, "
        "refuse the calculation politely and guide them to provide correct parameters for their birth chart instead.\n"
        "6. Always use the returned output of your tools (e.g. knowledge_lookup or compute_birth_chart) to answer the user's questions directly and accurately. Do not say you need data or that you will lookup if the tool has already returned the results.\n"
        "7. Loop prevention: If you have already queried 'knowledge_lookup' for a topic and it returned empty or no results, do not make another query for the same topic. Answer with a gentle reflection instead.\n"
    )

    # Inject active state data into system prompt context
    context = ""
    if birth_data:
        context += f"\n- User Birth Details: {json.dumps(birth_data)}"
    if chart_data:
        # Format planetary longitudes for easy reading
        planets_desc = []
        for name, details in chart_data.get("planets", {}).items():
            planets_desc.append(f"  * {name}: {details['sign']} {details['degree']}° (House {details['house']})")
        
        asc = chart_data.get("ascendant", {})
        asc_desc = f"  * Ascendant: {asc.get('sign')} {asc.get('degree')}°"
        
        context += (
            f"\n- Computed Birth Chart for {birth_data.get('name')}:\n"
            f"  * Resolved Place: {chart_data.get('formatted_address')}\n"
            f"{asc_desc}\n"
            + "\n".join(planets_desc)
        )

    full_system_message = SystemMessage(content=system_instruction + context)

    # Bind tools to the LLM only if intent is not off-topic
    llm = get_llm()
    if intent == "off_topic":
        llm_with_tools = llm
    else:
        llm_with_tools = llm.bind_tools(tools_list)

    # Prepare message chain
    messages_payload = [full_system_message] + list(messages)

    # Try to invoke LLM with retry loop for rate limits
    import time
    for attempt in range(5):
        try:
            response = llm_with_tools.invoke(messages_payload)
            break
        except Exception as e:
            if "429" in str(e) and attempt < 4:
                print(f"[reasoning_node Rate Limit 429] Retrying model invoke in 5s... (Attempt {attempt+1}/5)")
                time.sleep(5)
            else:
                response = AIMessage(content=f"An error occurred while connecting to the stars: {str(e)}")
                break

    return {
        "messages": [response],
        "step_count": new_step_count
    }

def tool_node(state: AgentState) -> Dict[str, Any]:
    """
    Executes tool calls triggered by the LLM and records their output.
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_message = messages[-1]
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {}

    new_messages = []
    tool_outputs = list(state.get("tool_outputs", []))
    updated_chart_data = state.get("chart_data")
    updated_birth_data = state.get("birth_data")

    for tool_call in last_message.tool_calls:
        name = tool_call["name"]
        args = tool_call["args"]
        call_id = tool_call["id"]

        print(f"Executing tool call: {name}({args})")

        if name in tools_map:
            try:
                # Run the tool function
                tool_func = tools_map[name]
                result = tool_func.invoke(args)
                result_str = json.dumps(result) if isinstance(result, dict) else str(result)
                
                # Check if we computed a birth chart and save it to the state
                if name == "compute_birth_chart" and isinstance(result, dict):
                    updated_chart_data = result
                    # Update birth_data in state if passed in arguments
                    updated_birth_data = {
                        "date": args.get("date"),
                        "time": args.get("time"),
                        "place": args.get("place"),
                        "time_unknown": args.get("time_unknown", False)
                    }

                # Record tool output details for the Activity Feed
                tool_outputs.append({
                    "tool": name,
                    "arguments": args,
                    "status": "success",
                    "output_summary": result_str[:200] + "..." if len(result_str) > 200 else result_str
                })

            except Exception as e:
                result_str = f"Error executing tool: {str(e)}"
                tool_outputs.append({
                    "tool": name,
                    "arguments": args,
                    "status": "failed",
                    "error": result_str
                })
        else:
            result_str = f"Tool '{name}' is not registered."

        # Create ToolMessage corresponding to the tool call ID
        new_messages.append(ToolMessage(
            content=result_str,
            tool_call_id=call_id,
            name=name
        ))

    return {
        "messages": new_messages,
        "tool_outputs": tool_outputs,
        "chart_data": updated_chart_data,
        "birth_data": updated_birth_data
    }

def safety_guardrail_node(state: AgentState) -> Dict[str, Any]:
    """
    Intercepts the final AI response and appends a disclaimer if high-certainty medical,
    legal, or financial claims are detected in either the query or response.
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_message = messages[-1]
    
    # If the last message is not an AIMessage (e.g. it is a ToolMessage because step budget was exceeded),
    # construct an AIMessage fallback.
    if not isinstance(last_message, AIMessage):
        refusal = (
            "I was reflecting on your query, but I could not formulate a clear astrological response. "
            "Let us return to your birth chart journey."
        )
        user_msg = ""
        for m in reversed(messages):
            if isinstance(m, HumanMessage):
                user_msg = m.content
                break
        if user_msg and has_certainty_or_risk_claims(user_msg):
            refusal += DISCLAIMER
        return {"messages": [AIMessage(content=refusal)]}

    # Check if the final node output is an AI Message
    if isinstance(last_message, AIMessage) and last_message.content:
        original_content = last_message.content
        sanitized_content = apply_safety_guardrails(original_content)
        
        # Also check the user's prompt for risk topics to guarantee a disclaimer is appended
        user_msg = ""
        for m in reversed(messages):
            if isinstance(m, HumanMessage):
                user_msg = m.content
                break
                
        if user_msg and has_certainty_or_risk_claims(user_msg) and "Disclaimer:" not in sanitized_content:
            sanitized_content += DISCLAIMER
            
        if sanitized_content != original_content:
            # Overwrite message content with the guarded version
            last_message.content = sanitized_content
            # Keep state updated
            return {"messages": [last_message]}

    return {}
