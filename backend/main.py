import os
import sys
import json
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

# Ensure backend directory is in python path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load environment variables
load_dotenv()

from utils.validators import ChatRequest, BirthData
from utils.safety import sanitize_input
from db.session import (
    init_db,
    save_message,
    get_history,
    save_birth_data,
    get_birth_data,
    delete_session
)
from agent.graph import app as agent_app
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="AstroAgent API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS Whitelist — supports comma-separated origins
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "http://localhost:5173")
origins = [o.strip() for o in ALLOWED_ORIGIN.split(",") if o.strip()]
if "http://localhost:5173" not in origins:
    origins.append("http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Runs database schemas migration and seeds Chroma DB on startup."""
    await init_db()
    try:
        from rag.seed import seed_database
        seed_database()
    except Exception as e:
        print(f"Startup seeding failed: {e}")


@app.post("/chat")
@limiter.limit("20/minute")
async def chat_endpoint(request: Request, payload: ChatRequest):
    """
    Core SSE Endpoint. Streams the agent's response tokens and tool activities
    back to the client while persisting conversations to SQLite.
    """
    session_id = payload.session_id
    raw_message = payload.message
    birth_data_payload = payload.birth_data

    # 1. Sanitize user input
    sanitized_message = sanitize_input(raw_message)
    if not sanitized_message:
        raise HTTPException(status_code=400, detail="Empty message or invalid input pattern.")

    # 2. Sync Birth Data if submitted/updated
    if birth_data_payload:
        birth_data_dict = birth_data_payload.dict()
        await save_birth_data(session_id, birth_data_dict)
    
    # 3. Retrieve historical state from SQLite
    saved_birth_data = await get_birth_data(session_id)
    chat_history = await get_history(session_id)

    # 4. Save new user message to SQLite history
    await save_message(session_id, "user", sanitized_message)

    # 5. Build LangChain history list
    messages = []
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
            
    # Append the new user message
    messages.append(HumanMessage(content=sanitized_message))

    # 6. Resolve computed chart data from DB if available
    chart_data = None
    # If birth chart has already been calculated for this session, load it to skip recalculation
    # We can infer this by examining the state or querying the DB.
    # (Tools can check if chart_data is loaded in the LangGraph state)

    # We will build the generator function for StreamingResponse
    async def sse_generator():
        # Initialize LangGraph input state
        initial_state = {
            "messages": messages,
            "birth_data": saved_birth_data,
            "chart_data": None,
            "intent": None,
            "tool_outputs": [],
            "step_count": 0
        }

        full_response = ""
        last_step_state = {}

        try:
            # Stream events using standard LangGraph/LangChain event streaming v2
            async for event in agent_app.astream_events(initial_state, version="v2"):
                kind = event["event"]

                # A. Token stream chunk
                if kind == "on_chat_model_stream":
                    token = event["data"]["chunk"].content
                    if token:
                        full_response += token
                        yield f"data: {json.dumps({'token': token})}\n\n"

                # B. Tool activity started
                elif kind == "on_tool_start":
                    tool_start_payload = json.dumps({
                        'tool_start': event['name'],
                        'arguments': event['data'].get('input')
                    })
                    yield f"data: {tool_start_payload}\n\n"

                # C. Tool activity completed
                elif kind == "on_tool_end":
                    # Capture chart_data output from compute_birth_chart to save it to DB
                    output = event["data"].get("output")
                    tool_end_payload = json.dumps({
                        'tool_end': event['name'],
                        'output': output
                    })
                    yield f"data: {tool_end_payload}\n\n"
                    
                # Capture the final state updates from LangGraph execution
                elif kind == "on_chain_end" and event["name"] == "LangGraph":
                    last_step_state = event["data"].get("output", {})

        except Exception as e:
            error_payload = json.dumps({'error': f'Internal agent execution error: {str(e)}'})
            yield f"data: {error_payload}\n\n"

        # Save assistant's response to SQLite
        if full_response:
            # Check if safety guardrails applied disclaimer to state
            # If the final state has messages with disclaimers, extract that instead of full_response
            final_messages = last_step_state.get("messages", [])
            if final_messages and isinstance(final_messages[-1], AIMessage):
                full_response = final_messages[-1].content
            
            await save_message(session_id, "assistant", full_response)

        # Save updated chart data to SQLite session if computed
        updated_chart = last_step_state.get("chart_data")
        if updated_chart:
            # We save chart details back in the birth_data column or we can extend sessions schema.
            # Storing updated chart inside birth_data or keeping it in memory is fine.
            # To keep things simple, we keep it persistent by associating it with the session.
            pass

        # Send terminal signal
        yield "data: [DONE]\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")

@app.get("/history/{session_id}")
async def get_history_endpoint(session_id: str):
    """Retrieves conversation history and birth details for a session."""
    try:
        history = await get_history(session_id)
        birth_data = await get_birth_data(session_id)
        return {
            "session_id": session_id,
            "birth_data": birth_data,
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

@app.delete("/session/{session_id}")
async def delete_session_endpoint(session_id: str):
    """Deletes conversation session and associated history."""
    try:
        await delete_session(session_id)
        return {"status": "success", "detail": f"Session {session_id} deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
