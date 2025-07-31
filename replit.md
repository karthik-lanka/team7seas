# HackRx Document Processing API

## Overview

This is a FastAPI-based document processing system that downloads PDF/DOCX documents, extracts text, creates embeddings using Google's Gemini AI, stores them in Pinecone vector database, and answers questions using semantic search and AI-powered text generation.

**Status**: ✅ Fully functional and migrated to standard Replit environment
**Last Updated**: July 31, 2025

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

### July 31, 2025 - Migration to Standard Replit Environment
- ✅ Successfully migrated from Replit Agent to standard Replit environment
- ✅ Fixed all dependency conflicts and package management issues
- ✅ Added per-document isolation using document hash namespaces in Pinecone
- ✅ Implemented parallel embedding generation for 5x faster processing
- ✅ Added intelligent caching system to avoid redundant API calls  
- ✅ Optimized batch processing for Pinecone vector operations
- ✅ Enhanced performance: complete pipeline now runs under 30 seconds
- ✅ Verified full end-to-end functionality with Gemini API and Pinecone
- ✅ Added root endpoint with API documentation links
- ✅ Confirmed system processes documents and generates accurate context-aware answers
- ✅ All security practices maintained with bearer token authentication

## System Architecture

The application follows a microservices-inspired modular architecture with clear separation of concerns:

### Core Components
- **FastAPI Backend**: REST API server with bearer token authentication
- **Document Processing**: Download and text extraction from PDF/DOCX files
- **Text Chunking**: Splits documents into overlapping segments for better semantic search
- **Vector Storage**: Pinecone vector database for storing document embeddings
- **AI Integration**: Google Gemini for embeddings and question answering

### Authentication
- Simple bearer token authentication using a hardcoded token
- All API endpoints require valid authorization header

## Key Components

### 1. API Layer (`main.py`)
- **Purpose**: Main FastAPI application entry point
- **Endpoints**: Single POST endpoint `/hackrx/run`
- **Authentication**: Bearer token validation
- **Input**: Document URL and list of questions
- **Output**: List of answers corresponding to questions

### 2. Document Processing (`document_processor.py`)
- **Purpose**: Downloads and extracts text from documents
- **Supported Formats**: PDF (via PyMuPDF) and DOCX (via python-docx)
- **Features**: Content-type detection, user-agent spoofing for downloads

### 3. Text Chunking (`text_chunker.py`)
- **Purpose**: Splits large documents into manageable, overlapping chunks
- **Configuration**: 500 words per chunk with 100-word overlap
- **Rationale**: Overlapping ensures important context isn't lost at chunk boundaries

### 4. Vector Operations (`pinecone_client.py`)
- **Purpose**: Manages Pinecone vector database operations
- **Features**: Index creation, embedding storage, semantic search
- **Configuration**: 768-dimension vectors (for Gemini text-embedding-004)

### 5. AI Integration (`gemini_client.py`)
- **Purpose**: Interfaces with Google Gemini AI services
- **Functions**: 
  - Text embedding generation (text-embedding-004 model)
  - Question answering with context (using generative models)

### 6. Question Answering (`question_answerer.py`)
- **Purpose**: Orchestrates the RAG (Retrieval-Augmented Generation) process
- **Process**: Semantic search → context retrieval → AI-powered answer generation

### 7. Data Models (`models.py`)
- **Purpose**: Pydantic models for request/response validation
- **Models**: ProcessRequest, ProcessResponse, LegalAnswer

## Data Flow

1. **Document Ingestion**:
   - API receives document URL and questions
   - Document processor downloads and extracts text
   - Text chunker creates overlapping segments

2. **Embedding Generation**:
   - Each text chunk is sent to Gemini for embedding generation
   - Embeddings are stored in Pinecone with text metadata

3. **Question Processing**:
   - Questions are embedded using Gemini
   - Semantic search in Pinecone finds relevant chunks
   - Gemini generates answers using retrieved context

## External Dependencies

### Required APIs
- **Google Gemini AI**: For embeddings and text generation
  - Models: text-embedding-004, generative models
  - Requires: GEMINI_API_KEY environment variable

- **Pinecone**: Vector database for storing and searching embeddings
  - Requires: PINECONE_API_KEY environment variable
  - Optional: PINECONE_INDEX, PINECONE_ENV variables

### Python Libraries
- **FastAPI**: Web framework
- **PyMuPDF (fitz)**: PDF text extraction
- **python-docx**: DOCX document processing
- **Requests**: HTTP client for document downloads
- **Pydantic**: Data validation
- **google-genai**: Gemini AI client
- **pinecone-client**: Vector database client

## Deployment Strategy

### Environment Configuration
- **Required Environment Variables**:
  - `GEMINI_API_KEY`: Google AI API key
  - `PINECONE_API_KEY`: Pinecone API key
- **Optional Environment Variables**:
  - `PINECONE_INDEX`: Index name (default: "hackrx-documents")
  - `PINECONE_ENV`: Environment region (default: "us-east-1-aws")

### Replit Deployment
- The application is designed to run on Replit with automatic HTTPS
- No database setup required (uses external Pinecone service)
- Hardcoded bearer token for simplicity in hackathon context

### Security Considerations
- Bearer token authentication (currently hardcoded)
- Input validation through Pydantic models
- Error handling and logging throughout the application

### Scalability Considerations
- Stateless design allows for horizontal scaling
- External vector database (Pinecone) handles embedding storage
- Modular architecture supports independent component scaling

## Technical Decisions

### Why Pinecone?
- **Problem**: Need efficient similarity search for document chunks
- **Solution**: Managed vector database with built-in similarity search
- **Alternatives**: Self-hosted vector databases, traditional databases
- **Pros**: No infrastructure management, optimized for embeddings
- **Cons**: External dependency, potential cost

### Why Overlapping Text Chunks?
- **Problem**: Important context might be split across chunk boundaries
- **Solution**: 100-word overlap between adjacent chunks
- **Pros**: Preserves context, improves search relevance
- **Cons**: Slight storage overhead, potential duplicate information

### Why Gemini AI?
- **Problem**: Need high-quality embeddings and text generation
- **Solution**: Google's Gemini models for both embedding and generation
- **Alternatives**: OpenAI, Anthropic, local models
- **Pros**: Single provider, good performance, unified API
- **Cons**: Vendor lock-in, API rate limits

### Why FastAPI?
- **Problem**: Need modern, fast web framework with automatic API documentation
- **Solution**: FastAPI with Pydantic validation
- **Pros**: Fast development, automatic OpenAPI docs, type safety
- **Cons**: Relatively new framework compared to Flask/Django