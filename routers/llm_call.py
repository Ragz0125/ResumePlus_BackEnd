from typing import Optional, TypedDict

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
import shortuuid
from databases.models.conversation import Conversations
from databases.models.user import User
from databases.mongo_db import get_mongo_db
from databases.sql_db import get_db
from routers.auth import get_current_user
from services.conversation_service import ConversationService
from services.user_service import UserService
from utils import gpt_model
from langchain_core.messages import HumanMessage, AIMessage
import datetime
from workflow.agent import graph_builder
from workflow.schema import EmailInput
from services.email_services import send_email

router  = APIRouter(
    prefix="/llm",
    tags=["LLM Call"]
)

class LlmRequest(BaseModel):
    user_id: Optional[int] = None
    query: str
    conversation_id: Optional[str] = None
    date: Optional[str] = None
    
class DbMessageShape(TypedDict):
    role:str
    content: str
    date: Optional[str] = None
    
class HILRequest(BaseModel):
    conversation_id: str
    is_approve: bool
    email_input: Optional[EmailInput] = None
    
    
@router.post("/test")
def test(request: Request):
    print(request.app.state.bm25_retriever)
    print(request.app.state.vector_retriever)
    return{}
    
    
@router.post("/")
def call_llm(request: LlmRequest, appRequest: Request, db = Depends(get_mongo_db), sql_db = Depends(get_db)):
    service = ConversationService(db)
    user_service = UserService(sql_db)
    conversation_id = request.conversation_id
    user_id = request.user_id
    
    dbMessage = DbMessageShape(role="user", content=request.query, date=request.date)
    query = HumanMessage(content=request.query)
    conversation_history = []
    
    if conversation_id != None:
        #retrieve the messages
        conversation_history = service.get_conversation(conversation_id, user_id)
        if(conversation_history is None):
            raise HTTPException(status_code=400, detail="Conversation Id does not exist")
        conversation_history = get_query_list(conversation_history)
        conversation_history.append(query)
        service.update_conversation(user_id, conversation_id, dbMessage)
    else:
        #create conversation_id
        conversation_id = shortuuid.uuid()
        service.insert_new_conversation(user_id, conversation_id, dbMessage)
        if (user_id is not None):
            user_service.create_conversation(conversation_id, user_id)
        conversation_history.append(query)
        
    #interaction with LLM Model    
    result = graph_builder.invoke({"messages": conversation_history},config={
            "configurable": {
                "vector_retriever": appRequest.app.state.vector_retriever,
                "bm25_retriever": appRequest.app.state.bm25_retriever,
            }
        },)
    
    #pushing message into the DB
    dbMessage = DbMessageShape(role="ai", content= result["messages"][-1].content, date=str(datetime.datetime.now()))
    service.update_conversation(user_id, conversation_id, dbMessage)
    
    
    if result.get("email_output"):
        email_output = result["email_output"]
        
        if(user_id is not None):
            user_service.udpate_conversation_hil_status(conversation_id, user_id, True)
        
        return {
            "conversation_id": conversation_id,
            "content": result["messages"][-1].content,
            "email_output": email_output,
            "hil_required": True,
        }
    
    return {
        "conversation_id": conversation_id,
        "content": result["messages"][-1].content
    }
    
    
def get_query_list(conversation_history):
    print(conversation_history)
    list_messages = conversation_history["messages"]
    query_list=[]
    for message in list_messages:
        if message["role"] == "ai":
            query_list.append(AIMessage(content=message["content"]))
        else: 
            query_list.append(HumanMessage(content=message["content"]))
    
    return query_list

@router.post("/hil")
def call_hil(request:HILRequest, current_user: User=Depends(get_current_user), db = Depends(get_mongo_db), sql_db = Depends(get_db)):
    hil_is_approved = request.is_approve
    email_input = request.email_input
    conversation_id = request.conversation_id
    
    service = ConversationService(db)
    user_service = UserService(sql_db)
    
    current_hil_status = user_service.get_conversation_hil_status(conversation_id, current_user.id)
    
    if current_hil_status == False:
       raise HTTPException(status_code=401, detail="Action Denied")
    
    #Update DB, change the HIL status of the conversation id
    user_service.udpate_conversation_hil_status(conversation_id, current_user.id, False)
    
    if(hil_is_approved):
        dbMessage = DbMessageShape(role="user", content="Yes, please send")
        service.update_conversation(current_user.id,conversation_id, dbMessage)
        response  = send_email(current_user, email_input["subject"], email_input["body"])
        
        if(response["success"]):
            #Update Conversation by saying Email has been sent Successfuly
            dbMessage = DbMessageShape(role="ai", content="Email Sent Successfully")
            service.update_conversation(current_user.id, conversation_id, dbMessage)
        
            
    else:
        #Update DB, change the HIL status of the conversation id
        return {
            "data": "Not sent as per your request"
        }
        
    return {
        "data": "Sent successfully"
    }
    
    