#!/usr/bin/env python

import chromadb
from typing import Annotated, TypedDict
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, END

DB_NAME="chromadb_example_collection"
MODEL_NAME="nomic-embed-text"


# --- 1. CONNECT TO LOCAL SERVICES ---
# Ollama for LLM and Embeddings
llm = ChatOllama(model="llama3", temperature=0)
embeddings = OllamaEmbeddings(model=MODEL_NAME)

# Connect to the EXISTING ChromaDB local server
vectorstore = Chroma(
    collection_name=DB_NAME,
    embedding_function=embeddings,
    host="localhost",
    port=8000  # Default Chroma port
)
retriever = vectorstore.as_retriever()

# --- 2. DEFINE THE GRAPH STATE ---
class GraphState(TypedDict):
    question: str
    context: str
    response: str

# --- 3. DEFINE THE NODES ---
def retrieve_node(state: GraphState):
    """Fetch data from the local Chroma server."""
    print(f"--- 19:02:55 | RETRIEVING FROM CHROMADB SERVER ---")
    question = state["question"]
    # Retrieve relevant snippets
    #docs = retriever.query(query_texts=[question], n_results=5)
    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])
    print(f"Retrieved {len(docs) } documents from ChromaDB.")
    print(f"Retrieved context: {context}")
    return {"context": context}

def generate_node(state: GraphState):
    """Generate answer using Ollama LLM."""
    print(f"--- 19:02:55 | GENERATING WITH OLLAMA ---")
    prompt = f"Context: {state['context']}\n\nQuestion: {state['question']}"
    response = llm.invoke(prompt)
    return {"response": response.content}

# --- 4. ASSEMBLE THE LANGGRAPH ---
builder = StateGraph(GraphState)

builder.add_node("retrieve", retrieve_node)
builder.add_node("generate", generate_node)

builder.set_entry_point("retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)

app = builder.compile()

# --- 5. EXECUTE ---
inputs = {"question": "how to set up localhost chromadb clinet in Python?"}
final_state = app.invoke(inputs)

print("\n--- FINAL RESPONSE ---")
print(final_state["response"])