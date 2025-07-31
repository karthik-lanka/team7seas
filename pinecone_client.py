import os
import logging
from typing import List, Dict, Any
import hashlib
from pinecone import Pinecone, ServerlessSpec
from gemini_client import GeminiClient

logger = logging.getLogger(__name__)

class PineconeClient:
    """Client for interacting with Pinecone vector database"""
    
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
            else:
                logger.info(f"Using existing Pinecone index: {self.index_name}")
                
        except Exception as e:
            logger.error(f"Error ensuring index exists: {str(e)}")
            raise Exception(f"Failed to initialize Pinecone index: {str(e)}")
    
    def _generate_chunk_id(self, text: str) -> str:
        """Generate a unique ID for a text chunk"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def store_chunks(self, chunks: List[str], gemini_client: GeminiClient):
        """
        Store text chunks in Pinecone with their embeddings
        
        Args:
            chunks: List of text chunks to store
            gemini_client: Gemini client for generating embeddings
        """
        try:
            vectors_to_upsert = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                
                # Generate embedding for the chunk
                embedding = gemini_client.generate_embedding(chunk)
                
                # Create vector with metadata
                vector_id = self._generate_chunk_id(chunk)
                vector = {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "text": chunk,
                        "chunk_index": i
                    }
                }
                vectors_to_upsert.append(vector)
            
            # Upsert vectors in batches
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch)
                logger.info(f"Upserted batch {i//batch_size + 1}")
            
            logger.info(f"Successfully stored {len(chunks)} chunks in Pinecone")
            
        except Exception as e:
            logger.error(f"Error storing chunks in Pinecone: {str(e)}")
            raise Exception(f"Failed to store chunks: {str(e)}")
    
    def search_relevant_chunks(self, query: str, gemini_client: GeminiClient, top_k: int = 5) -> List[str]:
        """
        Search for relevant text chunks using semantic similarity
        
        Args:
            query: Query text to search for
            gemini_client: Gemini client for generating query embedding
            top_k: Number of top results to return
            
        Returns:
            List of relevant text chunks
        """
        try:
            # Generate embedding for the query
            query_embedding = gemini_client.generate_embedding(query)
            
            # Search in Pinecone
            search_results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Extract text chunks from results
            relevant_chunks = []
            for match in search_results.matches:
                if match.metadata and "text" in match.metadata:
                    relevant_chunks.append(match.metadata["text"])
            
            logger.info(f"Found {len(relevant_chunks)} relevant chunks for query")
            return relevant_chunks
            
        except Exception as e:
            logger.error(f"Error searching in Pinecone: {str(e)}")
            raise Exception(f"Failed to search for relevant chunks: {str(e)}")
    
    def clear_index(self):
        """Clear all vectors from the index"""
        try:
            self.index.delete(delete_all=True)
            logger.info("Cleared all vectors from Pinecone index")
        except Exception as e:
            logger.error(f"Error clearing index: {str(e)}")
            raise Exception(f"Failed to clear index: {str(e)}")
