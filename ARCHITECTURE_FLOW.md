# Chatify Chatbot - Architecture & Logic Flow

## Overview

This document explains how the FastAPI microservice works and how the frontend (React) interacts with it. This will help you understand the architecture before implementing similar functionality in your Flutter app backend.

---

## 🏗️ System Architecture

```
┌─────────────────┐
│  React Frontend │
│   (Web Client)  │
└────────┬────────┘
         │
         │ HTTP REST API
         │
┌────────▼────────────────────────────┐
│      FastAPI Backend                │
│                                     │
│  ┌─────────────────────────────┐  │
│  │  API Endpoints (Routes)     │  │
│  │  - /chatbot/*               │  │
│  │  - /personalities/*         │  │
│  │  - /settings/*              │  │
│  │  - /analytics/*             │  │
│  └──────────┬──────────────────┘  │
│             │                      │
│  ┌──────────▼──────────────────┐  │
│  │  Service Layer              │  │
│  │  - session_service          │  │
│  │  - openai_service           │  │
│  │  - firebase_service         │  │
│  │  - analytics_service        │  │
│  └──────────┬──────────────────┘  │
│             │                      │
└─────────────┼──────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────┐       ┌──────▼──────┐
│Firebase│       │OpenAI API   │
│Database│       │(ChatGPT)    │
└────────┘       └─────────────┘
```

---

## 📱 Frontend to Backend Communication

### 1. **Initial Setup**

The frontend connects to the backend using Axios HTTP client:

```javascript
// Frontend (api.js)
const API_BASE_URL = "https://chatify-chatbot.onrender.com/api/v1";
```

### 2. **API Service Methods**

The frontend has organized API methods for different features:

- **Chatbot Operations** (`chatbotAPI`)

  - Get available personalities
  - Create session
  - Send message
  - Get session details
  - End session
  - Get session stats

- **Personality Management** (`personalityAPI`)

  - CRUD operations for personality templates

- **Settings** (`settingsAPI`)

  - Get/Update universal rules (rules that apply to all AI personalities)

- **Analytics** (`analyticsAPI`)
  - Get overview, personality stats, daily stats, user stats

---

## 🔄 Complete User Flow (Step-by-Step)

### **Step 1: User Opens the App**

**Frontend:**

```javascript
// App.jsx loads and displays the UI
// User sees the chat interface
```

**Backend:**

- Nothing happens yet (backend is ready and waiting)

---

### **Step 2: User Creates a Chat Session**

**Frontend:**

```javascript
// User selects a personality and clicks "Create Session"
const response = await chatbotAPI.createSession(userId, templateId);
```

**Backend Process:**

```
POST /api/v1/chatbot/session
  ↓
1. Generate unique session_id (UUID)
2. Load system prompt from Firebase:
   a. Get "universal rules" (apply to all personalities)
   b. Get personality-specific prompt
   c. Combine them into one system prompt
3. Create session object:
   {
     session_id: "uuid",
     user_id: "user123",
     template_id: "friendly-assistant",
     system_prompt: "combined prompt",
     status: "active",
     created_at: timestamp,
     last_activity: timestamp,
     message_count: 0,
     conversation_history: []
   }
4. Store in two places:
   a. In-memory (Python dict) - for fast access
   b. Firebase Database - for persistence
5. Track analytics (session created)
6. Return session_id to frontend
```

**Response to Frontend:**

```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Session created successfully"
}
```

---

### **Step 3: User Sends First Message**

**Frontend:**

```javascript
// User types "Hi" and clicks send
const response = await chatbotAPI.sendMessage(sessionId, "Hi");
```

**Backend Process:**

