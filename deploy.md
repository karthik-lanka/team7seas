# Deployment Guide for Render

This guide provides step-by-step instructions to deploy the HackRx Document Processing API on Render.

## Prerequisites

Before deploying, ensure you have:

1. **Render Account** - Sign up at [render.com](https://render.com)
2. **GitHub Repository** - Your code should be in a GitHub repository
3. **API Keys** - Obtain the required API keys:
   - Google Gemini API Key from [ai.google.dev](https://ai.google.dev/)
   - Pinecone API Key from [pinecone.io](https://www.pinecone.io/)

## Project Structure

Ensure your repository has these files:

```
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies (create from render-requirements.txt)
├── document_processor.py   # Document processing logic
├── text_chunker.py        # Text chunking functionality
├── gemini_client.py       # Gemini AI integration
├── pinecone_client.py     # Pinecone vector database
├── question_answerer.py   # Question answering logic
├── models.py              # Pydantic data models
├── README.md              # Project documentation
└── deploy.md              # This deployment guide
```

## Step 1: Prepare Your Repository

1. **Check Dependencies**: Create a `requirements.txt` file with all necessary packages:
   ```
   fastapi>=0.116.1
   uvicorn>=0.35.0
   pydantic>=2.11.7
   requests>=2.32.4
   pymupdf>=1.26.3
   python-docx>=1.2.0
   google-genai>=1.28.0
   pinecone-client>=6.0.0
   ```
   
   **Note**: If using this Replit project, copy the contents from `render-requirements.txt` to create your `requirements.txt` file in your GitHub repository.

2. **Verify Entry Point**: Ensure `main.py` contains the FastAPI app and can run with uvicorn:
   ```python
   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="0.0.0.0", port=5000)
   ```

## Step 2: Deploy to Render

### Option A: Deploy from GitHub (Recommended)

1. **Connect GitHub**:
   - Log into your Render dashboard
   - Click "New +" and select "Web Service"
   - Connect your GitHub account if not already connected
   - Select your repository containing the HackRx API

2. **Configure Web Service**:
   - **Name**: `hackrx-document-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users (e.g., `Oregon (US West)`)
   - **Branch**: `main` (or your deployment branch)
   - **Root Directory**: Leave empty (unless code is in subfolder)

3. **Build & Deploy Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host=0.0.0.0 --port=$PORT`
   - **Instance Type**: Choose based on expected load:
     - `Free` (for testing - has limitations)
     - `Starter` ($7/month - recommended for production)
     - `Standard` ($25/month - for higher traffic)

### Option B: Deploy from Git Repository

1. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Select "Public Git repository"
   - Enter your repository URL: `https://github.com/yourusername/your-repo-name`

2. **Follow the same configuration steps as Option A**

## Step 3: Environment Variables

In the Render dashboard, add these environment variables:

### Required Variables

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `GEMINI_API_KEY` | `your_gemini_api_key` | Google Gemini AI API key |
| `PINECONE_API_KEY` | `your_pinecone_api_key` | Pinecone vector database API key |

### Optional Variables

| Variable Name | Default Value | Description |
|---------------|---------------|-------------|
| `PINECONE_INDEX` | `hackrx-documents` | Pinecone index name |
| `PINECONE_ENV` | `us-east-1` | Pinecone environment region |

### How to Add Environment Variables

1. Go to your service dashboard on Render
2. Click on "Environment" tab
3. Click "Add Environment Variable"
4. Enter the variable name and value
5. Click "Save Changes"

## Step 4: Custom Domain (Optional)

1. **Add Custom Domain**:
   - Go to "Settings" tab in your service
   - Scroll to "Custom Domains"
   - Click "Add Custom Domain"
   - Enter your domain (e.g., `api.yourdomain.com`)

2. **Configure DNS**:
   - Add a CNAME record pointing to your Render service URL
   - Wait for DNS propagation (usually 5-15 minutes)

## Step 5: Verify Deployment

Once deployed, test your API:

### Health Check
```bash
curl https://your-app-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "HackRx Document Processing API"
}
```

### Full API Test
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

## Step 6: Monitor and Maintain

### Monitoring

1. **Render Dashboard**:
   - Monitor service health and logs
   - Check resource usage and performance metrics
   - View deployment history

2. **Log Access**:
   - Click "Logs" tab to view real-time application logs
   - Monitor for errors and performance issues

### Scaling

1. **Vertical Scaling**:
   - Upgrade instance type in service settings
   - Options: Free → Starter → Standard → Pro

2. **Horizontal Scaling**:
   - Available on Standard plans and above
   - Configure auto-scaling based on CPU/memory usage

### Updates

1. **Automatic Deployment**:
   - Render automatically deploys when you push to the connected branch
   - Monitor the "Deploys" tab for deployment status

2. **Manual Deployment**:
   - Click "Manual Deploy" → "Deploy latest commit"
   - Use for immediate deployments without code changes

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check `requirements.txt` for correct package names
   - Verify Python version compatibility
   - Review build logs for specific error messages

2. **Runtime Errors**:
   - Ensure all environment variables are set correctly
   - Check application logs for startup errors
   - Verify API keys are valid and have proper permissions

3. **Connection Issues**:
   - Test Pinecone connectivity with provided API key
   - Verify Gemini API key has proper permissions
   - Check if external document URLs are accessible

4. **Performance Issues**:
   - Upgrade to a higher instance type
   - Monitor resource usage in Render dashboard
   - Optimize code for better performance

### Getting Help

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Render Community**: [community.render.com](https://community.render.com)
- **Support**: Contact through Render dashboard

## Security Best Practices

1. **Environment Variables**:
   - Never commit API keys to your repository
   - Use Render's environment variable feature
   - Rotate API keys regularly

2. **HTTPS**:
   - Render provides automatic HTTPS
   - Always use HTTPS URLs for API calls

3. **Authentication**:
   - Keep the bearer token secure
   - Consider implementing token rotation for production

## Cost Optimization

1. **Free Tier Limitations**:
   - 750 hours/month compute time
   - Services sleep after 15 minutes of inactivity
   - Limited bandwidth and memory

2. **Paid Plans**:
   - Starter: $7/month - No sleeping, better performance
   - Standard: $25/month - More resources, autoscaling
   - Pro: Custom pricing - Enterprise features

3. **Resource Management**:
   - Monitor usage through Render dashboard
   - Scale down during low-traffic periods
   - Optimize code to reduce compute time

## Production Checklist

Before going live:

- [ ] All environment variables configured
- [ ] API keys tested and working
- [ ] Health endpoint responding correctly
- [ ] Full API workflow tested
- [ ] Custom domain configured (if needed)
- [ ] Monitoring and alerting set up
- [ ] Backup and disaster recovery plan
- [ ] Performance testing completed
- [ ] Security review conducted
- [ ] Documentation updated

## API Endpoints Summary

Once deployed, your API will be available at:

- **Base URL**: `https://your-app-name.onrender.com`
- **Health Check**: `GET /health`
- **Main Endpoint**: `POST /hackrx/run`
- **Documentation**: `GET /docs` (FastAPI auto-generated)

## Support

For deployment-specific issues:
1. Check Render service logs first
2. Review this deployment guide
3. Consult Render documentation
4. Contact support through appropriate channels

Your HackRx Document Processing API should now be successfully deployed and running on Render!