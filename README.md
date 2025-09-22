# FastAPI Boilerplate

A simple, clean FastAPI microservice boilerplate ready for development.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation using Python type annotations
- **Testing** - Basic test suite with pytest
- **CORS** - Cross-origin resource sharing configured
- **Environment Configuration** - Easy configuration management

## Project Structure

```
fastapi_boilerplate/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Application configuration
│   └── api/
│       └── v1/
│           ├── __init__.py
│           └── api.py         # Main API router
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Test configuration
│   └── test_main.py          # Main app tests
├── requirements.txt          # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/v1/` - API root
- `GET /api/v1/health` - API health check
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_main.py
```

## Development

### Code Formatting

```bash
# Format code with black
black app/ tests/

# Sort imports with isort
isort app/ tests/
```

## Environment Variables

| Variable       | Description                          | Default               |
| -------------- | ------------------------------------ | --------------------- |
| `PROJECT_NAME` | Application name                     | "FastAPI Boilerplate" |
| `ENVIRONMENT`  | Environment (development/production) | "development"         |
| `DEBUG`        | Debug mode                           | true                  |
| `LOG_LEVEL`    | Logging level                        | "INFO"                |

## License

This project is licensed under the MIT License.