```
POST /api/v1/chatbot/session/{session_id}/message
  ↓
1. Validate session exists and is active
2. Add user message to conversation history:
   {
     role: "user",
     content: "Hi",
     timestamp: current_time
   }
3. Prepare messages for OpenAI:
   [
     { role: "system", content: "system prompt" },
     ...previous messages (last 10),
     { role: "user", content: "Hi" }
   ]
4. Call OpenAI API:
   - Model: gpt-4o-mini
   - Temperature: 0.9 (for natural responses)
   - Max tokens: 50 (for short responses)
   - Add penalties to reduce repetition
5. Wait for AI response (add realistic typing delay)
6. Add AI response to conversation history:
   {
     role: "assistant",
     content: "Hey! What's up?",
     timestamp: current_time
   }
7. Update session:
   - last_activity = now
   - message_count += 1
   - Keep only last 20 messages (prevent context overflow)
8. Store updated data:
   - Update in-memory session
   - Update in Firebase
   - Store individual messages in Firebase conversations
9. Track analytics (message sent)
10. Return AI response to frontend
```

**Response to Frontend:**

```json
{
  "success": true,
  "response": "Hey! What's up?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_count": 1
}
```

---

### **Step 4: Conversation Continues**

**Frontend:**

```javascript
// User continues chatting
// Each message follows the same flow as Step 3
```

**Backend:**

- Maintains conversation context
- Each new message includes previous conversation history
- OpenAI uses the full context to generate relevant responses

---

### **Step 5: User Ends Session**

**Frontend:**

```javascript
// User clicks "End Session"
const response = await chatbotAPI.endSession(sessionId);
```

**Backend Process:**

```
DELETE /api/v1/chatbot/session/{session_id}
  ↓
1. Mark session as "ended"
2. Add ended_at timestamp
3. Calculate session duration
4. Track analytics (session ended, duration, message count)
5. Update Firebase with final session data
6. Remove from in-memory active sessions
7. Schedule Firebase conversation cleanup (after 30 seconds)
8. Return success
```

---

## 🔥 Firebase Data Structure

```
firebase-database/
├── templates/              # AI Personality Templates
│   ├── general-assistant/
│   │   ├── name: "General Assistant"
│   │   ├── personalityPrompt: "You are a friendly..."
│   │   ├── welcomeMessage: "Hello!"
│   │   ├── model: "gpt-4o-mini"
│   │   ├── temperature: 0.9
│   │   └── ...
│   └── baddie/
│       └── ...
│
├── settings/
│   └── universalRules/     # Rules that apply to ALL personalities
│       ├── rules: "Keep responses short..."
│       ├── enabled: true
│       └── version: "1.0"
│
├── userSessions/           # Active and recent sessions
│   └── {session_id}/
│       ├── user_id
│       ├── template_id
│       ├── status: "active" | "ended"
│       ├── created_at
│       ├── last_activity
│       ├── message_count
│       └── conversation_history: []
│
└── conversations/          # Message history (temp storage)
    └── {session_id}/
        └── messages/
            ├── message1: {role, content, timestamp}
            ├── message2: {role, content, timestamp}
            └── ...
```

---

## ⚙️ Key Backend Services

### 1. **Session Service** (`session_service.py`)

**Purpose:** Manages chatbot sessions and conversation flow

**Key Methods:**

- `create_session(user_id, template_id)` - Creates new chat session
- `send_message(session_id, message)` - Processes user messages
- `get_session(session_id)` - Retrieves session info
- `end_session(session_id)` - Ends a session
- `cleanup_expired_sessions()` - Removes old sessions (runs every 10 min)

**Key Features:**

- Stores sessions in memory (fast) AND Firebase (persistent)
- Automatically expires sessions after 30 minutes of inactivity
- Limits conversation history to last 20 messages
- Adds realistic typing delays based on message length

---

### 2. **OpenAI Service** (`openai_service.py`)

**Purpose:** Handles communication with OpenAI ChatGPT API

**Key Methods:**

- `chat_completion(messages, model, temperature, max_tokens)` - Core API call
- `conversational_chat(history, message, system_prompt)` - Chat with context

**Configuration:**

- Model: `gpt-4o-mini` (good quality, cost-effective)
- Temperature: `0.9` (natural, varied responses)
- Max Tokens: `50` (short, text-message style responses)
- Penalties: Reduces repetition in responses

**Demo Mode:**

- If no OpenAI API key, uses mock responses
- Good for testing without spending money

---

### 3. **Firebase Service** (`firebase_service.py`)

**Purpose:** Handles all Firebase database operations

