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
    
    Route to 'company_query' ONLY if the user is asking about a SPECIFIC company by name.
    Examples of company_query:
    - "Tell me about Acme Corp"
    - "What does TechFlow Solutions do?"
    - "Show me information on Microsoft"
    
    Route to 'general_query' for:
    - General questions about companies ("what companies are in the database", "list all companies")
    - Non-company questions ("hello", "how are you", "what can you do")
    - Requests for help or information about the system
    
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
    """Intelligent chat node that uses LLM to answer questions based on stored company data.
    
    This node provides ALL company data to the LLM and lets it intelligently 
    respond to any question using only the stored information.
    """
    user_input = state["input"]
    
    # Get all company data from database
    from companies.models import Company
    companies = Company.objects.all()
    
    if not companies.exists():
        return {
            "output": "No companies are currently in the database."
        }
    
    # Format all company data for the LLM
    company_data = "\n\n".join([
        f"Company: {c.name}\n"
        f"Description: {c.description}\n"
        f"Sector: {c.sector}\n"
        f"Financials: {c.financials}"
        for c in companies
    ])
    
    # Create intelligent prompt for LLM
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=f"""
        You are an AI assistant that answers questions about companies using ONLY the provided company database.
        
        COMPANY DATABASE:
        {company_data}
        
        INSTRUCTIONS:
        - Answer the user's question using ONLY the information from the company database above
        - Be helpful and conversational
        - If asked about companies not in the database, say they're not in our records
        - For general questions about "what companies" or "list companies", provide a nice summary
        - For questions about specific companies, provide detailed information
        - For questions asking for "more details" or "tell me more", provide comprehensive information
        - Do not use any external knowledge - only use the database provided above
        """),
        ("human", "{input}")
    ])
    
    # Use LLM to generate intelligent response
    chain = prompt | llm
    response = chain.invoke({"input": user_input})
    
    return {
        "output": response.content
    }

def company_tool_node(state: ChatState) -> ChatState:
    """Return a deterministic answer based solely on the company record."""
    user_input = state["input"]

    # The router decided this *is* a company query⇢ just strip common filler
    company_name = re.sub(
        r"\b(what is|about|tell me about|information on|the company)\b",
        "",
        user_input,
        flags=re.IGNORECASE,
    ).strip()
    print(f"DEBUG: Extracted company name: '{company_name}'")

    try:
        tool_result = get_company_tool.invoke({"name": company_name})
        print(f"DEBUG: Tool result: '{tool_result}'")
    except Exception as exc:
        print(f"DEBUG: Tool error: {exc}")
        return {"output": f"Error looking up '{company_name}'."}

    if tool_result == "Company not found.":
        return {"output": f"Sorry, I couldn't find any information for '{company_name}'."}

    # Otherwise we have a formatted company profile string
    response_text = (
        f"Here’s what we know about {company_name}:\n{tool_result}"
    )
    return {"output": response_text}

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