#!/usr/bin/env python

import chromadb

# New: Server mode
client = chromadb.HttpClient(host='localhost', port=8000)

# Verify connection
if type(client.heartbeat()) == int:
    # Should return a nanosecond timestamp
    print("Connected to ChromaDB server successfully.")
