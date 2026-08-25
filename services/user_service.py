

from databases.models.conversation import Conversations
from databases.models.user import User


class UserService():
    
    def __init__(self, db):
        self.db = db
        
    def create_conversation(self, conversation_id, user_id):
        conversation = Conversations(id=conversation_id, user_id=user_id)
        self.db.add(conversation)
        self.db.commit()
        self.db.close()
    
    def udpate_conversation_hil_status(self, conversation_id, user_id, status):
        conversation: Conversations = self.db.query(Conversations).filter(Conversations.id == conversation_id, Conversations.user_id == user_id).first()
        conversation.hil_activity_status = status
        print(conversation.hil_activity_status)
        self.db.commit()
        self.db.refresh(conversation)
    
    def get_conversation_hil_status(self, conversation_id, user_id):
        conversation: Conversations = self.db.query(Conversations).filter(Conversations.id == conversation_id, Conversations.user_id == user_id).first()
    
        return conversation.hil_activity_status