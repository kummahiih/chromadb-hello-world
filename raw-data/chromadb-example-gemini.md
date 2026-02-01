Since you have the ChromaDB server running as a standalone service on your machine, we will switch from the `persist_directory` configuration to the `HttpClient` configuration.

Here is the updated LangGraph implementation. This setup assumes your Chroma server is up (usually on port **8000**) and **Ollama** is ready to go.

### 1. Updated Implementation

```python
import chromadb
from typing import Annotated, TypedDict
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import StateGraph, END

# --- 1. CONNECT TO LOCAL SERVICES ---
# Ollama for LLM and Embeddings
llm = ChatOllama(model="llama3", temperature=0)
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Connect to the EXISTING ChromaDB local server
vectorstore = Chroma(
    collection_name="local_docs",
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
    docs = retriever.invoke(question)
    context = "\n\n".join([doc.page_content for doc in docs])
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
inputs = {"question": "What does my local documentation say about setup?"}
final_state = app.invoke(inputs)

print("\n--- FINAL RESPONSE ---")
print(final_state["response"])

```

---

### 2. Key Changes for Client Mode

* **Host/Port Configuration:** Instead of a file path, we use `host="localhost"` and `port=8000`. This allows the `langchain-chroma` wrapper to communicate with your running database container or process via HTTP.
* **Collection Name:** Ensure the `collection_name` matches exactly what you used when you originally populated the database. If it doesn't match, Chroma will return an empty list of documents.

### 3. Troubleshooting Connectivity

If the code fails to connect, verify two things:

1. **Chroma Status:** Run `curl http://localhost:8000/api/v1/heartbeat` in your terminal. If you don't get a response, the server isn't reachable.
2. **Ollama Status:** Ensure the Ollama app is running in your system tray or as a service, otherwise the `embeddings` step will time out.

**Would you like me to show you how to create a "Conditional Edge" so the graph only retrieves data if the LLM thinks it's necessary?**