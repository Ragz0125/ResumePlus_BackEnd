import json
from typing import Annotated, Optional, TypedDict

from langgraph.prebuilt import ToolNode
from utils import ROUTER_SYSTEM_PROMPT, gpt_model
from langchain.messages import AnyMessage, SystemMessage
from langgraph.graph import StateGraph, END, START, add_messages
from workflow.schema import EmailOutput
from workflow.tools import TOOLS, llm_bind_tools
from langchain_core.runnables import RunnableConfig

class AppState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    
    email_output: EmailOutput | None
    

def router_model(state: AppState,config: RunnableConfig):
    
    response = llm_bind_tools.invoke([SystemMessage(content=ROUTER_SYSTEM_PROMPT),*state["messages"]], config=config,)
    
    return {"messages": [response]}
    
    
def should_continue(state: AppState):
    if(state["messages"][-1].tool_calls):
        return "tools"
    
    return END

def save_tool_output(state: AppState):

    last_message = state["messages"][-1]
    
    print("Checking:", last_message.name)

    if last_message.name == "generate_email":

        email_output = json.loads(last_message.content)

        return {
            "email_output": email_output
        }

    return {}

graph = StateGraph(AppState)

graph.add_node("start", router_model)
graph.add_node("tools", ToolNode(TOOLS))
graph.add_node("save_tool_output", save_tool_output)

graph.add_edge(START, "start")
# IMPORTANT: directly go back to router

graph.add_conditional_edges(
    "start",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

graph.add_edge("tools", "save_tool_output")

graph.add_edge("save_tool_output", "start")

graph_builder = graph.compile()
    

