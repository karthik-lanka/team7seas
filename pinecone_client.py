import os
import logging
from typing import List, Dict, Any
import hashlib
from pinecone import Pinecone, ServerlessSpec
from gemini_client import GeminiClient
import time
import concurrent.futures
import threading

logger = logging.getLogger(__name__)

class PineconeClient:
    """Client for interacting with Pinecone vector database with per-document isolation"""
    
    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable is required")
        
        self.index_name = os.getenv("PINECONE_INDEX", "hackrx-documents")
        self.environment = os.getenv("PINECONE_ENV", "us-east-1")
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=api_key)
        
        # Create or connect to index
        self._ensure_index_exists()
        self.index = self.pc.Index(self.index_name)
        
        # Cache for embeddings to avoid redundant API calls
        self._embedding_cache = {}
        self._cache_lock = threading.Lock()
        
        logger.info(f"Pinecone client initialized with index: {self.index_name}")
    
    def _ensure_index_exists(self):
        """Ensure the Pinecone index exists, create if it doesn't"""
        try:
            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                
                # Create index with appropriate dimensions for Gemini embeddings
                self.pc.create_index(
                    name=self.index_name,
                    dimension=768,  # Dimension for text-embedding-004
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                
                # Wait for index to be ready
                while not self.pc.describe_index(self.index_name).status['ready']:
                    logger.info("Waiting for index to be ready...")
                    time.sleep(1)
            else:
                logger.info(f"Using existing Pinecone index: {self.index_name}")
                
        except Exception as e:
            logger.error(f"Error ensuring index exists: {str(e)}")
            raise Exception(f"Failed to initialize Pinecone index: {str(e)}")
    
    def _generate_document_hash(self, document_url: str) -> str:
        """Generate a unique hash for a document URL to use as namespace"""
        return hashlib.md5(document_url.encode()).hexdigest()[:16]
    
    def _generate_chunk_id(self, text: str, document_hash: str, chunk_index: int) -> str:
        """Generate a unique ID for a text chunk within a document namespace"""
        chunk_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        return f"{document_hash}_{chunk_index:04d}_{chunk_hash}"
    
    def _generate_embeddings_batch(self, chunks: List[str], gemini_client: GeminiClient) -> List[List[float]]:
        """Generate embeddings for multiple chunks using ultra-fast batch processing"""
        # Check cache for all chunks first
        cached_embeddings = []
        uncached_chunks = []
        uncached_indices = []
        
        for i, chunk in enumerate(chunks):
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
            with self._cache_lock:
                if chunk_hash in self._embedding_cache:
                    cached_embeddings.append((i, self._embedding_cache[chunk_hash]))
                else:
                    uncached_chunks.append(chunk)
                    uncached_indices.append(i)
        
        # Generate embeddings for uncached chunks in single batch call
        new_embeddings = []
        if uncached_chunks:
            # Use Gemini's batch embedding API for maximum speed
            new_embeddings = gemini_client.generate_embeddings_batch(uncached_chunks)
            
            # Cache the new embeddings
            with self._cache_lock:
                for chunk, embedding in zip(uncached_chunks, new_embeddings):
                    chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
                    self._embedding_cache[chunk_hash] = embedding
        
        # Combine cached and new embeddings in correct order
        final_embeddings: List[List[float]] = [[] for _ in range(len(chunks))]
        
        # Fill in cached embeddings
        for idx, embedding in cached_embeddings:
            final_embeddings[idx] = embedding
        
        # Fill in new embeddings
        for uncached_idx, embedding in zip(uncached_indices, new_embeddings):
            final_embeddings[uncached_idx] = embedding
        
        return final_embeddings
    
    def store_chunks(self, chunks: List[str], gemini_client: GeminiClient, document_url: str):
        """
        Store text chunks in Pinecone with their embeddings in isolated namespace
        
        Args:
            chunks: List of text chunks to store
            gemini_client: Gemini client for generating embeddings
            document_url: Source document URL for namespace isolation
        """
        try:
            document_hash = self._generate_document_hash(document_url)
            logger.info(f"Storing {len(chunks)} chunks for document namespace: {document_hash}")
            
            # Clear previous chunks for this document
            self.clear_document_chunks(document_url)
            
            # Generate embeddings efficiently
            start_time = time.time()
            embeddings = self._generate_embeddings_batch(chunks, gemini_client)
            embedding_time = time.time() - start_time
            logger.info(f"Generated {len(embeddings)} embeddings in {embedding_time:.2f} seconds")
            
            # Prepare vectors for upsert
            vectors_to_upsert = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                vector_id = self._generate_chunk_id(chunk, document_hash, i)
                vector = {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "text": chunk,
                        "chunk_index": i,
                        "document_hash": document_hash,
                        "document_url": document_url,
                        "timestamp": int(time.time())
                    }
                }
                vectors_to_upsert.append(vector)
            
            # Upsert vectors in optimized batches
            batch_size = 100
            start_time = time.time()
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch)
                logger.info(f"Upserted batch {i//batch_size + 1}/{(len(vectors_to_upsert) + batch_size - 1)//batch_size}")
            
            upsert_time = time.time() - start_time
            logger.info(f"Successfully stored {len(chunks)} chunks in {upsert_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error storing chunks in Pinecone: {str(e)}")
            raise Exception(f"Failed to store chunks: {str(e)}")
    
    def search_relevant_chunks(self, query: str, gemini_client: GeminiClient, document_url: str, top_k: int = 10) -> List[str]:
        """
        Search for relevant text chunks using semantic similarity within document namespace
        
        Args:
            query: Query text to search for
            gemini_client: Gemini client for generating query embedding
            document_url: Source document URL for namespace isolation
            top_k: Number of top results to return
            
        Returns:
            List of relevant text chunks
        """
        try:
            document_hash = self._generate_document_hash(document_url)
            
            # Generate embedding for the query (with caching)
            query_hash = hashlib.md5(query.encode()).hexdigest()
            with self._cache_lock:
                if query_hash in self._embedding_cache:
                    query_embedding = self._embedding_cache[query_hash]
                else:
                    query_embedding = gemini_client.generate_embedding(query)
                    self._embedding_cache[query_hash] = query_embedding
            
            # Search in Pinecone with document namespace filter
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter={"document_hash": document_hash}  # Fixed filter syntax
            )
            
            # Extract text chunks from results with minimum similarity threshold
            relevant_chunks = []
            similarity_threshold = 0.3  # Lower threshold for better recall
            
            logger.info(f"Pinecone search returned {len(search_results.matches)} matches")
            for i, match in enumerate(search_results.matches):
                logger.info(f"Match {i+1}: score={match.score:.3f}, id={match.id}")
                # Accept all matches for now to debug the issue
                if match.metadata and "text" in match.metadata:
                    relevant_chunks.append(match.metadata["text"])
                    logger.info(f"Added chunk with score {match.score:.3f}: {match.metadata['text'][:100]}...")
            
            logger.info(f"Found {len(relevant_chunks)} relevant chunks (score >= {similarity_threshold}) for query in document {document_hash}")
            return relevant_chunks
            
        except Exception as e:
            logger.error(f"Error searching in Pinecone: {str(e)}")
            raise Exception(f"Failed to search for relevant chunks: {str(e)}")
    
    def clear_document_chunks(self, document_url: str):
        """Clear chunks for a specific document"""
        try:
            document_hash = self._generate_document_hash(document_url)
            
            # Query to get all vector IDs for this document
            query_result = self.index.query(
                vector=[0.0] * 768,  # Dummy vector
                top_k=10000,  # Large number to get all
                include_metadata=True,
                filter={"document_hash": document_hash}
            )
            
            if query_result.matches:
                vector_ids = [match.id for match in query_result.matches]
                self.index.delete(ids=vector_ids)
                logger.info(f"Cleared {len(vector_ids)} vectors for document {document_hash}")
            
        except Exception as e:
            logger.error(f"Error clearing document chunks: {str(e)}")
            # Don't raise exception as this is non-critical
    
    def clear_index(self):
        """Clear all vectors from the index"""
        try:
            self.index.delete(delete_all=True)
            logger.info("Cleared all vectors from Pinecone index")
            # Clear cache as well
            with self._cache_lock:
                self._embedding_cache.clear()
        except Exception as e:
            logger.error(f"Error clearing index: {str(e)}")
            raise Exception(f"Failed to clear index: {str(e)}")
