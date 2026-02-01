#!/usr/bin/env python

import os
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

DB_NAME="chromadb_example_collection"
DOCS_FOLDER = "./raw-data"
MODEL_NAME="nomic-embed-text"

# 1. Setup Client and Collection
# Using persistent client so data saves to disk
client = chromadb.HttpClient(host='localhost', port=8000)
collection = client.get_or_create_collection(
    name=DB_NAME,
    embedding_function = OllamaEmbeddingFunction(
        url="http://localhost:11434/api/embeddings",  # Default Ollama URL
        model_name=MODEL_NAME
    )
)

# 2. Get the list of files already in the DB
# We only fetch 'ids' to make this operation fast (avoids downloading heavy vectors)
existing_docs = collection.get(include=[])
existing_ids = set(existing_docs["ids"])

print(f"Database currently has {len(existing_ids)} documents.")

# 3. Prepare lists for new data
new_ids = []
new_documents = []
new_metadatas = []


# 4. Loop through files in the folder
for root, _, files in os.walk(DOCS_FOLDER):
    for filename in files:
        if filename.endswith(".md"):  # Adjust for .md, .pdf, etc.
            
            # Use the filename as the unique ID
            # (You could also use the full path if you have nested folders)
            file_id = filename 
            
            # THE CHECK: Skip if we already have this ID
            if file_id in existing_ids:
                print(f"Skipping {filename} (already exists)")
                continue
            
            # If not in DB, read the file
            file_path = os.path.join(root, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text_content = f.read()
                    
                # Add to our batch lists
                new_ids.append(file_id)
                new_documents.append(text_content)
                new_metadatas.append({"source": filename})
                print(f"Queued {filename} for adding...")
                
            except Exception as e:
                print(f"Error reading {filename}: {e}")

# 5. Add to Chroma (only if we found new files)
if new_ids:
    print(f"\nAdding {len(new_ids)} new documents to the database...")
    collection.add(
        ids=new_ids,
        documents=new_documents,
        metadatas=new_metadatas
    )
    print("Success! Database updated.")
else:
    print("\nNo new documents found. Database is up to date.")