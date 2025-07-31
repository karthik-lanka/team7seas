# ✅ Deployment Checklist for HackRx API

## Pre-Deployment Verification

### 🔧 Environment Setup
- [ ] Python 3.11+ installed
- [ ] All dependencies installed from `render-requirements.txt`
- [ ] Environment variables set:
  - [ ] `GEMINI_API_KEY` (required)
  - [ ] `PINECONE_API_KEY` (required)
  - [ ] `PINECONE_INDEX` (optional, defaults to "hackrx-documents")
  - [ ] `PINECONE_ENV` (optional, defaults to "us-east-1-aws")

### 📁 Required Files Present
- [ ] `main.py` - FastAPI application
- [ ] `models.py` - Pydantic models
- [ ] `gemini_client.py` - Gemini AI integration
- [ ] `pinecone_client.py` - Pinecone vector database
- [ ] `document_processor.py` - PDF/DOCX processing
- [ ] `text_chunker.py` - Text chunking logic
- [ ] `question_answerer.py` - Q&A orchestration
- [ ] `render.yaml` - Render deployment blueprint
- [ ] `render-requirements.txt` - Production dependencies
- [ ] `Dockerfile` - Container deployment (optional)

### 🧪 Local Testing
Run automated pre-deployment check:
```bash
python deployment_checker.py pre
```

Expected output: `🎉 ALL PRE-DEPLOYMENT CHECKS PASSED!`

### 🏥 API Health Verification
```bash
# Start local server
uvicorn main:app --host=0.0.0.0 --port=5000

# Test health endpoint
curl http://localhost:5000/health

# Test API functionality  
python deployment_checker.py post
```

Expected: All checks pass with "EXCELLENT" performance rating

## Render.com Deployment Steps

### 🔗 Repository Setup
- [ ] Code pushed to GitHub repository
- [ ] Repository is public or accessible to Render
- [ ] All required files are committed and pushed

### 🌐 Render Service Creation
1. [ ] Sign in to [render.com](https://render.com)
2. [ ] Click **"New"** → **"Blueprint"**
3. [ ] Connect GitHub account if needed
4. [ ] Select repository containing HackRx API
5. [ ] Render detects `render.yaml` automatically

### 🔑 Environment Variables Configuration
In Render dashboard, set:
- [ ] `GEMINI_API_KEY` = your actual Gemini API key
- [ ] `PINECONE_API_KEY` = your actual Pinecone API key

**Critical**: Never commit API keys to repository!

### 🚀 Deployment Execution
- [ ] Click **"Apply"** to start deployment
- [ ] Monitor build logs for any errors
- [ ] Wait for "Live" status (typically 5-10 minutes)
- [ ] Note the assigned `.onrender.com` URL

## Post-Deployment Verification

### 🎯 Automated Testing
```bash
# Test deployed API (replace with your URL)
python deployment_checker.py post https://your-app.onrender.com
```

Expected output: `🎉 DEPLOYMENT VERIFICATION SUCCESSFUL!`

### 🔍 Manual Verification Steps

#### 1. Health Check
```bash
curl https://your-app.onrender.com/health
```
Expected: `{"status":"healthy","service":"HackRx Document Processing API"}`

#### 2. Root Endpoint
```bash
curl https://your-app.onrender.com/
```
Expected: Service information with endpoints list

#### 3. API Documentation
Visit: `https://your-app.onrender.com/docs`
Expected: Interactive Swagger UI documentation

#### 4. Full API Test
```bash
curl -X POST https://your-app.onrender.com/hackrx/run \
  -H "Authorization: Bearer 9953d967b81381295864fb71b20cd27085ee80c24512eeabce64f3f921bb009d" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment?",
        "What is the waiting period for pre-existing diseases?"
    ]
  }'
```

Expected: JSON response with accurate answers in under 30 seconds

## Performance Benchmarks

### ⚡ Speed Targets
- [ ] Document processing: < 5 seconds for 43 chunks
- [ ] Single question: < 10 seconds
- [ ] Multiple questions (5): < 30 seconds
- [ ] Overall API response: < 45 seconds

### 🎯 Accuracy Verification
Test questions should return accurate, detailed answers:
- [ ] Grace period: "30 days"
- [ ] PED waiting period: "36 months"
- [ ] Maternity coverage: Comprehensive details
- [ ] No hallucinated information

## Troubleshooting Guide

### 🛠️ Common Issues & Solutions

#### Build Failures
- [ ] Check `render-requirements.txt` syntax
- [ ] Verify package versions are available on PyPI
- [ ] Review build logs in Render dashboard

#### Health Check Failures
- [ ] Verify `uvicorn main:app` starts correctly
- [ ] Check port binding uses `$PORT` environment variable
- [ ] Review application startup logs

#### API Errors
- [ ] Confirm environment variables are set correctly
- [ ] Verify Gemini API key has proper permissions
- [ ] Test Pinecone API key and index access
- [ ] Check request format matches API specification

#### Performance Issues
- [ ] Monitor API rate limits for Gemini/Pinecone
- [ ] Check for memory/CPU constraints in logs
- [ ] Verify batch processing is working correctly

### 📋 Deployment Status Matrix

| Component | Local | Render | Status |
|-----------|-------|--------|--------|
| Health Check | ⭕ | ⭕ | Pending |
| Root Endpoint | ⭕ | ⭕ | Pending |
| Document Processing | ⭕ | ⭕ | Pending |
| Question Answering | ⭕ | ⭕ | Pending |
| Performance < 30s | ⭕ | ⭕ | Pending |

Fill in: ✅ Pass, ❌ Fail, ⭕ Not Tested

## 🎉 Success Criteria

Deployment is successful when:
- [ ] All automated checks pass
- [ ] Health endpoint returns 200 OK
- [ ] API processes documents and answers questions
- [ ] Response time is under 30 seconds
- [ ] Answers are accurate and detailed
- [ ] No errors in application logs

## 📞 Support Resources

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Deployment Checker**: `python deployment_checker.py`
- **Complete Guide**: See `RENDER_DEPLOYMENT_GUIDE.md`
- **API Documentation**: Visit `/docs` endpoint after deployment

---

**🚀 Ready to deploy? Start with the pre-deployment check and follow each step carefully!**