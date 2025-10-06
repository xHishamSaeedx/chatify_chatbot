#!/bin/bash

# Start Chatify Chatbot Service with Docker Compose

echo "🚀 Starting Chatify Chatbot Service..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Please copy env.docker.example to .env and configure your environment variables:"
    echo "   cp env.docker.example .env"
    echo "   # Then edit .env with your actual configuration"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Chatify Chatbot Service is running!"
    echo "🌐 API available at: http://localhost:8000"
    echo "📊 Health check: http://localhost:8000/api/v1/health"
    echo "🤖 AI Fallback API: http://localhost:8000/api/v1/ai-fallback/"
    echo ""
    echo "📋 Useful commands:"
    echo "   docker-compose logs -f          # View logs"
    echo "   docker-compose down             # Stop services"
    echo "   docker-compose restart          # Restart services"
else
    echo "❌ Failed to start services. Check logs with: docker-compose logs"
    exit 1
fi

