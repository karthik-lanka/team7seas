import re
from typing import List
import logging

logger = logging.getLogger(__name__)

class TextChunker:
    """Handles text chunking with overlapping segments"""
    
    def __init__(self, chunk_size: int = 800, overlap_size: int = 150):
        """
        Initialize text chunker with optimized settings for speed and accuracy
        
        Args:
            chunk_size: Target number of words per chunk (increased for fewer chunks)
            overlap_size: Number of words to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of text chunks
        """
        try:
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Split into words
            words = cleaned_text.split()
            
            if len(words) <= self.chunk_size:
                # If text is smaller than chunk size, return as single chunk
                return [cleaned_text]
            
            chunks = []
            start_idx = 0
            
            while start_idx < len(words):
                # Calculate end index for current chunk
                end_idx = min(start_idx + self.chunk_size, len(words))
                
                # Extract chunk words
                chunk_words = words[start_idx:end_idx]
                chunk_text = ' '.join(chunk_words)
                
                if chunk_text.strip():
                    chunks.append(chunk_text)
                
                # If we've reached the end, break
                if end_idx >= len(words):
                    break
                
                # Move start index forward by (chunk_size - overlap_size)
                start_idx += (self.chunk_size - self.overlap_size)
            
            logger.info(f"Created {len(chunks)} chunks from {len(words)} words")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            raise Exception(f"Failed to chunk text: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\'\"\/]', ' ', text)
        
        # Remove excessive punctuation
        text = re.sub(r'\.{3,}', '...', text)
        text = re.sub(r'\-{2,}', '--', text)
        
        return text.strip()