**Key Methods:**

- `get_data(path)` - Read data from Firebase
- `set_data(path, data)` - Write/update data
- `push_data(path, data)` - Add new item to list
- `delete_data(path)` - Remove data

**Usage:**

- Store personality templates
- Store universal rules
- Store sessions for persistence
- Store conversation history

---

### 4. **Analytics Service** (`analytics_service.py`)

**Purpose:** Tracks usage statistics

**Tracks:**

- Session creation/ending
- Messages sent
- User activity
- Personality usage
- Daily statistics

---

## 🔐 System Prompt Strategy

The backend uses a **two-layer system prompt**:

### 1. Universal Rules (applies to ALL personalities)

```
CRITICAL RULES:
- Keep responses VERY short (1-9 words max)
- Use casual language and shortforms
- NEVER repeat the same response twice
- Use emojis rarely
- Don't mention being an AI
- Keep it natural like real texting
```

### 2. Personality-Specific Prompt (varies by personality)

```
Example for "Baddie" personality:
"You are a confident, sassy person with attitude.
You don't take nonsense from anyone..."
```

### Combined Approach:

```
final_prompt = universal_rules + "\n\n" + personality_prompt
```

**Why this works:**

- Universal rules ensure consistency across all personalities
- Personality prompts add unique characteristics
- Easy to update rules globally without changing each personality
- Backend caches the combined prompt at session creation (not loaded every message)

---

## 🧹 Automatic Cleanup System

### Background Jobs (APScheduler)

```python
# Runs every 10 minutes
scheduler.add_job(
    session_service.cleanup_expired_sessions,
    'interval',
    minutes=10
)
```

### What Gets Cleaned:

1. **In-Memory Sessions** - Sessions inactive for 30+ minutes
2. **Firebase Sessions** - Sessions inactive for 30+ minutes
3. **Ended Sessions** - Sessions marked "ended" and older than 1 hour
4. **Conversation History** - Deleted 30 seconds after session ends

---

## 🎨 Frontend Components

### 1. **App.jsx** (Main Container)

- Manages overall app state
- Tracks active session
- Manages conversation messages
- Navigation between tabs (Chat, Personalities, Rules, Analytics)

### 2. **ChatInterface.jsx** (Chat UI)

- Displays messages
- Input field for typing
- Send button
- Auto-scroll to latest message
- Loading states

### 3. **SessionManager.jsx** (Session Control)

- Create new session
- Select personality
- Display active session info
- End session button

### 4. **PersonalityManager.jsx** (Admin UI)

- View all personalities
- Create new personality
- Edit existing personality
- Delete personality

### 5. **UniversalRules.jsx** (Settings UI)

- View universal rules
- Edit rules
- Enable/disable rules

### 6. **Analytics.jsx** (Dashboard)

- Session statistics
- Personality usage
- Daily trends
- User activity

---

## 🔄 Request/Response Flow Examples

### Example 1: Creating a Session

**Frontend Request:**

```javascript
POST /api/v1/chatbot/session
Body: {
  "user_id": "user_12345",
  "template_id": "friendly-assistant"
}
```

**Backend Internal Flow:**

```
1. Generate session_id: "550e8400..."
2. Load from Firebase:
   - Universal rules: "Keep responses short..."
   - Personality prompt: "You are friendly..."
3. Combine: system_prompt = rules + prompt
4. Create session object
5. Store in memory & Firebase
6. Track analytics
```

**Backend Response:**

```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Session created successfully"
}
```

---

### Example 2: Sending a Message

**Frontend Request:**

```javascript
POST /api/v1/chatbot/session/550e8400.../message
Body: {
  "message": "What's your favorite color?"
}
```

**Backend Internal Flow:**

```
1. Get session from memory
2. Add user message to history
3. Prepare OpenAI request:
   {
     messages: [
       {role: "system", content: "system_prompt"},
       {role: "user", content: "What's your favorite color?"}
     ]
   }
4. Call OpenAI API
5. Get response: "I love blue! 💙 Yours?"
6. Add to history
7. Update session
8. Save to Firebase
9. Track analytics
```

**Backend Response:**

