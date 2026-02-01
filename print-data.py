#!/usr/bin/env python

import chromadb
DB_NAME="chromadb_example_collection"
DOCS_FOLDER = "./raw-data"

# 1. Setup Client and Collection
# Using persistent client so data saves to disk
client = chromadb.HttpClient(host='localhost', port=8000)
collection = client.get_or_create_collection(name=DB_NAME)

print(collection.get()) # Gets all the data