# Chatify Chatbot - Chat Process Flow

## Overview

This document explains the core chat functionality - how messages flow from the frontend through the FastAPI backend to OpenAI and back. This focuses ONLY on the chat process.

---

## 🏗️ System Architecture (Chat Only)

```
┌─────────────────┐
│  React Frontend │
│   (User Types)  │
└────────┬────────┘
         │
         │ HTTP REST API
         │
┌────────▼────────────────────────────┐
│      FastAPI Backend                │
│                                     │
│  ┌─────────────────────────────┐  │
│  │  Chat Endpoints             │  │
│  │  POST /chatbot/session      │  │
│  │  POST /session/{id}/message │  │
│  │  DELETE /session/{id}       │  │
│  └──────────┬──────────────────┘  │
│             │                      │
│  ┌──────────▼──────────────────┐  │
│  │  Service Layer              │  │
│  │  - session_service          │  │
│  │  - openai_service           │  │
│  │  - firebase_service         │  │
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

## 📱 Frontend API Calls

### **Setup**

```javascript
// Frontend connects to backend
const API_BASE_URL = "https://chatify-chatbot.onrender.com/api/v1";
```

### **The 3 Core Chat Operations**

```javascript
// 1. Create a new chat session
createSession: async (userId, templateId) => {
  const response = await api.post("/chatbot/session", {
    user_id: userId,
    template_id: templateId,
  });
  return response.data;
};

// 2. Send a message
sendMessage: async (sessionId, message) => {
  const response = await api.post(`/chatbot/session/${sessionId}/message`, {
    message,
  });
  return response.data;
};

// 3. End the session
endSession: async (sessionId) => {
  const response = await api.delete(`/chatbot/session/${sessionId}`);
  return response.data;
};
```

---

## 🔄 Complete Chat Flow (Step-by-Step)

### **Step 1: User Creates a Chat Session**

**Frontend Action:**

```javascript
// User clicks "Start Chat" button
const response = await chatbotAPI.createSession(
  "user_12345",
  "friendly-assistant"
);
```

**What Happens in Backend:**

```
POST /api/v1/chatbot/session
Body: { user_id: "user_12345", template_id: "friendly-assistant" }

BACKEND PROCESS:
├─ 1. Generate unique session_id (UUID)
│     → "550e8400-e29b-41d4-a716-446655440000"
│
├─ 2. Load AI personality/instructions from Firebase
│     → Get system prompt for "friendly-assistant"
│     → Example: "You are a friendly, helpful assistant..."
│
├─ 3. Create session object in memory:
│     {
│       session_id: "550e8400...",
│       user_id: "user_12345",
│       template_id: "friendly-assistant",
│       system_prompt: "You are friendly...",
│       status: "active",
│       created_at: "2025-10-02T10:30:00",
│       conversation_history: []  ← Empty, no messages yet
│     }
│
├─ 4. Save to Firebase (for persistence)
│     → /userSessions/550e8400.../
│
└─ 5. Return session_id to frontend
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

### **Step 2: User Sends First Message**

**Frontend Action:**

```javascript
// User types "Hi" and clicks send
const response = await chatbotAPI.sendMessage(sessionId, "Hi");
```

**What Happens in Backend:**

```
POST /api/v1/chatbot/session/550e8400.../message
Body: { message: "Hi" }

BACKEND PROCESS:
├─ 1. Get session from memory
│     → Find session with id "550e8400..."
│     → Verify it's still active
│
├─ 2. Add user message to conversation history
│     conversation_history: [
│       { role: "user", content: "Hi", timestamp: "..." }
│     ]
│
├─ 3. Prepare request for OpenAI API
│     messages = [
│       { role: "system", content: "You are friendly..." },  ← AI instructions
│       { role: "user", content: "Hi" }                      ← User's message
│     ]
│
├─ 4. Call OpenAI ChatGPT API
│     POST https://api.openai.com/v1/chat/completions
│     {
│       model: "gpt-4o-mini",
│       messages: [...],
│       temperature: 0.9,
│       max_tokens: 50
│     }
│
├─ 5. OpenAI responds with AI message
│     AI says: "Hey! What's up?"
│
├─ 6. Add AI response to conversation history
│     conversation_history: [
│       { role: "user", content: "Hi" },
│       { role: "assistant", content: "Hey! What's up?" }
│     ]
│
├─ 7. Update session
│     - last_activity = now
│     - message_count = 1
│
├─ 8. Save updated session to Firebase
│
└─ 9. Return AI response to frontend
```

**Response to Frontend:**

```json
{
  "success": true,
  "response": "Hey! What's up?",
  "session_id": "550e8400...",
  "message_count": 1
}
```

