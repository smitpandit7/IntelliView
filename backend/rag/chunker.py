from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_resume(resume_text:str)-> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=60,
        separators=["\n\n", "\n", ".", " ", ]
    )
    chunks = splitter.split_text(resume_text)
    return chunks