"""Pinecone vector database client for storing and retrieving code embeddings."""

import os
import hashlib
from typing import Optional
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from langchain_core.embeddings import Embeddings

from utils.helpers import setup_logging, chunk_code

load_dotenv()
logger = setup_logging()


class SimpleEmbeddings(Embeddings):
    """Simple embeddings using Groq for text embedding simulation.
    
    Note: In production, use a dedicated embedding model like OpenAI's
    text-embedding-ada-002 or sentence-transformers.
    """
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of documents."""
        return [self._simple_embed(text) for text in texts]
    
    def embed_query(self, text: str) -> list[float]:
        """Embed a query string."""
        return self._simple_embed(text)
    
    def _simple_embed(self, text: str) -> list[float]:
        """Create a simple deterministic embedding from text hash.
        
        This is a placeholder - replace with actual embedding model in production.
        """
        # Create deterministic embedding from text hash
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        embedding = []
        for i in range(0, min(len(text_hash), self.dimension * 2), 2):
            if len(embedding) >= self.dimension:
                break
            hex_pair = text_hash[i:i+2]
            value = (int(hex_pair, 16) - 128) / 128.0
            embedding.append(value)
        
        # Pad if necessary
        while len(embedding) < self.dimension:
            embedding.append(0.0)
        
        return embedding[:self.dimension]


class PineconeClient:
    """Client for Pinecone vector database operations."""
    
    def __init__(
        self,
        index_name: Optional[str] = None,
        api_key: Optional[str] = None,
        dimension: int = 384
    ):
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "doc-generator")
        self.dimension = dimension
        
        if not self.api_key:
            logger.warning("PINECONE_API_KEY not found - vector storage disabled")
            self.enabled = False
            self.pc = None
            self.index = None
            self.vector_store = None
            return
        
        self.enabled = True
        self.pc = Pinecone(api_key=self.api_key)
        self.embeddings = SimpleEmbeddings(dimension=dimension)
        
        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)
        self.vector_store = None
        
        logger.info(f"Pinecone client initialized with index: {self.index_name}")
    
    def _ensure_index_exists(self):
        """Create index if it doesn't exist."""
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            logger.info(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
    
    def store_code_chunks(self, code: str, metadata: dict) -> list[str]:
        """Store code chunks with embeddings."""
        if not self.enabled:
            logger.warning("Pinecone disabled - skipping storage")
            return []
        
        chunks = chunk_code(code)
        ids = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = hashlib.md5(f"{metadata.get('name', 'unknown')}_{i}_{chunk[:50]}".encode()).hexdigest()
            embedding = self.embeddings.embed_query(chunk)
            
            chunk_metadata = {
                **metadata,
                "chunk_index": i,
                "content": chunk[:1000]  # Store truncated content for retrieval
            }
            
            self.index.upsert(vectors=[(chunk_id, embedding, chunk_metadata)])
            ids.append(chunk_id)
        
        logger.info(f"Stored {len(ids)} chunks in Pinecone")
        return ids
    
    def store_parsed_structure(self, structure: dict, code_type: str) -> str:
        """Store parsed code structure for later retrieval."""
        if not self.enabled:
            return ""
        
        import json
        structure_text = json.dumps(structure, indent=2)
        structure_id = hashlib.md5(structure_text.encode()).hexdigest()
        
        embedding = self.embeddings.embed_query(structure_text)
        metadata = {
            "type": "parsed_structure",
            "code_type": code_type,
            "content": structure_text[:1000]
        }
        
        self.index.upsert(vectors=[(structure_id, embedding, metadata)])
        logger.info(f"Stored parsed structure with id: {structure_id}")
        return structure_id
    
    def retrieve_similar(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve similar code chunks or structures."""
        if not self.enabled:
            return []
        
        query_embedding = self.embeddings.embed_query(query)
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        return [
            {
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            }
            for match in results.matches
        ]
    
    def store_documentation(self, doc_id: str, documentation: str, metadata: dict) -> str:
        """Store generated documentation."""
        if not self.enabled:
            return ""
        
        embedding = self.embeddings.embed_query(documentation)
        doc_metadata = {
            **metadata,
            "type": "documentation",
            "content": documentation[:1000]
        }
        
        self.index.upsert(vectors=[(doc_id, embedding, doc_metadata)])
        logger.info(f"Stored documentation with id: {doc_id}")
        return doc_id
