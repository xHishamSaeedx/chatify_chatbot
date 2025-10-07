# Chatify Chatbot Service - Docker Setup

This guide will help you run the Chatify Chatbot service using Docker for easy development and testing.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Your environment variables configured

### 1. Setup Environment
```bash
# Copy the example environment file
cp env.docker.example .env

# Edit .env with your actual configuration
# You need to set:
# - FIREBASE_PROJECT_ID
# - FIREBASE_PRIVATE_KEY  
# - FIREBASE_CLIENT_EMAIL
# - OPENAI_API_KEY
```

### 2. Start the Service
```bash
# On Windows
start-docker.bat

# On Linux/Mac
./start-docker.sh
```

### 3. Verify It's Working
```bash
# Test the API
python test-api.py

# Or check manually
curl http://localhost:8000/api/v1/health
```

## 📋 Available Services

Once running, the following services will be available:

- **Main API**: http://localhost:8000
- **Health Check**: http://localhost:8000/api/v1/health
- **AI Fallback API**: http://localhost:8000/api/v1/ai-fallback/
- **Redis**: localhost:6379

## 🔧 Useful Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up --build -d

# Check service status
docker-compose ps
```

## 🧪 Testing the AI Fallback

1. Start the service using the commands above
2. Run the test script: `python test-api.py`
3. The test will:
   - Set a matching state for a test user
   - Wait for the 10-second timeout
   - Trigger AI fallback
   - Verify the AI chatbot is created

## 🐛 Troubleshooting

### Service Won't Start
- Check if Docker Desktop is running
- Verify your `.env` file has all required variables
- Check logs: `docker-compose logs`

### API Connection Issues
- Verify the service is running: `docker-compose ps`
- Test health endpoint: `curl http://localhost:8000/api/v1/health`
- Check if port 8000 is available

### AI Fallback Not Working
- Check OpenAI API key in `.env`
- Verify Redis is running: `docker-compose ps`
- Test with: `python test-api.py`

## 📁 File Structure

```
chatify_chatbot/
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Service orchestration
├── start-docker.bat        # Windows startup script
├── start-docker.sh         # Linux/Mac startup script
├── test-api.py            # API testing script
├── env.docker.example     # Environment template
└── README_DOCKER.md       # This file
```

## 🔗 Integration with Flutter App

Once the Docker service is running, your Flutter app should be able to connect to:
- `http://localhost:8000` (if running on same machine)
- `http://your-server-ip:8000` (if running on different machine)

Make sure your Flutter app's API configuration points to the correct URL.

