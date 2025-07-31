import os
import json
import logging
from typing import List, Dict, Any
from google import genai
from google.genai import types
from models import LegalAnswer

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Gemini AI"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.client = genai.Client(api_key=api_key)
        logger.info("Gemini client initialized")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Gemini text-embedding-004 model
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        try:
            # Use the embedding model following the blueprint pattern
            result = self.client.models.embed_content(
                model="text-embedding-004",
                contents=[text]
            )
            
            # Extract embedding values from the response
            if hasattr(result, 'embeddings') and result.embeddings:
                embedding = result.embeddings[0]
                # Handle ContentEmbedding object
                if hasattr(embedding, 'values'):
                    return list(embedding.values)
                else:
                    logger.error(f"Embedding object attributes: {dir(embedding)}")
                    raise Exception("Embedding object has no 'values' attribute")
            else:
                logger.error(f"Response attributes: {dir(result)}")
                raise Exception("No embeddings in response")
                
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a single API call for maximum speed
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Use batch embedding for much faster processing
            result = self.client.models.embed_content(
                model="text-embedding-004",
                contents=texts
            )
            
            embeddings = []
            if hasattr(result, 'embeddings') and result.embeddings:
                for embedding in result.embeddings:
                    if hasattr(embedding, 'values'):
                        embeddings.append(list(embedding.values))
                    else:
                        raise Exception("Embedding object has no 'values' attribute")
                return embeddings
            else:
                raise Exception("No embeddings in response")
                
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise Exception(f"Failed to generate batch embeddings: {str(e)}")
    
    def answer_question_with_context(self, question: str, context_chunks: List[str]) -> str:
        """
        Answer a question using provided context chunks
        
        Args:
            question: The question to answer
            context_chunks: List of relevant text chunks for context
            
        Returns:
            The answer string extracted from the AI response
        """
        try:
            # Prepare context
            chunks_text = "\n".join([f"- {chunk}" for chunk in context_chunks])
            
            system_prompt = (
                "You are a legal AI assistant. Based on the following text chunks, "
                "answer the question accurately and comprehensively. "
                "Provide your response as JSON with the following format: "
                '{"answer": "your detailed answer", "condition": "any conditions or limitations", '
                '"rationale": "reasoning behind your answer"}'
            )
            
            user_prompt = f"""Question: {question}

Context chunks:
{chunks_text}

Please analyze the provided context and answer the question. If the context doesn't contain enough information to answer the question completely, state that clearly in your response."""
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=user_prompt)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=LegalAnswer,
                    temperature=0.0,  # Zero temperature for fastest, most consistent responses
                    max_output_tokens=2048,  # Limit output for faster generation
                ),
            )
            
            if not response.text:
                raise Exception("Empty response from Gemini")
            
            # Parse the JSON response
            try:
                json_response = json.loads(response.text)
                answer = json_response.get("answer", "No answer provided")
                return answer
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw response
                logger.warning("Failed to parse JSON response, returning raw text")
                return response.text
                
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return f"Error generating answer: {str(e)}"
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate text using Gemini
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            return response.text or "No response generated"
            
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise Exception(f"Failed to generate text: {str(e)}")
