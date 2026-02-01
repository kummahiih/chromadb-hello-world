To do this efficiently, you should use the **filename (or file path)** as the unique ID for each record.

The most performant strategy is **"Check, Filter, then Batch Add."**

1. **Fetch all existing IDs** from the database (so you know what you already have).
2. **Scan your folder** and verify which files are missing from that list.
3. **Process only the new files** and add them in batches.

This approach saves time and money (if you are using paid APIs like OpenAI) because you don't regenerate embeddings for files that already exist.

### Python Script: The "Incremental Load" Pattern

Here is a complete script. It assumes you have a folder named `documents` containing `.txt` files.

```python
import os
import chromadb

# 1. Setup Client and Collection
# Using persistent client so data saves to disk
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="my_knowledge_base")

# 2. Get the list of files already in the DB
# We only fetch 'ids' to make this operation fast (avoids downloading heavy vectors)
existing_docs = collection.get(include=[])
existing_ids = set(existing_docs["ids"])

print(f"Database currently has {len(existing_ids)} documents.")

# 3. Prepare lists for new data
new_ids = []
new_documents = []
new_metadatas = []
DOCS_FOLDER = "./documents"

# 4. Loop through files in the folder
for root, _, files in os.walk(DOCS_FOLDER):
    for filename in files:
        if filename.endswith(".txt"):  # Adjust for .md, .pdf, etc.
            
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

```

### Why this approach is best

* **Speed:** `collection.get(include=[])` is instant even with thousands of docs because it doesn't load the vector data, just the ID index.
* **Cost Efficiency:** You strictly avoid running the embedding model (which is the slow/expensive part) on files you've already processed.
* **Consistency:** By explicitly assigning `ids=filename`, you prevent duplicate entries. If you let Chroma auto-generate IDs (UUIDs), adding "ProjectNotes.txt" twice would result in two identical entries with different random IDs.

### Advanced Tip: Content Hashing

The script above assumes that if the **filename** is the same, the content is the same.
If you have files where the name stays the same but the *content changes* (e.g., a "notes.txt" that you update daily), checking the ID is not enough.

In that case, you generate a hash (MD5) of the file content and store that in the metadata.

1. Read file.
2. Calculate Hash.
3. Check if `metadata['hash'] == new_hash` in the DB.
4. If different, use `collection.upsert()` to overwrite the old version.

Would you like to see how to implement the **Content Hash** method to handle file updates as well?