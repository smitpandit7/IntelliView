# test.py
from parsers.resume_parser import parse_resume, extract_text_from_pdf
from parsers.jd_parser import parse_jd
from rag.chunker import chunk_resume
from rag.embedder import build_vectorstore
from rag.retriever import retrieve_context

# 1. Parse
resume_json = parse_resume("sample_resume.pdf")
print("Resume parsed:", resume_json["name"])

# 2. Chunk
resume_text = extract_text_from_pdf("sample_resume.pdf")
chunks = chunk_resume(resume_text)
print(f"Chunks created: {len(chunks)}")

# 3. Embed
vectorstore = build_vectorstore(chunks)
print("Vectorstore built")

# 4. Retrieve
context = retrieve_context(vectorstore, "What projects has this candidate built?")
print("Retrieved context:", context[:200])