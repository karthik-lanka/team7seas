# Deployment Checklist for Render

Use this checklist to ensure your HackRx Document Processing API is ready for deployment on Render.

## ✅ Pre-Deployment Checklist

### Repository Setup
- [ ] All code files are in GitHub repository
- [ ] `requirements.txt` created from `render-requirements.txt` 
- [ ] `main.py` has proper uvicorn entry point
- [ ] All API endpoints tested locally
- [ ] No hardcoded secrets in code

### Required Files Check
- [ ] `main.py` - FastAPI application
- [ ] `requirements.txt` - Python dependencies
- [ ] `document_processor.py` - Document processing
- [ ] `text_chunker.py` - Text chunking
- [ ] `gemini_client.py` - Gemini AI integration
- [ ] `pinecone_client.py` - Pinecone database
- [ ] `question_answerer.py` - Q&A logic
- [ ] `models.py` - Pydantic models
- [ ] `README.md` - Documentation
- [ ] `deploy.md` - Deployment guide

### API Testing
- [ ] Health endpoint (`/health`) responds correctly
- [ ] Main endpoint (`/hackrx/run`) processes documents
- [ ] Bearer token authentication works
- [ ] All three required headers tested:
  - [ ] `Content-Type: application/json`
  - [ ] `Accept: application/json`
  - [ ] `Authorization: Bearer 9953d967b81381295864fb71b20cd27085ee80c24512eeabce64f3f921bb009d`

### API Keys and Secrets
- [ ] Google Gemini API key obtained and tested
- [ ] Pinecone API key obtained and tested
- [ ] Both keys have proper permissions
- [ ] Keys are NOT in repository code

## 🚀 Render Deployment Steps

### 1. Service Creation
- [ ] Render account created
- [ ] GitHub repository connected
- [ ] Web Service created from repository
- [ ] Python 3 environment selected

### 2. Build Configuration
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn main:app --host=0.0.0.0 --port=$PORT`
- [ ] Correct branch selected (usually `main`)
- [ ] Instance type chosen (Starter recommended)

### 3. Environment Variables
- [ ] `GEMINI_API_KEY` added with your Google API key
- [ ] `PINECONE_API_KEY` added with your Pinecone API key
- [ ] Optional: `PINECONE_INDEX` (default: hackrx-documents)
- [ ] Optional: `PINECONE_ENV` (default: us-east-1)

### 4. Deployment Verification
- [ ] Service deployed successfully
- [ ] No build errors in logs
- [ ] Service is running (not crashed)
- [ ] Health check responds: `GET https://your-app.onrender.com/health`

### 5. API Testing on Render
Test with the complete curl command:
```bash
curl -X POST https://your-app-name.onrender.com/hackrx/run \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer 9953d967b81381295864fb71b20cd27085ee80c24512eeabce64f3f921bb009d" \
  -d '{
    "documents": "https://www.orimi.com/pdf-test.pdf",
    "questions": ["What is this document about?"]
  }'
```

Expected response format:
```json
{
  "answers": ["The document is about..."]
}
```

## 🔧 Post-Deployment Tasks

### Monitoring Setup
- [ ] Check Render dashboard for service health
- [ ] Monitor logs for any errors
- [ ] Verify resource usage is within limits
- [ ] Set up alerts if needed

### Performance Testing
- [ ] Test with larger PDF documents
- [ ] Test with multiple questions
- [ ] Verify response times are acceptable
- [ ] Monitor memory and CPU usage

### Documentation Updates
- [ ] Update README.md with live Render URL
- [ ] Share API documentation with team
- [ ] Document any environment-specific configurations

## 🚨 Troubleshooting Guide

### Common Build Issues
- **Dependencies not installing**: Check `requirements.txt` format
- **Python version errors**: Ensure Python 3.11+ compatibility
- **Memory issues**: Upgrade to Starter plan or higher

### Runtime Issues
- **Service crashes on startup**: Check environment variables
- **API key errors**: Verify keys are valid and properly set
- **Pinecone connection errors**: Check API key and region settings
- **Gemini API errors**: Verify API key has proper permissions

### API Issues
- **401 Unauthorized**: Check bearer token in Authorization header
- **404 Not Found**: Verify endpoint URL is correct
- **500 Internal Server Error**: Check service logs for details
- **Timeout errors**: Consider upgrading instance type

## 📞 Support Resources

- **Render Documentation**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Google Gemini API**: https://ai.google.dev/docs
- **Pinecone Documentation**: https://docs.pinecone.io

## ✅ Final Verification

Before marking deployment complete:
- [ ] API responds to health checks
- [ ] Document processing works end-to-end
- [ ] Questions are answered correctly
- [ ] All headers are properly handled
- [ ] Error handling works as expected
- [ ] Performance is acceptable
- [ ] Logs show no critical errors

**Deployment Status**: 
- [ ] **READY FOR PRODUCTION** - All checks passed
- [ ] **NEEDS FIXES** - See issues above
- [ ] **IN PROGRESS** - Still completing checklist

---

**Date Completed**: ___________  
**Deployed By**: ___________  
**Render Service URL**: ___________