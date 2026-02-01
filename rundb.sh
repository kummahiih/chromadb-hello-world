#!/bin/bash
. env/bin/activate
chroma run --host localhost --port 8000 --path ./chromadb-persistence
