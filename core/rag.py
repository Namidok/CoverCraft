import os
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# Embedding model — runs locally, no API needed
MODEL_NAME = "all-MiniLM-L6-v2"
CHROMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "chromadb")

embedder = SentenceTransformer(MODEL_NAME)

client = chromadb.PersistentClient(path=CHROMA_DIR)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " "],
)


def get_or_create_collection(name: str):
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def add_document(collection_name: str, text: str, metadata: dict = None):
    """Split text into chunks, embed, and store in ChromaDB."""
    collection = get_or_create_collection(collection_name)
    chunks = splitter.split_text(text)

    ids = [f"{collection_name}_{i}" for i in range(len(chunks))]
    embeddings = embedder.encode(chunks).tolist()
    metadatas = [metadata or {} for _ in chunks]

    # Clear existing docs with same prefix
    existing = collection.get()
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)


def query_collection(collection_name: str, query: str, n_results: int = 5):
    """Search ChromaDB for relevant chunks."""
    collection = get_or_create_collection(collection_name)

    if collection.count() == 0:
        return []

    query_embedding = embedder.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=min(n_results, collection.count()),
    )

    return results["documents"][0] if results["documents"] else []


def add_cv(text: str):
    """Store CV in the 'cv' collection."""
    return add_document("srikar_cv", text, {"type": "cv"})


def add_jd(text: str, company: str, role: str):
    """Store a job description in the 'jds' collection."""
    return add_document(
        f"jd_{company.lower().replace(' ', '_')}",
        text,
        {"type": "jd", "company": company, "role": role},
    )


def get_cv_context(query: str, n: int = 5):
    """Retrieve relevant CV chunks."""
    return query_collection("srikar_cv", query, n)


def get_jd_context(company: str, query: str, n: int = 5):
    """Retrieve relevant JD chunks for a company."""
    collection_name = f"jd_{company.lower().replace(' ', '_')}"
    return query_collection(collection_name, query, n)