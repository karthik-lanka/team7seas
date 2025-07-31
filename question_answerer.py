import logging
from typing import List
from gemini_client import GeminiClient
from pinecone_client import PineconeClient

logger = logging.getLogger(__name__)

class QuestionAnswerer:
    """Handles question answering using Gemini AI and Pinecone search"""
    
    def __init__(self, gemini_client: GeminiClient, pinecone_client: PineconeClient):
        self.gemini_client = gemini_client
        self.pinecone_client = pinecone_client
        logger.info("Question answerer initialized")
    
    def answer_question(self, question: str) -> str:
        """
        Answer a question using semantic search and AI generation
        
        Args:
            question: The question to answer
            
        Returns:
            The answer as a string
        """
        try:
            # Search for relevant chunks
            logger.info(f"Searching for relevant chunks for question: {question[:100]}...")
            relevant_chunks = self.pinecone_client.search_relevant_chunks(
                query=question,
                gemini_client=self.gemini_client,
                top_k=5
            )
            
            if not relevant_chunks:
                return "No relevant information found in the document to answer this question."
            
            # Generate answer using relevant chunks as context
            logger.info(f"Generating answer using {len(relevant_chunks)} relevant chunks")
            answer = self.gemini_client.answer_question_with_context(
                question=question,
                context_chunks=relevant_chunks
            )
            
            return answer
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return f"Error processing question: {str(e)}"
