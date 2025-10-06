# Local Development Setup

This guide will help you set up both the backend and frontend for local development.

## Prerequisites

- Python 3.8+ installed
- Flutter SDK installed
- Git installed

## Backend Setup (chatify_chatbot)

### 1. Navigate to backend directory
```bash
cd S:\Projects\chatify_chatbot
```

### 2. Run the setup script
```bash
python setup_local_dev.py
```

### 3. Configure environment variables
- Copy `env.example` to `.env`
- Update the `.env` file with your actual values:
  - Firebase credentials
  - OpenAI API key
  - Other required environment variables

### 4. Start the backend server
```bash
python setup_local_dev.py --run
```

The backend will be available at: http://127.0.0.1:8000
API documentation: http://127.0.0.1:8000/docs

## Frontend Setup (Blabinn-Frontend)

### 1. Navigate to frontend directory
```bash
cd S:\Projects\Blabinn-Frontend
```

### 2. Run the setup script
**Windows:**
```cmd
setup_local_dev.bat
```

**macOS/Linux:**
```bash
chmod +x setup_local_dev.sh
./setup_local_dev.sh
```

### 3. Update IP address (if needed)
- Open `lib/core/env_config.dart`
- Update `apiBaseUrlAndroid` with your computer's IP address
- Find your IP with: `ipconfig` (Windows) or `ifconfig` (macOS/Linux)

### 4. Start the frontend
```bash
flutter run
```

## Development Workflow

1. Start the backend first: `python setup_local_dev.py --run`
2. Start the frontend: `flutter run`
3. Both applications will communicate locally

## Troubleshooting

### Backend Issues
- Ensure all environment variables are set in `.env`
- Check that port 8000 is not in use
- Verify Firebase credentials are correct

### Frontend Issues
- Ensure Flutter is properly installed
- Check that the IP address in `env_config.dart` matches your computer's IP
- Verify the backend is running and accessible

### Connection Issues
- Check firewall settings
- Ensure both applications are on the same network
- Verify CORS settings in backend configuration

## Environment Configuration

The frontend is configured to use:
- **Android**: `http://YOUR_IP:8000` (update in env_config.dart)
- **iOS/Web**: `http://localhost:8000`
- **Environment**: `development`

## API Endpoints

When running locally, the backend provides:
- Health check: http://127.0.0.1:8000/health
- API docs: http://127.0.0.1:8000/docs
- API base: http://127.0.0.1:8000/api/v1
