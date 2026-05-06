import streamlit as st
from sentence_transformers import SentenceTransformer
import chromadb
from ollama import Client

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Local RAG Assistant",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Local RAG Assistant")
# =========================
# CHAT HISTORY
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# DISPLAY CHAT HISTORY
# =========================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])    

# =========================
# LOAD EMBEDDING MODEL
# =========================

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("BAAI/bge-base-en")

model = load_embedding_model()

# =========================
# LOAD CHROMADB
# =========================

@st.cache_resource
def load_chroma():

    client = chromadb.PersistentClient(path="./chroma_db")

    collection = client.get_collection(name="rag-demo")

    return collection

collection = load_chroma()

# =========================
# LOAD OLLAMA
# =========================

@st.cache_resource
def load_ollama():

    return Client(host='http://127.0.0.1:11434')

client_ollama = load_ollama()

# =========================
# USER INPUT
# =========================

query = st.chat_input("Ask your question")

# =========================
# SEARCH BUTTON
# =========================

# =========================
# PROCESS USER MESSAGE
# =========================

if query:

    # Show user message
    st.chat_message("user").markdown(query)

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    with st.spinner("Thinking..."):

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
        # CONTEXT
        # =========================

        context = "\n".join(results["documents"][0])

        # =========================
        # CONVERSATION HISTORY
        # =========================

        history = ""

        for msg in st.session_state.messages[-6:]:

            history += f"{msg['role']}: {msg['content']}\n"

        # =========================
        # PROMPT
        # =========================

        prompt = f"""
You are an AI research assistant.

Use:
1. Previous conversation
2. Retrieved context

to answer naturally and helpfully.

Conversation:
{history}

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

        answer = response["message"]["content"]

    # =========================
    # SHOW AI RESPONSE
    # =========================

    with st.chat_message("assistant"):
        st.markdown(answer)

    # Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    # =========================
    # SOURCES
    # =========================

    with st.expander("Retrieved Sources"):

        for i, doc in enumerate(results["documents"][0]):

            st.markdown(f"### Chunk {i+1}")

            st.write(doc)

            st.write(
                f"Source: {results['metadatas'][0][i]['source']}"
            )

            st.markdown("---")