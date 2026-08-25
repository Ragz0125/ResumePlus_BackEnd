from langchain_community.document_loaders import PyPDFLoader
import re
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from utils import OPENAI_API_KEY

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)

def chunk_material():
    document=PyPDFLoader("Raghav_Rajaraman_Resume.pdf")
    document_content = document.load()[0].page_content
    HEADERS = ["SUMMARY", "EDUCATION", "EXPERIENCE", "RESEARCH", "PROJECTS", "TECHNICAL SKILLS"]
    
    regex_exp = r"^(" + "|".join(map(re.escape, HEADERS)) + r")\s*\*?$"
    clean_text = document_content.split("\n")
    
    chunks = {}
    content = ""
    header = ""
    for line in clean_text:
        if re.fullmatch(regex_exp, line.strip().upper()):
            if header:
                chunks[header] = content
            else:
                #For Details Sections as there in no Header for it
                chunks["Contact Information"] = content
                content = ""
            header = line.strip()
            chunks[header] = ""
        else: 
            content = content + line.strip("\n")
    #For the last section (Technical Skills)
    if(content):
        chunks[header] = content
    
    docs = []
    for chunk in chunks:
        docs.append(Document(metadata={"section": chunk}, page_content=chunks[chunk]))
    
    return docs

def create_vector_db():
    vector_db = Chroma.from_documents(documents=docs, embedding=embedding_model, persist_directory="./resume_db", collection_metadata={"hnsw:space": "cosine"} )
    
def get_vector_retriever():
    db = Chroma(persist_directory="./resume_db", embedding_function=embedding_model)
    return db.as_retriever(search_kwargs={"k":3})
    
def get_bm25_retriever(docs):
    bm25_retreiver = BM25Retriever.from_documents(docs)
    bm25_retreiver.k = 2
    
    return bm25_retreiver
    