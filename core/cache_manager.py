import sqlite3
import hashlib
import os

class CacheManager:
    def __init__(self, db_path="core/cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Creates the SQLite database for caching queries."""
        # Ensure the directory exists just in case
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # query_hash is the Primary Key so we don't save duplicates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_cache (
                query_hash TEXT PRIMARY KEY,
                response TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _generate_hash(self, query: str) -> str:
        """Normalizes and hashes the query to create a unique, consistent key."""
        # Normalize: lowercase and strip extra, weird whitespace
        normalized_query = " ".join(query.lower().split())
        # Create a SHA-256 hash
        return hashlib.sha256(normalized_query.encode('utf-8')).hexdigest()

    def get(self, query: str):
        """Retrieves a cached response if the exact query has been asked before."""
        query_hash = self._generate_hash(query)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT response FROM query_cache WHERE query_hash = ?", (query_hash,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0] # Return the cached text
        return None

    def set(self, query: str, response: str):
        """Saves a new query and its generated response to the cache."""
        query_hash = self._generate_hash(query)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # INSERT OR REPLACE so if there's a collision, we just update the cache
        cursor.execute('''
            INSERT OR REPLACE INTO query_cache (query_hash, response)
            VALUES (?, ?)
        ''', (query_hash, response))
        
        conn.commit()
        conn.close()