**Frontend displays AI message in chat UI**

---

### **Step 3: User Sends Second Message**

**Frontend Action:**

```javascript
// User types "What's your name?"
const response = await chatbotAPI.sendMessage(sessionId, "What's your name?");
```

**What Happens in Backend:**

```
POST /api/v1/chatbot/session/550e8400.../message
Body: { message: "What's your name?" }

BACKEND PROCESS:
├─ 1. Get session from memory
│
├─ 2. Add user message to history
│     conversation_history: [
│       { role: "user", content: "Hi" },
│       { role: "assistant", content: "Hey! What's up?" },
│       { role: "user", content: "What's your name?" }  ← New
│     ]
│
├─ 3. Prepare OpenAI request with FULL context
│     messages = [
│       { role: "system", content: "You are friendly..." },
│       { role: "user", content: "Hi" },                    ← Previous context
│       { role: "assistant", content: "Hey! What's up?" },  ← Previous context
│       { role: "user", content: "What's your name?" }      ← New message
│     ]
│
├─ 4. Call OpenAI API (with full conversation context)
│     → OpenAI understands the conversation flow
│
├─ 5. OpenAI responds: "I'm Alex! Nice to meet you 😊"
│
├─ 6. Add to conversation history
│     conversation_history: [
│       { role: "user", content: "Hi" },
│       { role: "assistant", content: "Hey! What's up?" },
│       { role: "user", content: "What's your name?" },
│       { role: "assistant", content: "I'm Alex! Nice to meet you 😊" }
│     ]
│
├─ 7. Update session & save to Firebase
│
└─ 8. Return response to frontend
```

**Response to Frontend:**

```json
{
  "success": true,
  "response": "I'm Alex! Nice to meet you 😊",
  "session_id": "550e8400...",
  "message_count": 2
}
```

**Key Point:** Each message includes the full conversation history so the AI understands context!

---

### **Step 4: Conversation Continues...**

The process repeats for every message:

```
User sends message
  → Backend adds to history
  → Backend sends to OpenAI with full context
  → OpenAI responds
  → Backend adds response to history
  → Backend returns response to frontend
```

**Conversation History Grows:**

```
Message 1: "Hi" → "Hey! What's up?"
Message 2: "What's your name?" → "I'm Alex! Nice to meet you 😊"
Message 3: "What do you like?" → "I love chatting with people!"
Message 4: "Same here!" → "That's awesome! 😄"
...
```

---

### **Step 5: User Ends Session**

**Frontend Action:**

```javascript
// User clicks "End Chat"
await chatbotAPI.endSession(sessionId);
```

**What Happens in Backend:**

```
DELETE /api/v1/chatbot/session/550e8400...

BACKEND PROCESS:
├─ 1. Get session from memory
│
├─ 2. Mark session as "ended"
│     status: "ended"
│     ended_at: "2025-10-02T11:00:00"
│
├─ 3. Calculate stats
│     - Session duration: 30 minutes
│     - Total messages: 15
│
├─ 4. Save final state to Firebase
│
├─ 5. Remove from active sessions (memory)
│     → Free up memory
│
└─ 6. Return success
```

**Response to Frontend:**

```json
{
  "success": true,
  "message": "Session ended successfully"
}
```

---

## 🗄️ Firebase Data Structure (Chat Only)

```
firebase-database/
│
├── templates/                    # AI Personality Templates
│   └── friendly-assistant/
│       ├── name: "Friendly Assistant"
│       ├── personalityPrompt: "You are a friendly..."
│       └── model: "gpt-4o-mini"
│
└── userSessions/                 # Chat Sessions
    └── 550e8400.../              # Session ID
        ├── user_id: "user_12345"
        ├── template_id: "friendly-assistant"
        ├── status: "active" or "ended"
        ├── created_at: timestamp
        ├── last_activity: timestamp
        ├── message_count: 15
        └── conversation_history: [
            { role: "user", content: "Hi", timestamp: "..." },
            { role: "assistant", content: "Hey! What's up?", timestamp: "..." },
            ...
          ]
```

---

## 🧠 How the Backend Manages Chat Sessions

### **In-Memory Storage (Fast)**

```python
# Python dictionary for quick access
active_sessions = {
  "550e8400...": {
    session_id: "550e8400...",
    user_id: "user_12345",
    conversation_history: [...],
    system_prompt: "...",
    status: "active"
  },
  "661f9500...": {
    # Another active session
  }
}
```

**Why in-memory?**

- ⚡ Super fast access (no database query)
- 🔄 Used for every message request
- 💾 Synced to Firebase for persistence

