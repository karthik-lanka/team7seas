from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from models import ProcessRequest, ProcessResponse
from document_processor import DocumentProcessor
from text_chunker import TextChunker
from gemini_client import GeminiClient
from pinecone_client import PineconeClient
from question_answerer import QuestionAnswerer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HackRx Document Processing API", version="1.0.0")
security = HTTPBearer()

# Expected bearer token
EXPECTED_TOKEN = "9953d967b81381295864fb71b20cd27085ee80c24512eeabce64f3f921bb009d"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify the bearer token"""
    if credentials.credentials != EXPECTED_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

@app.post("/hackrx/run", response_model=ProcessResponse)
async def process_documents(request: ProcessRequest, token: str = Depends(verify_token)):
    """
    Process documents and answer questions using Gemini AI and Pinecone
    """
    try:
        logger.info(f"Processing request with {len(request.questions)} questions")
        
        # Initialize clients
        document_processor = DocumentProcessor()
        text_chunker = TextChunker()
        gemini_client = GeminiClient()
        pinecone_client = PineconeClient()
        question_answerer = QuestionAnswerer(gemini_client, pinecone_client)
        
        # Download and process document
        logger.info(f"Downloading document from: {request.documents}")
        document_text = document_processor.process_document(str(request.documents))
        
        if not document_text or len(document_text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="No text content found in the document"
            )
        
        # Chunk the text
        logger.info("Chunking document text")
        chunks = text_chunker.chunk_text(document_text)
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Failed to create text chunks from document"
            )
        
        logger.info(f"Created {len(chunks)} text chunks")
        
        # Generate embeddings and store in Pinecone with document isolation
        logger.info("Generating embeddings and storing in Pinecone")
        pinecone_client.store_chunks(chunks, gemini_client, str(request.documents))
        
        # Answer questions
        logger.info("Processing questions")
        answers = []
        for i, question in enumerate(request.questions):
            logger.info(f"Processing question {i+1}/{len(request.questions)}: {question[:100]}...")
            try:
                answer = question_answerer.answer_question(question, str(request.documents))
                answers.append(answer)
            except Exception as e:
                logger.error(f"Error processing question {i+1}: {str(e)}")
                answers.append(f"Error processing question: {str(e)}")
        
        logger.info(f"Successfully processed all questions")
        return ProcessResponse(answers=answers)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "HackRx Document Processing API",
        "version": "1.0.0", 
        "status": "running",
        "endpoints": {
            "POST /hackrx/run": "Process documents and answer questions",
            "GET /health": "Health check",
            "GET /docs": "Interactive API documentation"
        },
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "HackRx Document Processing API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
