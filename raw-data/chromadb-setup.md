To install and run ChromaDB as a standalone server (client/server mode), the standard and most reliable method is using **Docker**. This separates the database from your application code, allowing multiple applications to connect to the same vector index.

Here are the two primary ways to set it up.

### Method 1: Docker (Recommended)

This is the preferred method for production or stable development environments.

**1. Run a single container**
If you have Docker installed, you can run Chroma immediately with this command:

```bash
docker run -p 8000:8000 chromadb/chroma

```

**2. Run with Docker Compose (For Persistence)**
To ensure your data survives after you stop the container, you should mount a volume. Create a file named `docker-compose.yml`:

```yaml
version: '3.9'

services:
  server:
    image: chromadb/chroma:latest
    volumes:
      # Mounts the local 'chroma_data' folder to the container
      - ./chroma_data:/chroma/chroma
    ports:
      - "8000:8000"

```

Then start it in the background:

```bash
docker-compose up -d

```

### Method 2: Python CLI (For Local Dev)

If you don't want to use Docker, you can run the server directly using the Python package you likely already installed.

1. **Install the server dependencies:**
```bash
pip install "chromadb[server]"

```


2. **Run the server command:**
You must specify a path where the data will be stored.
```bash
chroma run --path ./my_chroma_data

```


*The server will start on `localhost:8000` by default.*

---

### How to Connect (The Client)

Once the server is running (Method 1 or 2), you must change your Python code to connect to the server instead of creating a local database.

**Instead of:**

```python
# Old: Local mode
client = chromadb.PersistentClient(path="./db")

```

**Use this:**

```python
import chromadb

# New: Server mode
client = chromadb.HttpClient(host='localhost', port=8000)

# Verify connection
print(client.heartbeat())  # Should return a nanosecond timestamp

```

### Verification

You can verify the server is running by visiting the heartbeat endpoint in your browser:
`http://localhost:8000/api/v1/heartbeat`

Would you like to know how to set up **authentication** (like a static API token) for your new Chroma server?