from datetime import datetime

from fastapi import Request
import requests
from langchain.messages import HumanMessage, SystemMessage
from langchain.tools import tool
from rag_pipeline.retriever import retrieve_docs
from utils import GIT_HUB_API, PROJECTS_SYSTEM_PROMPT, RAG_SYSTEM_PROMPT, gpt_model, EMAIL_SYSTEM_PROMPT
from workflow.schema import EmailOutput
from langchain_core.runnables import RunnableConfig


llm_email_output = gpt_model.with_structured_output(schema=EmailOutput)

@tool
def generate_email(context: str):
    """Generate email when context is provided"""
    
    print("Generating Email")
    
    messages = [SystemMessage(content=EMAIL_SYSTEM_PROMPT), HumanMessage(content=context)]
    
    response = llm_email_output.invoke(messages)
    print("Email:", response )
    
    return response

@tool
def generate_rag(query, config: RunnableConfig):
    """Retreive docs when asked about the candidate"""
    
    print("RAG Tool ", query)

    vector_retriever = config["configurable"]["vector_retriever"]
    bm25_retriever = config["configurable"]["bm25_retriever"]
    
    docs = retrieve_docs(query, vector_retriever, bm25_retriever)
    
    result = gpt_model.invoke([SystemMessage(content=RAG_SYSTEM_PROMPT.format(query=query, context_docs=docs))])
    
    return result.content

@tool
def get_projects():
    """Retrieve personal project from github. This function will be used only when the user asks about the personal projects or projects 
    that the candidate has worked on"""
    
    response = requests.get(GIT_HUB_API)
    
    projects = []
    for project in response.json():
        project_created_date = datetime.fromisoformat(project["created_at"])
        if(project_created_date.year > 2022):
            projects.append({
            "url" : project["html_url"],
            "created_date": project["created_at"],
            "description": project["description"]
            })
            
    messages = [SystemMessage(content=PROJECTS_SYSTEM_PROMPT), HumanMessage(content=str(projects))] 
    result = gpt_model.invoke(messages)
       
    return result.content


TOOLS =[generate_email, generate_rag, get_projects]

llm_bind_tools = gpt_model.bind_tools(TOOLS)