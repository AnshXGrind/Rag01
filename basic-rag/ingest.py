import os
from sentence_transformers import SentenceTransformer
import chromadb
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# =========================
# EMBEDDING MODEL
# =========================

model = SentenceTransformer("BAAI/bge-base-en")

# =========================
# CHROMADB
# =========================

client = chromadb.PersistentClient(path="./chroma_db")

# Delete old collection
try:
    client.delete_collection("rag-demo")
except:
    pass

collection = client.get_or_create_collection(name="rag-demo")

# =========================
# TEXT SPLITTER
# =========================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)

all_chunks = []
all_metadata = []

# =========================
# READ ALL FILES
# =========================

for file_name in os.listdir("data"):

    path = os.path.join("data", file_name)

    text = ""

    print(f"\nProcessing: {file_name}")

    # =========================
    # TXT FILES
    # =========================

    if file_name.endswith(".txt"):

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

    # =========================
    # PDF FILES
    # =========================

    elif file_name.endswith(".pdf"):

        reader = PdfReader(path)

        for page_num, page in enumerate(reader.pages):

            extracted = page.extract_text()

            if extracted:

                text += extracted + "\n"

    else:
        continue

    # =========================
    # CHUNKING
    # =========================

    chunks = splitter.split_text(text)

    for chunk in chunks:

        all_chunks.append(chunk)

        all_metadata.append({
            "source": file_name
        })

# =========================
# CREATE EMBEDDINGS
# =========================

print("\nCreating embeddings...")

embeddings = model.encode(all_chunks)

# =========================
# STORE IN CHROMADB
# =========================

print("\nStoring in ChromaDB...")

for i, chunk in enumerate(all_chunks):

    collection.add(
        documents=[chunk],
        embeddings=[embeddings[i].tolist()],
        metadatas=[all_metadata[i]],
        ids=[str(i)]
    )

print(f"\nSUCCESS: Stored {len(all_chunks)} chunks!")