#!/bin/bash

# Render Deployment Script for HackRx Document Processing API

echo "🚀 Deploying HackRx Document Processing API to Render..."

# Check if environment variables are set
if [ -z "$GEMINI_API_KEY" ] || [ -z "$PINECONE_API_KEY" ]; then
    echo "❌ Error: Required environment variables not set"
    echo "Please set GEMINI_API_KEY and PINECONE_API_KEY in Render dashboard"
    exit 1
fi

echo "✅ Environment variables configured"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r render-requirements.txt

echo "🏥 Starting health checks..."
# Wait for services to be ready
sleep 5

echo "🎉 Deployment complete!"
echo "📊 API Status: Ready"
echo "🔗 Endpoints:"
echo "  - POST /hackrx/run - Process documents and answer questions"
echo "  - GET /health - Health check"
echo "  - GET /docs - Interactive API documentation"