---

### **Firebase Storage (Persistent)**

- Stores sessions permanently
- Survives server restarts
- Used for:
  - Session creation (write)
  - Message updates (write)
  - Session ending (write)
  - Loading old sessions (read)

---

### **Conversation Context Management**

**Problem:** Sending entire conversation to OpenAI can be expensive and slow

**Solution:** Limit context to last 10-20 messages

```python
# Only send recent messages to OpenAI
recent_messages = conversation_history[-10:]

messages_to_send = [
  {"role": "system", "content": system_prompt},
  ...recent_messages,  # Last 10 messages
  {"role": "user", "content": new_message}
]
```

**Why this works:**

- OpenAI doesn't need the entire 100-message history
- Recent context is usually enough
- Reduces API costs
- Faster response times

---

## 🤖 OpenAI Integration Details

### **How the Backend Talks to OpenAI**

```python
# Backend calls OpenAI API
response = openai_client.chat.completions.create(
  model="gpt-4o-mini",           # AI model to use
  messages=[                      # Conversation to send
    {"role": "system", "content": "You are friendly..."},
    {"role": "user", "content": "Hi"},
  ],
  temperature=0.9,                # Creativity level (0-2)
  max_tokens=50,                  # Max length of response
  presence_penalty=0.6,           # Reduce repetition
  frequency_penalty=0.6           # Reduce repetition
)

ai_message = response.choices[0].message.content
# "Hey! What's up?"
```

### **Key Settings Explained**

| Setting             | Value         | Why?                                               |
| ------------------- | ------------- | -------------------------------------------------- |
| `model`             | `gpt-4o-mini` | Good quality, cost-effective                       |
| `temperature`       | `0.9`         | More creative/natural responses (vs 0.1 = robotic) |
| `max_tokens`        | `50`          | Short responses (like texting, not essays)         |
| `presence_penalty`  | `0.6`         | Avoid repeating same topics                        |
| `frequency_penalty` | `0.6`         | Avoid repeating same words                         |

---

## 🔧 Session Service Implementation

### **Core Methods**

```python
class SessionService:
    active_sessions = {}  # In-memory storage

    # 1. Create Session
    async def create_session(user_id, template_id):
        session_id = generate_uuid()
        system_prompt = load_from_firebase(f"/templates/{template_id}")

        session = {
            "session_id": session_id,
            "user_id": user_id,
            "system_prompt": system_prompt,
            "conversation_history": [],
            "status": "active"
        }

        # Store in memory
        active_sessions[session_id] = session

        # Store in Firebase
        firebase.set(f"/userSessions/{session_id}", session)

        return {"success": True, "session_id": session_id}

    # 2. Send Message
    async def send_message(session_id, user_message):
        # Get session
        session = active_sessions[session_id]

        # Add user message to history
        session["conversation_history"].append({
            "role": "user",
            "content": user_message
        })

        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": session["system_prompt"]},
            *session["conversation_history"]
        ]

        # Call OpenAI
        ai_response = await openai.chat_completion(messages)

        # Add AI response to history
        session["conversation_history"].append({
            "role": "assistant",
            "content": ai_response
        })

        # Update Firebase
        firebase.set(f"/userSessions/{session_id}", session)

        return {"success": True, "response": ai_response}

    # 3. End Session
    async def end_session(session_id):
        session = active_sessions[session_id]
        session["status"] = "ended"

        # Update Firebase
        firebase.set(f"/userSessions/{session_id}", session)

        # Remove from memory
        del active_sessions[session_id]

        return {"success": True}
```

---

## 🚀 Implementing in Your Flutter Backend

### **Architecture for Flutter**

```
Flutter Backend Structure:
├── models/
│   └── session.dart           # Session data model
│
├── services/
│   ├── session_service.dart   # Manages chat sessions
│   ├── openai_service.dart    # Calls OpenAI API
│   └── firebase_service.dart  # Firebase operations
│
├── routes/
│   └── chat_routes.dart       # API endpoints
│
└── main.dart                  # Server setup
```

---

### **Flutter/Dart Implementation Example**

