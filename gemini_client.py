# import os
# import json
# import logging
# from typing import List, Dict, Any
# from google import genai
# from google.genai import types
# from models import LegalAnswer

# logger = logging.getLogger(__name__)

# class GeminiClient:
#     """Client for interacting with Gemini AI"""
    
#     def __init__(self):
#         api_key = os.getenv("GEMINI_API_KEY")
#         if not api_key:
#             raise ValueError("GEMINI_API_KEY environment variable is required")
        
#         self.client = genai.Client(api_key=api_key)
#         logger.info("Gemini client initialized")
    
#     def generate_embedding(self, text: str) -> List[float]:
#         """
#         Generate embedding for text using Gemini text-embedding-004 model
        
#         Args:
#             text: Input text to embed
            
#         Returns:
#             Embedding vector as list of floats
#         """
#         try:
#             # Use the embedding model following the blueprint pattern
#             result = self.client.models.embed_content(
#                 model="text-embedding-004",
#                 contents=[text]
#             )
            
#             # Extract embedding values from the response
#             if hasattr(result, 'embeddings') and result.embeddings:
#                 embedding = result.embeddings[0]
#                 # Handle ContentEmbedding object
#                 if hasattr(embedding, 'values'):
#                     return list(embedding.values)
#                 else:
#                     logger.error(f"Embedding object attributes: {dir(embedding)}")
#                     raise Exception("Embedding object has no 'values' attribute")
#             else:
#                 logger.error(f"Response attributes: {dir(result)}")
#                 raise Exception("No embeddings in response")
                
#         except Exception as e:
#             logger.error(f"Error generating embedding: {str(e)}")
#             raise Exception(f"Failed to generate embedding: {str(e)}")
    
#     def answer_question_with_context(self, question: str, context_chunks: List[str]) -> str:
#         """
#         Answer a question using provided context chunks
        
#         Args:
#             question: The question to answer
#             context_chunks: List of relevant text chunks for context
            
#         Returns:
#             The answer string extracted from the AI response
#         """
#         try:
#             # Prepare context
#             chunks_text = "\n".join([f"- {chunk}" for chunk in context_chunks])
            
#             system_prompt = (
#                 "You are a legal AI assistant. Based on the following text chunks, "
#                 "answer the question accurately and comprehensively. "
#                 "Provide your response as JSON with the following format: "
#                 '{"answer": "your detailed answer", "condition": "any conditions or limitations", '
#                 '"rationale": "reasoning behind your answer"}'
#             )
            
#             user_prompt = f"""Question: {question}

# Context chunks:
# {chunks_text}

# Please analyze the provided context and answer the question. If the context doesn't contain enough information to answer the question completely, state that clearly in your response."""
            
#             response = self.client.models.generate_content(
#                 model="gemini-2.5-pro",
#                 contents=[
#                     types.Content(role="user", parts=[types.Part(text=user_prompt)])
#                 ],
#                 config=types.GenerateContentConfig(
#                     system_instruction=system_prompt,
#                     response_mime_type="application/json",
#                     response_schema=LegalAnswer,
#                     temperature=0.1,  # Low temperature for more consistent responses
#                 ),
#             )
            
#             if not response.text:
#                 raise Exception("Empty response from Gemini")
            
#             # Parse the JSON response
#             try:
#                 json_response = json.loads(response.text)
#                 answer = json_response.get("answer", "No answer provided")
#                 return answer
#             except json.JSONDecodeError:
#                 # If JSON parsing fails, return the raw response
#                 logger.warning("Failed to parse JSON response, returning raw text")
#                 return response.text
                
#         except Exception as e:
#             logger.error(f"Error answering question: {str(e)}")
#             return f"Error generating answer: {str(e)}"
    
#     def generate_text(self, prompt: str) -> str:
#         """
#         Generate text using Gemini
        
#         Args:
#             prompt: Input prompt
            
#         Returns:
#             Generated text
#         """
#         try:
#             response = self.client.models.generate_content(
#                 model="gemini-2.5-flash",
#                 contents=prompt
#             )
            
#             return response.text or "No response generated"
            
#         except Exception as e:
#             logger.error(f"Error generating text: {str(e)}")
#             raise Exception(f"Failed to generate text: {str(e)}")

def answer_question_with_context(self, question: str, context_chunks: List[str], retries: int = 2) -> str:
    """
    Answer a question using Gemini with provided context chunks and retries on failure.

    Args:
        question: The question to answer.
        context_chunks: List of relevant text chunks.
        retries: How many times to retry in case of internal error (default is 2).

    Returns:
        The answer string.
    """
    import time

    # Limit context size to reduce latency and avoid Gemini overload
    trimmed_chunks = context_chunks[:5]
    chunks_text = "\n".join([f"- {chunk}" for chunk in trimmed_chunks])

    system_prompt = (
        "You are a legal AI assistant. Based on the following text chunks, "
        "answer the question accurately. Return only a JSON: "
        '{"answer": "...", "condition": "...", "rationale": "..."}'
    )

    user_prompt = f"""Question: {question}

Context chunks:
{chunks_text}

Answer with evidence. If insufficient data, say so."""

    for attempt in range(retries + 1):
        try:
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",  # Faster, more stable
                contents=[
                    types.Content(role="user", parts=[types.Part(text=user_prompt)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=LegalAnswer,
                    temperature=0.2,
                ),
            )

            if not response.text:
                raise Exception("Empty response from Gemini")

            # Try to parse the JSON and extract answer
            try:
                parsed = json.loads(response.text)
                return parsed.get("answer", "No answer in response")
            except json.JSONDecodeError:
                logger.warning("Non-JSON response returned")
                return response.text

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < retries:
                time.sleep(1)
                continue
            return f"Error generating answer: {str(e)}"
