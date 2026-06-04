from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import router_node, reasoning_node, tool_node, safety_guardrail_node

def should_continue(state: AgentState) -> str:
    """
    Conditional edge function that determines whether the agent should execute tools,
    apply safety checks, or exit due to the loop step budget.
    """
    messages = state.get("messages", [])
    step_count = state.get("step_count", 0)

    # 1. Step Budget Guard (limit to 6 loops to prevent runaway API costs)
    if step_count > 6:
        print("Safety Override: Step budget limit exceeded. Forcing end.")
        return "safety"

    if not messages:
        return "safety"

    last_message = messages[-1]

    # 2. If the LLM requested tool calls, route to the tool executor node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # 3. Otherwise, apply safety guardrails and conclude
    return "safety"

# Build the StateGraph
workflow = StateGraph(AgentState)

# Register all nodes
workflow.add_node("router", router_node)
workflow.add_node("reasoning", reasoning_node)
workflow.add_node("tools", tool_node)
workflow.add_node("safety", safety_guardrail_node)

# Set the starting node
workflow.set_entry_point("router")

# Define the edge transitions
workflow.add_edge("router", "reasoning")

# Conditional transition after reasoning
workflow.add_conditional_edges(
    "reasoning",
    should_continue,
    {
        "tools": "tools",
        "safety": "safety"
    }
)

# Unconditional transition from tools back to reasoning loop
workflow.add_edge("tools", "reasoning")

# Unconditional transition from safety node to the end
workflow.add_edge("safety", END)

# Compile the graph
app = workflow.compile()
