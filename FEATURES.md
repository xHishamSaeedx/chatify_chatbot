# Chatify Chatbot - Features & Architecture

## 🚀 Overview

Chatify is a multi-personality chatbot system built with FastAPI, OpenAI, and Firebase. It supports multiple concurrent users with different personality types, each with unique conversation styles and behaviors.

## ✨ Key Features

### 1. **Multiple Personality Types**
- **13 Different Personalities** with unique conversation styles
- **Dynamic Personality Selection** via API or web interface
- **Consistent Personality Behavior** throughout conversations

### 2. **Multi-User Support**
- **Concurrent Sessions** - Multiple users can chat simultaneously
- **Session Isolation** - Each user's conversation is completely separate
- **Unique Session IDs** - UUID-based session management
- **Real-time Communication** - Fast response times

### 3. **Smart Memory Management**
- **Automatic Cleanup** - Sessions expire after 30 minutes of inactivity
- **Memory Optimization** - Only last 20 messages kept in memory
- **Firebase Cleanup** - Conversation history deleted 30 seconds after session ends
- **No Memory Leaks** - Proper cleanup of ended sessions

### 4. **Realistic Typing Simulation**
- **Base Delay** - 1-2 seconds for all responses
- **Word-based Delay** - Additional 0.3s per word beyond 2 words
- **Emoji Delay** - Additional 0.2s per emoji
- **Maximum Delay** - Capped at 8 seconds for very long messages

### 5. **Robust Architecture**
- **FastAPI Backend** - High-performance async API
- **OpenAI Integration** - GPT-powered responses
- **Firebase Database** - Persistent session storage
- **Error Handling** - Graceful failure management

## 🎭 Personality Types

| Personality | Description | Style |
|-------------|-------------|-------|
| **General** | Friendly and casual | "Heyy, not much! Just kicking back. U?" |
| **Baddie** | Confident and sassy | "Just living my best life, you? 🔥" |
| **Hot Bold** | Bold and flirty | "What's good? 😏" |
| **Party Girl** | Fun and energetic | "Heyy! 🎉" |
| **Career-Driven** | Ambitious hustler | "Grinding hard, what about you?" |
| **Hippie** | Peaceful and spiritual | "Peace ✌️" |
| **Content Creator** | Creative and trendy | "Just vibing, you? ✨" |
| **Innocent** | Sweet and cute | "Hey! Just being cute, you? 😊" |
| **Sarcastic** | Witty and savage | "Just living my best life, you?" |
| **Romantic** | Dreamy and loving | "Hi, lost in daydreams of love. 💖" |
| **Mysterious** | Quiet and intriguing | "Hey. Just thoughts wandering. You?" |
| **Pick-Me** | Tries too hard | "Hi, just being different. You?" |
| **Clingy** | Possessive and needy | "Hi 💕 Just thinking about you." |

## 🏗️ Architecture

### Backend Components

```
app/
├── api/v1/endpoints/          # API endpoints
│   ├── chat.py               # Direct chat endpoints
│   └── chatbot.py            # Session management endpoints
├── services/                 # Core services
│   ├── session_service.py    # Session management
│   ├── openai_service.py     # OpenAI integration
│   └── firebase_service.py   # Firebase operations
├── schemas/                  # Data models
└── static/                   # Web interface
    └── index.html           # Test interface
```

### Data Flow

1. **Session Creation** → Generate UUID → Store in memory + Firebase
2. **Message Processing** → OpenAI API → Response → Update history
3. **Session End** → Mark as ended → Cleanup memory → Schedule Firebase cleanup
4. **Background Cleanup** → Wait 30 seconds → Delete Firebase conversation history

## 🔧 API Endpoints

### Session Management
- `POST /api/v1/chatbot/session` - Create new session
- `GET /api/v1/chatbot/session/{session_id}` - Get session info
- `DELETE /api/v1/chatbot/session/{session_id}` - End session
- `POST /api/v1/chatbot/session/{session_id}/message` - Send message

### Personality Management
- `GET /api/v1/chatbot/personalities` - List all personalities
- `GET /api/v1/chatbot/stats` - Get session statistics
- `POST /api/v1/chatbot/cleanup` - Manual cleanup

### Direct Chat (No Sessions)
- `POST /api/v1/chat/` - Chat with conversation history
- `POST /api/v1/chat/simple` - Simple chat
- `POST /api/v1/chat/conversation` - Full conversation context

## 💾 Data Storage

### Memory (Active Sessions)
```python
active_sessions = {
    "session_id": {
        "session_id": "uuid",
        "user_id": "user123",
        "template_id": "baddie",
        "status": "active",
        "conversation_history": [...],  # Last 20 messages
        "message_count": 5,
        "created_at": "2024-01-01T00:00:00",
        "last_activity": "2024-01-01T00:05:00"
    }
}
```

### Firebase Structure
```
/userSessions/{session_id}     # Session metadata
/conversations/{session_id}/   # Conversation history (deleted after 30s)
/templates/{template_id}       # Personality templates
```

## 🔄 Session Lifecycle

1. **Creation** - User selects personality → Session created → UUID generated
2. **Active** - Messages exchanged → History updated → Last activity tracked
3. **Expiration** - 30 minutes inactivity → Auto-cleanup triggered
4. **End** - User ends session → Memory cleaned → Firebase cleanup scheduled
5. **Cleanup** - 30 seconds later → Firebase conversation history deleted

## 🛡️ Security & Privacy

- **No Persistent Data** - Conversation history automatically deleted
- **Session Isolation** - Users cannot access other sessions
- **Input Validation** - Message length limits (4000 chars)
- **Error Handling** - Graceful failure without data exposure

## 🚀 Performance

- **Async Operations** - Non-blocking API calls
- **Memory Efficient** - Only active sessions in memory
- **Fast Response** - OpenAI API with optimized prompts
- **Scalable** - Handles multiple concurrent users

## 🧪 Testing

### Web Interface
- Access: `http://localhost:8000/static/index.html`
- Features: Personality selection, session management, real-time chat
- Multi-tab support for testing concurrent users

### API Testing
```bash
# Create session
curl -X POST "http://localhost:8000/api/v1/chatbot/session" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "template_id": "baddie"}'

# Send message
curl -X POST "http://localhost:8000/api/v1/chatbot/session/{session_id}/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hey, what'\''s up?"}'
```

## 📋 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_key
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_DATABASE_URL=your_database_url
# ... other Firebase config
```

### Settings
- **Session Timeout**: 30 minutes
- **Firebase Cleanup Delay**: 30 seconds
- **Max Messages in Memory**: 20
- **Max Message Length**: 4000 characters
- **Typing Delay**: 1-2s base + 0.3s/word + 0.2s/emoji (max 8s)

## 🔮 Future Enhancements

- [ ] User authentication
- [ ] Conversation analytics
- [ ] Custom personality creation
- [ ] Message encryption
- [ ] Rate limiting
- [ ] WebSocket support for real-time updates

## 📞 Support

For issues or questions:
1. Check the logs for error messages
2. Verify OpenAI API key is valid
3. Ensure Firebase configuration is correct
4. Test with the web interface first

---

**Built with ❤️ using FastAPI, OpenAI, and Firebase**
