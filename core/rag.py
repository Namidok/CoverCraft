import os
import re
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter

CHROMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "chromadb")

client = chromadb.PersistentClient(path=CHROMA_DIR)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " "],
)


def sanitize_name(name: str) -> str:
    clean = re.sub(r'[^a-z0-9-]', '-', name.lower())
    clean = re.sub(r'-+', '-', clean)
    clean = clean.strip('-')
    if len(clean) < 3:
        clean = clean + "job"
    clean = clean[:40].rstrip('-')
    return clean


def get_or_create_collection(name: str):
    safe_name = sanitize_name(name)
    return client.get_or_create_collection(
        name=safe_name,
        metadata={"hnsw:space": "cosine"},
    )


def clean_text(text: str) -> str:
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'[^\x20-\x7e\n\r\t\u00c0-\u024f]', '', text)
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        printable = sum(1 for c in line if c.isprintable())
        if printable / len(line) > 0.85:
            lines.append(line)
    return '\n'.join(lines).strip()


def add_document(collection_name: str, text: str, metadata: dict = None):
    collection = get_or_create_collection(collection_name)
    text = clean_text(text)
    chunks = splitter.split_text(text)

    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    ids = [f"{sanitize_name(collection_name)}_{i}" for i in range(len(chunks))]
    metadatas = [metadata or {} for _ in chunks]

    collection.add(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
    )
    return len(chunks)


def query_collection(collection_name: str, query: str, n_results: int = 5):
    collection = get_or_create_collection(collection_name)
    if collection.count() == 0:
        return []
    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
    )
    return results["documents"][0] if results["documents"] else []


def add_cv(text: str):
    return add_document("user-cv", text, {"type": "cv"})


def add_jd(text: str, company: str, role: str):
    return add_document(
        f"jd-{company.lower().replace(' ', '-')[:40]}",
        text,
        {"type": "jd", "company": company, "role": role},
    )


def get_cv_context(query: str, n: int = 5):
    return query_collection("user-cv", query, n)


def get_jd_context(company: str, query: str, n: int = 5):
    collection_name = f"jd-{company.lower().replace(' ', '-')[:40]}"
    return query_collection(collection_name, query, n)