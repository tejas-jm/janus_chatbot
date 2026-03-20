import os
import json
import sqlite3
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

class RAGEngine:
    def __init__(self, db_path="core/rag.db", data_dir="data"):
        self.db_path = db_path
        self.data_dir = data_dir
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.ollama_url = "http://localhost:11434/api/generate"
        self.llm_model = "llama3" # Or "phi3" if you prefer
        
        self._init_db()
        self._ingest_documents()

    def _init_db(self):
        """Creates the SQLite database to store document chunks and embeddings."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                content TEXT,
                embedding TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _get_embedding(self, text):
        """Generates a vector embedding for a given text string."""
        return self.encoder.encode(text).tolist()

    def _cosine_similarity(self, vec1, vec2):
        """Calculates the similarity between two vectors."""
        v1, v2 = np.array(vec1), np.array(vec2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def _ingest_documents(self):
        """Reads files from the data directory, chunks them, and stores them if the DB is empty."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if we already have data
        cursor.execute("SELECT COUNT(*) FROM chunks")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return # Skip ingestion if already populated
            
        print("Ingesting documents into SQLite...")
        for filename in os.listdir(self.data_dir):
            filepath = os.path.join(self.data_dir, filename)
            
            if filename.endswith(".txt") or filename.endswith(".md"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
                    
                    # Simple chunking strategy: Split by double newlines (paragraphs/sections)
                    chunks = [chunk.strip() for chunk in text.split('\n\n') if len(chunk.strip()) > 50]
                    
                    for chunk in chunks:
                        embedding = self._get_embedding(chunk)
                        cursor.execute(
                            "INSERT INTO chunks (filename, content, embedding) VALUES (?, ?, ?)",
                            (filename, chunk, json.dumps(embedding))
                        )
        conn.commit()
        conn.close()
        print("Ingestion complete.")

    def retrieve(self, query, top_k=3):
        """Finds the most relevant document chunks for a user's query."""
        query_embedding = self._get_embedding(query)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT filename, content, embedding FROM chunks")
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for filename, content, emb_json in rows:
            chunk_embedding = json.loads(emb_json)
            similarity = self._cosine_similarity(query_embedding, chunk_embedding)
            results.append((similarity, filename, content))
            
        # Sort by highest similarity and grab the top K
        results.sort(key=lambda x: x[0], reverse=True)
        top_results = results[:top_k]
        
        # Extract unique sources and the text content
        context_chunks = [res[2] for res in top_results]
        sources = list(set([res[1] for res in top_results]))
        
        return context_chunks, sources

    def generate_answer(self, query, context_chunks, history):
        """Calls the local Ollama LLM with the context and history."""
        context_str = "\n---\n".join(context_chunks)
        
        prompt = f"""You are a helpful company assistant. Use the following Context to answer the User's query. 
                     If the answer is not in the context, say "I cannot find the answer in the provided documents."

                     Recent Conversation History:
                     {history}

                     Knowledge Base Context:
                     {context_str}

                     User Query: {query}
                     Answer:"""

        payload = {
            "model": self.llm_model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.RequestException as e:
            return f"Error connecting to local LLM: {e}. Please ensure Ollama is running."

    def summarize_text(self, text_to_summarize):
        """Used for the optional /summarize command."""
        prompt = f"Summarise the following conversation history in one concise paragraph:\n\n{text_to_summarize}"
        
        payload = {
            "model": self.llm_model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.RequestException as e:
            return "Error connecting to local LLM for summary."