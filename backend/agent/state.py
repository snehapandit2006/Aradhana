from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # Chat messages history (annotated with add_messages so new messages append automatically)
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Birth details (name, date, time, place, time_unknown)
    birth_data: Optional[Dict[str, Any]]
    
    # Computed birth chart data (planets positions, house cusps, ascendant)
    chart_data: Optional[Dict[str, Any]]
    
    # User's detected intent (e.g., 'chart_calculation', 'daily_transit', 'general_rag', 'off_topic', etc.)
    intent: Optional[str]
    
    # Track outputs from tool executions
    tool_outputs: List[Dict[str, Any]]
    
    # Protection against infinite loops (max 6 loops allowed)
    step_count: int