```dart
// Session Model
class Session {
  String sessionId;
  String userId;
  String systemPrompt;
  List<Message> conversationHistory;
  String status;

  Session({
    required this.sessionId,
    required this.userId,
    required this.systemPrompt,
    required this.conversationHistory,
    required this.status,
  });
}

// Session Service
class SessionService {
  Map<String, Session> activeSessions = {};

  // 1. Create Session
  Future<Map<String, dynamic>> createSession(String userId, String templateId) async {
    // Generate ID
    String sessionId = Uuid().v4();

    // Load personality prompt from Firebase
    String systemPrompt = await FirebaseService.getData('/templates/$templateId/personalityPrompt');

    // Create session
    Session session = Session(
      sessionId: sessionId,
      userId: userId,
      systemPrompt: systemPrompt,
      conversationHistory: [],
      status: 'active',
    );

    // Store in memory
    activeSessions[sessionId] = session;

    // Store in Firebase
    await FirebaseService.setData('/userSessions/$sessionId', session.toJson());

    return {
      'success': true,
      'session_id': sessionId,
    };
  }

  // 2. Send Message
  Future<Map<String, dynamic>> sendMessage(String sessionId, String userMessage) async {
    // Get session
    Session session = activeSessions[sessionId];

    // Add user message
    session.conversationHistory.add(Message(
      role: 'user',
      content: userMessage,
    ));

    // Prepare for OpenAI
    List<Map<String, String>> messages = [
      {'role': 'system', 'content': session.systemPrompt},
      ...session.conversationHistory.map((m) => m.toJson()),
    ];

    // Call OpenAI
    String aiResponse = await OpenAIService.chatCompletion(messages);

    // Add AI response
    session.conversationHistory.add(Message(
      role: 'assistant',
      content: aiResponse,
    ));

    // Update Firebase
    await FirebaseService.setData('/userSessions/$sessionId', session.toJson());

    return {
      'success': true,
      'response': aiResponse,
    };
  }

  // 3. End Session
  Future<void> endSession(String sessionId) async {
    Session session = activeSessions[sessionId];
    session.status = 'ended';

    // Update Firebase
    await FirebaseService.setData('/userSessions/$sessionId', session.toJson());

    // Remove from memory
    activeSessions.remove(sessionId);
  }
}
```

---

### **For Your Blabinn App (User-to-User Chat)**

Since Blabinn is user-to-user (not user-to-AI), adapt like this:

```dart
class ConnectionService {
  // Create connection between two users
  Future<Connection> createConnection(String user1Id, String user2Id) async {
    String connectionId = Uuid().v4();

    Connection connection = Connection(
      connectionId: connectionId,
      user1Id: user1Id,
      user2Id: user2Id,
      status: 'active',
      messages: [],
    );

    // Store in Firebase
    await FirebaseService.setData('/connections/$connectionId', connection.toJson());

    return connection;
  }

  // Send message between users (NO OpenAI!)
  Future<void> sendMessage(String connectionId, String senderId, String content) async {
    Message message = Message(
      messageId: Uuid().v4(),
      senderId: senderId,
      content: content,
      timestamp: DateTime.now(),
    );

    // Store message
    await FirebaseService.pushData('/connections/$connectionId/messages', message.toJson());

    // Send push notification to recipient
    String recipientId = getRecipientId(connectionId, senderId);
    await NotificationService.sendNotification(recipientId, content);
  }
}
```

---

## 🎯 Key Concepts Summary

### **1. Session = Conversation Container**

- Stores all messages between user and AI
- Has unique ID
- Tracks status (active/ended)

### **2. Conversation History = Context**

- List of all messages in order
- Sent to OpenAI with each new message
- AI uses it to understand context

### **3. System Prompt = AI Instructions**

- Tells AI how to behave
- Loaded once when session is created
- Sent to OpenAI with every message

### **4. In-Memory + Firebase = Fast + Persistent**

- In-memory: Fast access for active chats
- Firebase: Permanent storage, survives crashes

### **5. Frontend Doesn't Know About OpenAI**

- Frontend just calls backend endpoints
- Backend handles all AI communication
- Clean separation of concerns

---

## 🔄 Message Flow Diagram

```
User Types Message
    ↓
Frontend: POST /session/{id}/message
    ↓
Backend: Get session from memory
    ↓
Backend: Add user message to history
    ↓
Backend: Prepare messages array
    ↓
Backend: Call OpenAI API
    ↓
OpenAI: Process with AI model
    ↓
OpenAI: Return AI response
    ↓
Backend: Add AI response to history
    ↓
Backend: Save to Firebase
    ↓
Backend: Return response to frontend
    ↓
Frontend: Display AI message in chat UI
    ↓
User sees response
```

---

## ✅ That's It!

The entire chat process boils down to:

1. **Create Session** → Generate ID, load personality, store session
2. **Send Message** → Add to history, call OpenAI, get response, save
3. **End Session** → Mark as ended, clean up

Everything else is just optimizations (caching, cleanup, etc.) around these 3 core operations.

For your Flutter backend, implement these same 3 operations and you'll have a working chat system! 🚀
