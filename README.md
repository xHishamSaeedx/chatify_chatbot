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

# Chatify Chatbot Integration Plan

## Overview

When users don't get matched within 10 seconds in the random connection feature, they will be automatically connected to the Chatify Chatbot for an engaging AI conversation experience.

## How It Works

1. User starts random connection
2. System waits 10 seconds for a match
3. If no match found → Connect to Chatify Chatbot
4. User chats with AI while waiting for human matches

## What Needs to Be Built

### 1. Redis Server Changes (Blabbin-Redis)

**Modify Timeout Logic**

- Change from 5-minute timeout to 10-second chatbot trigger
- Add new timeout reason: "chatbot_fallback_triggered"
- Send webhook to backend when 10 seconds pass without match

**New Webhook Endpoint**

- Add chatbot fallback webhook to notify backend
- Include user profile data for chatbot personalization

### 2. Backend Changes (Blabbin)

**Modify Timeout Handler**

- Add logic to detect 10-second chatbot triggers
- Automatically call Chatify Chatbot API
- Send WebSocket notification to user

**New Controller**

- Handle chatbot connection requests
- Manage active chatbot sessions
- End chatbot sessions when needed

### 3. Chatify Chatbot Enhancements

**New API Endpoints**

- Create chatbot session for user
- Send/receive messages
- Get session details
- End session

**Session Management**

- Handle multiple users simultaneously
- Load different AI personality templates
- Store conversation history

**Prompt Template System**

- Store AI personalities in Firebase
- Different templates: casual chat, dating advice, general conversation
- Personalize based on user profile

### 4. Firebase Database Structure

**Prompt Templates Collection**

- Store different AI personalities
- Each template has system prompt, temperature, token limits

**Chatbot Sessions Collection**

- Track active user sessions
- Store session status, user info, template used

**Conversation History Collection**

- Store all chat messages per session
- Track token usage and conversation flow

### 5. API Endpoints Needed

**Redis Server (Blabbin-Redis)**

- Send chatbot fallback webhook to backend
- Include user profile data for personalization

**Blabbin Backend**

- Connect user to chatbot
- Get user's active chatbot session
- End chatbot session

**Chatify Chatbot**

- Create new session
- Send message to session
- Get session details
- End session
- Get available templates

### 6. WebSocket Events

**New Events**

- User connected to chatbot
- New message from chatbot
- Chatbot session ended

### 7. Implementation Steps

1. Set up Firebase collections for prompt templates
2. Modify Redis server timeout logic (5 min → 10 sec)
3. Build chatbot session service in Chatify
4. Modify timeout handler in Blabbin backend
5. Create API endpoints in all services
6. Add WebSocket notifications
7. Frontend integration for chatbot UI
8. Testing and optimization

### 8. Benefits

- Users always have someone to talk to
- Keeps users engaged during wait times
- Collects conversation data for insights
- Handles unlimited concurrent users
- Customizable AI personalities

### 9. Configuration Needed

**Environment Variables**

- Chatify Bot URL and API key
- OpenAI API key
- Firebase project settings
- Timeout duration (10 seconds)

This creates a seamless fallback system ensuring users always have an engaging conversation experience.

## Detailed Implementation Guide

### Prompt Template System in Firebase

**How to Set Up Templates**

1. **Create Firebase Collections**

   - Collection: `prompt_templates`
   - Document IDs: `casual_chat`, `dating_advice`, `general_conversation`, `flirty_chat`

2. **Template Structure**

   ```
   casual_chat: {
     name: "Friendly Companion",
     system_prompt: "You are a warm, friendly AI companion...",
     temperature: 0.8,
     max_tokens: 500,
     personality_traits: ["friendly", "supportive", "conversational"],
     created_at: timestamp,
     updated_at: timestamp
   }
   ```

3. **Template Selection Logic**

   - Default: `casual_chat` for most users
   - User preference: Based on user's interests or previous conversations
   - Time-based: Different templates for different times of day
   - Context-aware: Dating advice template if user mentions relationship topics

4. **Personalization Variables**
   - User's name, age, interests
   - Previous conversation topics
   - User's communication style
   - Current mood or context

**How to Load Templates**

1. **Service Method**: `PromptService.get_template(template_type)`
2. **Caching**: Store templates in memory for fast access
3. **Fallback**: Default template if specific one not found
4. **Updates**: Refresh templates periodically from Firebase

### Conversation Management for Multiple Users

**How to Handle Multiple Concurrent Users**

1. **Session Isolation**

   - Each user gets unique session ID
   - Separate conversation history per session
   - Independent AI context per user

2. **Memory Management**

   - Store conversation history in Firebase
   - Limit conversation length (last 20 messages)
   - Compress old messages to save tokens

3. **User State Tracking**

   ```
   Session Data: {
     session_id: "uuid",
     user_id: "user123",
     template_type: "casual_chat",
     conversation_history: [...],
     last_activity: timestamp,
     message_count: 15,
     total_tokens_used: 1200
   }
   ```

4. **Concurrent User Handling**
   - Use async/await for non-blocking operations
   - Connection pooling for Firebase
   - Rate limiting per user
   - Session cleanup for inactive users

**How to Maintain Conversations**

1. **Message Flow**

   - User sends message → Store in Firebase → Send to OpenAI → Store response → Return to user

2. **Context Management**

   - Keep last 10-15 messages for context
   - Include user profile in system prompt
   - Maintain conversation topic awareness

3. **Session Lifecycle**

   - Create: When user connects to chatbot
   - Active: During conversation
   - Pause: When user stops responding (5+ minutes)
   - Resume: When user returns
   - End: When user disconnects or manually ends

4. **Data Persistence**
   - Store all messages with timestamps
   - Track token usage per session
   - Save conversation summaries
   - Analytics data for improvement

**How to Scale for Many Users**

1. **Database Optimization**

   - Index on user_id and session_id
   - Partition conversations by date
   - Use Firebase batch operations

2. **Performance Strategies**

   - Cache active sessions in Redis
   - Async message processing
   - Connection pooling
   - Load balancing across instances

3. **Resource Management**

   - Monitor OpenAI API usage
   - Implement rate limiting
   - Clean up old sessions
   - Optimize prompt templates

4. **Monitoring & Analytics**
   - Track active sessions count
   - Monitor response times
   - User satisfaction metrics
   - Conversation quality scores

**Implementation Priority**

1. **Phase 1**: Basic template system with 2-3 templates
2. **Phase 2**: Session management for single user
3. **Phase 3**: Multi-user concurrent support
4. **Phase 4**: Advanced personalization
5. **Phase 5**: Analytics and optimization

This approach ensures the chatbot can handle multiple users efficiently while providing personalized, engaging conversations.
