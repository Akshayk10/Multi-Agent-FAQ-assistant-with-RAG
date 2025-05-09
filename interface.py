import streamlit as st
from agents import agent_router
from vector_store import load_vector_store

st.set_page_config(page_title="Multi-Agent FAQ Assistant", layout="wide")

# Load vector store
vector_store = load_vector_store()

# Check if vector store is empty
if len(vector_store.get()['ids']) == 0:
    st.error("Vector store is empty. Please run the initialization script first.")
    st.stop()

st.title("📘 Multi-Agent FAQ Assistant")
query = st.text_input("🔍 Ask a question")
if query:
    result = agent_router(query, vector_store)
    st.markdown(f"### 🔧 Tool Used: `{result['tool']}`")
    if "snippets" in result:
        st.markdown("### 📚 Retrieved Context:")
        for i, snippet in enumerate(result["snippets"]):
            st.write(f"**Snippet {i+1}:** {snippet[:400]}...")
    st.markdown("### 💬 Answer:")
    st.success(result["answer"])