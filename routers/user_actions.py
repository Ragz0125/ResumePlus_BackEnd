
from fastapi import APIRouter, Depends, HTTPException

from databases import mongo_db
from databases.models.user import User
from routers.auth import get_current_user
from services.conversation_service import ConversationService


router = APIRouter(
    prefix="",
    tags=["User Actions"]
)

#Get the conversations by user id
@router.get('/users/conversations')
def get_conversations_by_user_id(current_user: User=Depends(get_current_user), db = Depends(mongo_db.get_mongo_db)):
    
    conversation_service = ConversationService(db)
    data = conversation_service.get_conversation_user(current_user.id)
    result=[]
    
    for item in data:
        result.append(item)
        
    return result

@router.get("/conversation/{conversation_id}")
def get_conversation_by_id(conversation_id: str, db = Depends(mongo_db.get_mongo_db)):
    
    conversation_service = ConversationService(db)
    data = conversation_service.get_conversation(conversation_id)
    
    if(data.get("user_id")):
        raise HTTPException(status_code=401, detail="Not authorized to access this conversation")

    return data

@router.get("/user/conversation/{conversation_id}")
def get_conversation_id_by_user_id(conversation_id:str, current_user: User=Depends(get_current_user), db = Depends(mongo_db.get_mongo_db)):
    conversation_service = ConversationService(db)
    data = conversation_service.get_auth_conversation(conversation_id, current_user.id)
    if data is None:
        raise HTTPException(status_code=401, detail="Conversation does not exist")
    
    return {
        "data": data
    }
    
@router.get("/user/details")
def get_user_details(current_user: User=Depends(get_current_user)):
    
    return {
        "user_id": current_user.id,
        "user_name": current_user.username
    }