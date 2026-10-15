from sentence_transformers import SentenceTransformer, util
_dedup_model = SentenceTransformer("BAAI/bge-small-en-v1.5")

def retrieve_context(vectorstore, query: str, k: int = 3) -> str:
    results = vectorstore.similarity_search(query, k=k)
    context = "\n\n".join([doc.page_content for doc in results])
    return context

def is_duplicate_question(new_question:str, asked_question: list, threshold: float = 0.85) -> bool:
    if not asked_question:
        return False
    
    new_embedding = _dedup_model.encode(new_question, convert_to_tensor= True)
    asked_embeddings = _dedup_model.encode(asked_question, convert_to_tensor= True)

    similarities = util.cos_sim(new_embedding, asked_embeddings)[0]
    max_similarity = float(similarities.max())

    print(f"[DEDUP] Max similarity: {max_similarity:.2f}")
    return max_similarity >= threshold