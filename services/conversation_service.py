class ConversationService:
    def __init__(self, db):
        self.conversations = db["conversations"]
        
    def get_conversation(self, conversation_id, user_id=None):
        conversation_history= {}
        if(user_id is not None):
             conversation_history = self.conversations.find_one({"conversation_id": conversation_id, "user_id": user_id}, {"_id": 0})
        else:
            conversation_history = self.conversations.find_one({"conversation_id": conversation_id}, {"_id": 0})
        return conversation_history
    
    def insert_new_conversation(self, user_id, conversation_id, message):
        return self.conversations.insert_one({
            "user_id": user_id,
            "conversation_id": conversation_id,
            "messages": [message]
        })
    
    def update_conversation(self, user_id, conversation_id, message):
        return self.conversations.update_one({
            "user_id": user_id,
            "conversation_id":conversation_id},
            {
                "$push": {
                    "messages": message,
                }
            }
            )
        
    def get_conversation_user(self, user_id):
        return self.conversations.find({"user_id": user_id},{"_id": 0})
    
    def get_auth_conversation(self, conversation_id, user_id):
        return self.conversations.find_one({"conversation_id": conversation_id, "user_id":user_id}, {"_id":0})
        