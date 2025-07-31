# HackRx Document Processing API

A FastAPI backend application that processes PDF and DOCX documents, extracts text, creates embeddings using Google's Gemini AI, stores them in Pinecone vector database, and answers questions using semantic search and AI-powered text generation.

## Features

✅ **HTTPS Ready** - Automatically provided by Replit deployment  
✅ **HackRx Compliant** - `/hackrx/run` endpoint with bearer token authentication  
✅ **Document Processing** - Supports PDF and DOCX files from URLs  
✅ **AI-Powered** - Uses Google Gemini for embeddings and question answering  
✅ **Vector Search** - Pinecone for efficient semantic search  
✅ **Robust Error Handling** - Comprehensive logging and error management  

## API Endpoints

### POST /hackrx/run

Process documents and answer questions using AI.

**Required Headers**:
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer 9953d967b81381295864fb71b20cd27085ee80c24512eeabce64f3f921bb009d
```

**Request Body**:
```json
{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "What is the main topic of this document?",
    "What are the key findings?"
  ]
}
```

**Response**:
```json
{
  "answers": [
    "The main topic is...",
    "The key findings include..."
  ]
}
```

### GET /health

Health check endpoint to verify API status.

**Response**:
```json
{
  "status": "healthy",
  "service": "HackRx Document Processing API"
}
```

## Environment Variables

Required environment variables that must be set in Replit Secrets:

- `GEMINI_API_KEY` - Google Gemini AI API key
- `PINECONE_API_KEY` - Pinecone vector database API key

Optional environment variables:
- `PINECONE_INDEX` - Pinecone index name (default: "hackrx-documents")
- `PINECONE_ENV` - Pinecone environment (default: "us-east-1")

## Usage Example

```bash
curl -X POST https://your-app-url.onrender.com/hackrx/run \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer 9953d967b81381295864fb71b20cd27085ee80c24512eeabce64f3f921bb009d" \
  -d '{
    "documents": "https://www.orimi.com/pdf-test.pdf",
    "questions": [
      "What is the main topic of this document?",
      "What does this document explain?"
    ]
  }'
```

## How It Works

1. **Document Download**: Downloads PDF/DOCX from provided URL
2. **Text Extraction**: Extracts text content using PyMuPDF (PDF) or python-docx (DOCX)
3. **Text Chunking**: Splits text into overlapping 500-word chunks with 100-word overlap
4. **Embedding Generation**: Creates vector embeddings using Gemini text-embedding-004 model
5. **Vector Storage**: Stores embeddings in Pinecone with text metadata
6. **Question Processing**: 
   - Embeds each question using Gemini
   - Performs semantic search in Pinecone for relevant chunks
   - Uses Gemini generative AI to answer questions based on retrieved context

## Supported Document Types

- **PDF**: Any PDF document accessible via public URL
- **DOCX**: Microsoft Word documents accessible via public URL

## Technical Stack

- **Framework**: FastAPI
- **AI/ML**: Google Gemini (embeddings + text generation)
- **Vector Database**: Pinecone
- **Document Processing**: PyMuPDF, python-docx
- **Deployment**: Replit (automatic HTTPS)

## Deployment

The application is designed to run on Replit with automatic HTTPS and port management. Simply:

1. Set up the required environment variables in Replit Secrets
2. The application will automatically create Pinecone indexes if they don't exist
3. Access the API at your Replit app URL

## Security

- Bearer token authentication for all protected endpoints
- Input validation using Pydantic models
- Comprehensive error handling and logging
- Secure environment variable management

## Performance

- Optimized for document processing and semantic search
- Batch processing for embedding generation
- Efficient chunking strategy for large documents
- Scalable vector database backend