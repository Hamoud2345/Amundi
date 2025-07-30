# ── agent/langgraph_agent.py ────────────────────────────────────────────
from langgraph.graph import StateGraph, END
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import SystemMessage
from typing import TypedDict
from .llm_factory import make_llm
from .tools import get_company_tool
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
import re

llm = make_llm()

# ── State ────────────────────────────────────────────────────────────────
class ChatState(TypedDict):
    input: str
    output: str
    route: str

# ── Router ───────────────────────────────────────────────────────────────
class Router(BaseModel):
    """Route a user query to the appropriate tool or agent."""
    datasource: str = Field(
        description="Given a user query, route it to 'company_query' for company-related questions or 'general_query' for all others.",
        enum=["company_query", "general_query"],
    )

router_prompt = PromptTemplate(
    template="""
    You are an expert at routing a user's request to the appropriate data source.
    Based on the user's query, route them to 'company_query' or 'general_query'.

    User query: {input}
    """,
    input_variables=["input"],
)

# Try to use structured_output helper; fallback to parser if not supported
try:
    router_chain = router_prompt | llm.with_structured_output(Router)
except NotImplementedError:
    parser = PydanticOutputParser(pydantic_object=Router)
    router_chain = router_prompt | llm | parser

# ── Nodes ────────────────────────────────────────────────────────────────
def route_message(state: ChatState) -> dict:
    """Routes the user's message to the appropriate node."""
    user_input = state["input"]
    route = router_chain.invoke({"input": user_input})
    print(f"DEBUG: Router decided: {route.datasource}")
    return {"route": route.datasource}

def chat_node(state: ChatState) -> ChatState:
    """LLM node for general chat."""
    PROMPT = ChatPromptTemplate.from_messages([
        SystemMessage(content="You are a helpful assistant."),
        ("human", "{input}")
    ])
    chain = PROMPT | llm
    response = chain.invoke({"input": state["input"]})
    return {"output": response.content}

def company_tool_node(state: ChatState) -> ChatState:
    """Tool node that gets company information and generates AI response."""
    user_input = state["input"]
    
    # Simplified extraction: the router already decided it's a company query
    company_name = re.sub(r'\b(what is|about|tell me about|information on|the company)\b', '', user_input, flags=re.IGNORECASE).strip()
    print(f"DEBUG: Extracted company name: '{company_name}'")
    
    try:
        tool_result = get_company_tool.invoke({"name": company_name})
        print(f"DEBUG: Tool result: '{tool_result}'")
        
        enhanced_prompt = f"""You are CompanyBot. A user asked: "{state['input']}"

Here is the company information from our database:
{tool_result}

Please provide a helpful response based on this information. If the company was not found, let the user know."""
        
        response = llm.invoke(enhanced_prompt)
        return {"output": response.content}
        
    except Exception as e:
        print(f"DEBUG: Tool error: {e}")
        return {"output": f"Error looking up '{company_name}'."}

# ── Graph ────────────────────────────────────────────────────────────────
def decide_route(state: ChatState):
    """Helper function to route from the router to the correct node."""
    if state["route"] == "company_query":
        return "get_company_info"
    return "chat"

graph = StateGraph(ChatState)
graph.add_node("router", route_message)
graph.add_node("chat", chat_node)
graph.add_node("get_company_info", company_tool_node)

graph.set_entry_point("router")
graph.add_conditional_edges(source="router", path=decide_route, path_map={
    "get_company_info": "get_company_info",
    "chat": "chat"
})
graph.add_edge("chat", END)
graph.add_edge("get_company_info", END)

app = graph.compile()

def run_chat(message: str) -> str:
    """Used by the Django /chat/ view."""
    # The `app` is our compiled graph
    result = app.invoke({"input": message})
    return result["output"]