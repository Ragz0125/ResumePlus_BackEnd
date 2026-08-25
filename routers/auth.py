from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from databases.models.user import User
from databases.sql_db import get_db
from utils import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, get_hashed_password, get_user, verify_password
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

router = APIRouter(
    prefix="",
    tags=['auth']
)

class UserRequest(BaseModel):
    username: str = Field(min_length=4)
    password: str = Field(min_length=6)
    email: str 
    name: str = Field(min_length=5)


@router.post("/signup")
def signup_user(request: UserRequest, db = Depends(get_db)):
    #Check if username already exists
    user_exists = get_user(db, request.username)
    
    if(user_exists):
        raise HTTPException(status_code=400, detail="User already exists")
    #Then Create new user
    hashed_password = get_hashed_password(request.password)
    user = User(name=request.name, username=request.username, password=request.password,hashed_password=hashed_password, email=request.email)
    db.add(user)
    db.commit()
    db.close()
    return {
        "message": "User created successfully",
        "data": user
    }
    

@router.post("/login")
def get_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = get_user(db, form_data.username)
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username")
    
    if not verify_password(user.hashed_password, form_data.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    access_token = create_access_token({
        "sub": str(user.id)
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
@router.get("/user")
def get_current_user(token: str= Depends(oauth2_scheme), db =Depends(get_db)):
    user_id = decode_access_token(token)
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
    
def create_access_token(data:dict):
    to_encode= data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    to_encode.update({
        "exp": expire
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt

def decode_access_token(token: str):
    
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            ALGORITHM
        )
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid Token")
        
        return user_id
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    
    