from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from databases.sql_db import engine
from databases.sql_db import Base
from rag_pipeline.chunk import chunk_material, create_vector_db, get_bm25_retriever, get_vector_retriever
from routers.llm_call import router as llm_router
from routers.auth import router as auth_router
from routers.user_actions import router as actions_router
from fastapi.middleware.cors import CORSMiddleware
from utils import VECTORDB_PATH
#from databases.mongo_db import mongo_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    docs = chunk_material()
    if not Path(VECTORDB_PATH).exists():
        print("Hello")
        create_vector_db(docs)
        bm25_retriever = get_bm25_retriever(docs)
        vector_retriever = get_vector_retriever()
    else:

        print("Loading existing vector DB...")
        vector_retriever = get_vector_retriever()
        bm25_retriever = get_bm25_retriever(docs)
        
    app.state.vector_retriever = vector_retriever
    app.state.bm25_retriever = bm25_retriever

    yield
        
    
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(llm_router)
app.include_router(auth_router)
app.include_router(actions_router)

# print(mongo_db["conversations"])