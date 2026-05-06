from sentence_transformers import SentenceTransformer
import chromadb
from ollama import Client

# =========================
# OLLAMA CLIENT
# =========================

client_ollama = Client(host='http://127.0.0.1:11434')

# =========================
# EMBEDDING MODEL
# =========================

model = SentenceTransformer("BAAI/bge-base-en")

# =========================
# CHROMADB
# =========================

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection(name="rag-demo")

# =========================
# USER QUERY
# =========================

query = input("\nAsk something: ")

# =========================
# EMBED QUERY
# =========================

query_embedding = model.encode([query])[0]

# =========================
# RETRIEVE CHUNKS
# =========================

results = collection.query(
    query_embeddings=[query_embedding.tolist()],
    n_results=5
)

# =========================
# SHOW RETRIEVED CHUNKS
# =========================

print("\n=========================")
print("RETRIEVED CHUNKS")
print("=========================")

for i, doc in enumerate(results["documents"][0]):

    print(f"\nChunk {i+1}:\n")

    print(doc)

    print("\nSOURCE:")

    print(results["metadatas"][0][i]["source"])

    print("\n-------------------------")

# =========================
# COMBINE CONTEXT
# =========================

context = "\n".join(results["documents"][0])

# =========================
# PROMPT
# =========================

prompt = f"""
You are an AI research assistant.

Answer the user's question using the provided context.

If the context does not contain enough information,
clearly say that.

Provide a detailed and helpful response.

Context:
{context}

Question:
{query}
"""

# =========================
# OLLAMA RESPONSE
# =========================

response = client_ollama.chat(
    model="llama3",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

# =========================
# FINAL ANSWER
# =========================

print("\n=========================")
print("AI ANSWER")
print("=========================\n")

print(response["message"]["content"])