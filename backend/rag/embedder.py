from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def build_vectorstore(chunks: list[str]) -> Chroma:
    embedding = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
    )

    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embedding,
        collection_name="resume_context"
    )

    return vectorstore