```json
{
  "success": true,
  "response": "I love blue! 💙 Yours?",
  "session_id": "550e8400...",
  "message_count": 5
}
```

---

## 🚀 How to Implement in Flutter Backend

### 1. **Core Components You Need:**

```
Flutter Backend Structure:
├── models/
│   ├── session.dart        # Session data model
│   ├── message.dart        # Message data model
│   └── personality.dart    # Personality template model
│
├── services/
│   ├── session_service.dart    # Session management
│   ├── openai_service.dart     # OpenAI integration
│   ├── firebase_service.dart   # Firebase operations
│   └── analytics_service.dart  # Analytics tracking
│
├── routes/
│   ├── chatbot_routes.dart     # Chatbot endpoints
│   ├── personality_routes.dart # Personality CRUD
│   ├── settings_routes.dart    # Settings endpoints
│   └── analytics_routes.dart   # Analytics endpoints
│
└── main.dart                    # Server setup
```

---

### 2. **Session Management Implementation:**

```dart
// Pseudo-code for session service
class SessionService {
  Map<String, Session> activeSessions = {};

  Future<Map<String, dynamic>> createSession(String userId, String templateId) async {
    // 1. Generate session ID
    String sessionId = Uuid().v4();

    // 2. Load system prompt
    String universalRules = await FirebaseService.getData('/settings/universalRules');
    String personalityPrompt = await FirebaseService.getData('/templates/$templateId');
    String systemPrompt = '$universalRules\n\n$personalityPrompt';

    // 3. Create session
    Session session = Session(
      sessionId: sessionId,
      userId: userId,
      templateId: templateId,
      systemPrompt: systemPrompt,
      status: 'active',
      createdAt: DateTime.now(),
      conversationHistory: [],
    );

    // 4. Store in memory
    activeSessions[sessionId] = session;

    // 5. Store in Firebase
    await FirebaseService.setData('/userSessions/$sessionId', session.toJson());

    // 6. Return response
    return {
      'success': true,
      'session_id': sessionId,
    };
  }

  Future<Map<String, dynamic>> sendMessage(String sessionId, String message) async {
    // 1. Get session
    Session session = activeSessions[sessionId];

    // 2. Add user message to history
    session.conversationHistory.add({
      'role': 'user',
      'content': message,
      'timestamp': DateTime.now().toIso8601String(),
    });

    // 3. Call OpenAI
    Map<String, dynamic> response = await OpenAIService.chatCompletion(
      messages: [
        {'role': 'system', 'content': session.systemPrompt},
        ...session.conversationHistory,
      ],
    );

    // 4. Add AI response to history
    session.conversationHistory.add({
      'role': 'assistant',
      'content': response['content'],
      'timestamp': DateTime.now().toIso8601String(),
    });

    // 5. Update session
    session.messageCount++;
    session.lastActivity = DateTime.now();

    // 6. Save to Firebase
    await FirebaseService.setData('/userSessions/$sessionId', session.toJson());

    // 7. Return response
    return {
      'success': true,
      'response': response['content'],
      'message_count': session.messageCount,
    };
  }
}
```

---

### 3. **Key Differences for Flutter/Blabinn:**

Since you're building **Blabinn** (a dating app with anonymous chat), here are adaptations:

**For Anonymous 1-on-1 Chat:**

```dart
// Instead of user-to-AI, it's user-to-user
class ConnectionService {
  // Create a connection between two users
  Future<Connection> createConnection(String userId1, String userId2) async {
    String connectionId = Uuid().v4();

    Connection connection = Connection(
      connectionId: connectionId,
      user1Id: userId1,
      user2Id: userId2,
      status: 'active',
      startedAt: DateTime.now(),
      messages: [],
    );

    // Store in Firebase
    await FirebaseService.setData('/connections/$connectionId', connection.toJson());

    return connection;
  }

  // Send message between users
  Future<void> sendMessage(String connectionId, String senderId, String content) async {
    Message message = Message(
      messageId: Uuid().v4(),
      connectionId: connectionId,
      senderId: senderId,
      content: content,
      timestamp: DateTime.now(),
    );

    // Store message in Firebase
    await FirebaseService.pushData('/connections/$connectionId/messages', message.toJson());

    // Send push notification to recipient
    await NotificationService.sendNotification(recipientId, message);
  }
}
```

