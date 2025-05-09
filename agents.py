from tools import calculator_tool, dictionary_tool
from vector_store import retrieve_chunks
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

# Load the .env file containing GOOGLE_API_KEY
load_dotenv()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

def rag_llm_answer(chunks, query):
    context = "\n".join([doc.page_content for doc in chunks])
    prompt = f"Context:\n{context}\n\nAnswer this: {query}"
    return llm.invoke(prompt)

def agent_router(query, vector_store):
    lower_query = query.lower()

    if "calculate" in lower_query:
        return {"tool": "Calculator", "answer": calculator_tool(query)}
    elif "define" in lower_query:
        return {"tool": "Dictionary", "answer": dictionary_tool(query)}
    else:
        chunks = retrieve_chunks(query, vector_store)
        print(f"Retrieved {len(chunks)} chunks for query: {query}")  # 👈 Add this line
        answer = rag_llm_answer(chunks, query)
        return {
            "tool": "RAG → Gemini",
            "snippets": [doc.page_content for doc in chunks],
            "answer": answer
        }