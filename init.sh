#!/bin/bash
python3 -m venv env
. env/bin/activate
pip install chromadb
pip install -U langgraph langchain-ollama langchain-chroma
