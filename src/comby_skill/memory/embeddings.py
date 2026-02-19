"""
Vector Embeddings Module

Provides code embeddings for similarity search using sentence-transformers.
"""

from typing import List, Optional, Dict, Any, Tuple
import numpy as np


class CodeEmbedder:
    """Generate embeddings for code snippets."""

    def __init__(
        self,
        model_name: str = "microsoft/graphcodebert-base",
        device: Optional[str] = None,
    ):
        """Initialize embedder.

        Args:
            model_name: HuggingFace model name
            device: Device to use (cpu, cuda)
        """
        self.model_name = model_name
        self.device = device
        self.model = None

    def load_model(self):
        """Load the embedding model."""
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch

            if self.device is None:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name).to(self.device)
            self.model.eval()

        except ImportError:
            # Fallback to simple embeddings
            self.model = None

    def embed_code(
        self,
        code: str,
        max_length: int = 512,
    ) -> np.ndarray:
        """Generate embedding for code.

        Args:
            code: Code snippet
            max_length: Maximum token length

        Returns:
            Embedding vector
        """
        if self.model is None:
            return self._simple_embed(code)

        import torch

        # Tokenize
        inputs = self.tokenizer(
            code,
            return_tensors="pt",
            max_length=max_length,
            truncation=True,
        ).to(self.device)

        # Generate embedding
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use mean pooling of last hidden state
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze()

        return embedding.cpu().numpy()

    def embed_batch(
        self,
        code_snippets: List[str],
        batch_size: int = 8,
    ) -> List[np.ndarray]:
        """Generate embeddings for batch of code.

        Args:
            code_snippets: List of code snippets
            batch_size: Batch size

        Returns:
            List of embedding vectors
        """
        if self.model is None:
            return [self._simple_embed(code) for code in code_snippets]

        import torch

        embeddings = []

        for i in range(0, len(code_snippets), batch_size):
            batch = code_snippets[i:i + batch_size]

            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True,
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                batch_embeddings = outputs.last_hidden_state.mean(dim=1)

            embeddings.extend(batch_embeddings.cpu().numpy())

        return embeddings

    def _simple_embed(self, code: str) -> np.ndarray:
        """Simple fallback embedding.

        Args:
            code: Code snippet

        Returns:
            Simple embedding vector
        """
        # Simple hash-based embedding as fallback
        import hashlib

        # Tokenize by whitespace and common delimiters
        tokens = code.split() + list("{}()[];,")

        # Create bag of words
        embedding = np.zeros(256)
        for token in tokens:
            h = int(hashlib.md5(token.encode()).hexdigest()[:8], 16)
            embedding[h % 256] += 1

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding


class EmbeddingStore:
    """Store and query code embeddings."""

    def __init__(self, db_path: str = ":memory:"):
        """Initialize embedding store.

        Args:
            db_path: Path to SQLite database
        """
        import sqlite3
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                function_name TEXT,
                line_start INTEGER,
                line_end INTEGER,
                embedding BLOB,
                code_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(file_path, function_name, line_start)
            )
        """)
        self.conn.commit()

    def add_embedding(
        self,
        file_path: str,
        embedding: np.ndarray,
        code_text: str,
        function_name: Optional[str] = None,
        line_start: Optional[int] = None,
        line_end: Optional[int] = None,
    ):
        """Add embedding to store.

        Args:
            file_path: Path to file
            embedding: Embedding vector
            code_text: Code snippet
            function_name: Function name if applicable
            line_start: Start line
            line_end: End line
        """
        import pickle

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO code_embeddings
            (file_path, function_name, line_start, line_end, embedding, code_text)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            file_path,
            function_name,
            line_start,
            line_end,
            pickle.dumps(embedding),
            code_text,
        ))
        self.conn.commit()

    def find_similar(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Find similar code snippets.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results
            threshold: Similarity threshold

        Returns:
            List of similar code with scores
        """
        import pickle

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT file_path, function_name, line_start, line_end, embedding, code_text
            FROM code_embeddings
        """)

        results = []
        for row in cursor.fetchall():
            stored_embedding = pickle.loads(row[4])
            similarity = self._cosine_similarity(query_embedding, stored_embedding)

            if similarity >= threshold:
                results.append({
                    "file_path": row[0],
                    "function_name": row[1],
                    "line_start": row[2],
                    "line_end": row[3],
                    "similarity": float(similarity),
                    "code_text": row[5],
                })

        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Cosine similarity
        """
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def close(self):
        """Close database connection."""
        self.conn.close()


def embed_functions(
    file_path: str,
    code_content: str,
    embedder: Optional[CodeEmbedder] = None,
) -> List[Dict[str, Any]]:
    """Embed all functions in a file.

    Args:
        file_path: Path to file
        code_content: Source code
        embedder: Embedder instance

    Returns:
        List of function embeddings
    """
    import re

    if embedder is None:
        embedder = CodeEmbedder()
        embedder.load_model()

    # Extract function blocks
    functions = []

    # Python pattern
    py_pattern = r'def\s+(\w+)\s*\(([^)]*)\):(.*?)(?=\ndef\s|\Z)'
    for match in re.finditer(py_pattern, code_content, re.DOTALL):
        func_name = match.group(1)
        func_code = match.group(0)
        line_start = code_content[:match.start()].count('\n') + 1
        line_end = code_content[:match.end()].count('\n')

        embedding = embedder.embed_code(func_code)

        functions.append({
            "file_path": file_path,
            "function_name": func_name,
            "line_start": line_start,
            "line_end": line_end,
            "embedding": embedding,
            "code": func_code,
        })

    return functions