---

## 🎯 Key Takeaways for Your Flutter Backend

### 1. **Session Management:**

- Use in-memory storage for active sessions (fast access)
- Use Firebase for persistence (survives server restarts)
- Implement automatic cleanup for expired sessions

### 2. **Data Flow:**

- Frontend → API Endpoint → Service Layer → External Services (Firebase/OpenAI)
- Keep business logic in service layer, not in routes

### 3. **System Prompts (if using AI):**

- Combine universal rules with personality-specific prompts
- Cache prompts at session creation, not every message
- Make rules easy to update globally

### 4. **Conversation Context:**

- Maintain conversation history in session
- Limit history to last 10-20 messages to prevent token overflow
- Include full context when calling AI API

### 5. **Performance:**

- Use in-memory cache for frequently accessed data
- Batch Firebase writes when possible
- Add realistic delays for better UX (typing indicators)

### 6. **Analytics:**

- Track session creation, messages sent, session duration
- Store aggregated stats for dashboards
- Log important events for debugging

### 7. **Cleanup:**

- Implement background jobs for cleanup
- Set reasonable timeouts (30 min for chat sessions)
- Clean up both in-memory and persistent storage

---

## 📊 Performance Optimizations

### 1. **Caching Strategy:**

```
✅ Cache in session:
- System prompt (loaded once at creation)
- Conversation history (in memory)
- User preferences

❌ Don't cache:
- Real-time data (active sessions count)
- Analytics (changes frequently)
```

### 2. **Database Reads:**

```
Minimize Firebase reads by:
- Loading templates once at startup
- Caching universal rules
- Using in-memory sessions
- Only syncing changes to Firebase
```

### 3. **API Calls:**

```
Optimize OpenAI calls:
- Include only relevant context (last 10 messages)
- Use appropriate model (gpt-4o-mini is good)
- Set reasonable max_tokens limit
- Add penalties to reduce repetition
```

---

## 🔒 Security Considerations

### 1. **API Keys:**

- Never expose API keys to frontend
- Store in environment variables
- Use separate keys for dev/prod

### 2. **Session Validation:**

- Always validate session exists before processing
- Check session ownership (user can only access their sessions)
- Verify session is active before allowing messages

### 3. **Input Validation:**

- Sanitize user messages
- Limit message length (e.g., 4000 characters max)
- Rate limiting to prevent spam

### 4. **Firebase Security Rules:**

```javascript
// Example Firebase rules
{
  "rules": {
    "userSessions": {
      "$sessionId": {
        ".read": "auth != null && data.child('user_id').val() === auth.uid",
        ".write": "auth != null"
      }
    }
  }
}
```

---

## 🧪 Testing Recommendations

### 1. **Unit Tests:**

- Test each service method independently
- Mock external dependencies (OpenAI, Firebase)
- Test edge cases (expired sessions, invalid input)

### 2. **Integration Tests:**

- Test complete flows (create session → send message → end session)
- Test Firebase integration
- Test OpenAI integration

### 3. **Load Tests:**

- Test with multiple concurrent sessions
- Test cleanup jobs under load
- Monitor memory usage

---

## 📚 Additional Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **OpenAI API Docs:** https://platform.openai.com/docs/
- **Firebase Admin SDK:** https://firebase.google.com/docs/admin/setup
- **APScheduler Docs:** https://apscheduler.readthedocs.io/

---

## 🎉 Summary

This FastAPI microservice provides:

1. ✅ RESTful API for chat functionality
2. ✅ Session management with persistence
3. ✅ AI integration with OpenAI
4. ✅ Flexible personality system
5. ✅ Universal rules for consistency
6. ✅ Automatic cleanup and maintenance
7. ✅ Analytics tracking
8. ✅ Firebase integration for data persistence

**The same principles apply to your Flutter backend, just adapt the implementation to Dart and your specific use case (user-to-user chat vs user-to-AI).**
