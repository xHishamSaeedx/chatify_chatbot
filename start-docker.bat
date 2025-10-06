@echo off
echo 🚀 Starting Chatify Chatbot Service...

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found!
    echo 📝 Please copy env.docker.example to .env and configure your environment variables:
    echo    copy env.docker.example .env
    echo    # Then edit .env with your actual configuration
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Build and start services
echo 🔨 Building and starting services...
docker-compose up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are running
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo ❌ Failed to start services. Check logs with: docker-compose logs
    pause
    exit /b 1
) else (
    echo ✅ Chatify Chatbot Service is running!
    echo 🌐 API available at: http://localhost:8000
    echo 📊 Health check: http://localhost:8000/api/v1/health
    echo 🤖 AI Fallback API: http://localhost:8000/api/v1/ai-fallback/
    echo.
    echo 📋 Useful commands:
    echo    docker-compose logs -f          # View logs
    echo    docker-compose down             # Stop services
    echo    docker-compose restart          # Restart services
)

pause

