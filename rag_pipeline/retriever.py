def retrieve_docs(query, vector_retriever, bm25_retriever):
    vector_docs = vector_retriever.invoke(query)
    bm25_docs = bm25_retriever.invoke(query)
    
    docs = remove_duplicate_docs(vector_docs, bm25_docs)
    
    return docs
    
    
def remove_duplicate_docs(vector_docs, bm25_docs):
    docs = vector_docs+bm25_docs
    seen= set()
    final_docs = []
    
    print(docs)
    
    for doc in docs:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
        else:
            final_docs.append(doc)
    return final_docs