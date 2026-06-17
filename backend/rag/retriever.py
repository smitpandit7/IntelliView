def retrieve_context(vectorstore, query: str, k: int = 3) -> str:
    results = vectorstore.similarity_search(query, k=k)
    context = "\n\n".join([doc.page_content for doc in results])
    return context