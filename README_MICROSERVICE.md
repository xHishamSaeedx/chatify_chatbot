# Chatify Chatbot - Microservice Architecture

🤖 **Enhanced chatbot service** optimized for backend-to-backend communication with the modular AI orchestrator system.

## 🏗️ Microservice Optimization

The chatbot service has been enhanced with a **microservice adapter layer** that provides:

### **✅ What's New**
- **Microservice Adapter**: Enhanced interfaces for orchestrator communication
- **Performance Metrics**: Response time tracking, session statistics
- **Enhanced Logging**: Detailed microservice operation logs
- **Health Monitoring**: Comprehensive service health and dependency checks
- **Metadata Support**: Orchestrator metadata tracking through requests

### **🔄 API Endpoints**

#### **Microservice Optimized Endpoints** (New)
```
POST   /api/v1/microservice/session              # Create AI session
POST   /api/v1/microservice/session/{id}/message # Send message to AI
DELETE /api/v1/microservice/session/{id}        # End AI session
GET    /api/v1/microservice/health/detailed     # Detailed health check
GET    /api/v1/microservice/stats               # Service statistics
POST   /api/v1/microservice/cleanup             # Trigger cleanup
GET    /api/v1/microservice/version             # Service version
```

#### **Legacy Endpoints** (Still Available)
```
POST   /api/v1/chatbot/session                  # Standard session creation
POST   /api/v1/chatbot/session/{id}/message     # Standard message sending
DELETE /api/v1/chatbot/session/{id}             # Standard session end
GET    /api/v1/health                           # Basic health check
```

## 🚀 Backend Integration

The backend orchestrator should use the **microservice endpoints** for optimal performance:

### **Example: Create Session**
```javascript
// Backend Orchestrator (Node.js)
const response = await axios.post('http://localhost:8000/api/v1/microservice/session', {
  user_id: 'user_123',
  template_id: 'flirty-romantic',
  orchestrator_metadata: {
    orchestrator_id: 'blabin-backend',
    request_id: 'req_456'
  }
}, {
  headers: {
    'X-Orchestrator-Id': 'blabin-backend'
  }
});

// Enhanced Response
{
  "success": true,
  "session_id": "session_789",
  "debug_info": {
    "response_limit": 6,
    "exchange_count": 0,
    "enthusiasm": 3
  },
  "microservice": {
    "service_name": "Chatify Chatbot Microservice",
    "version": "2.0.0",
    "processing_time_ms": 45.2,
    "orchestrator_metadata": {...},
    "created_at": "2025-10-13T..."
  }
}
```

### **Example: Send Message**
```javascript
const response = await axios.post(`http://localhost:8000/api/v1/microservice/session/${sessionId}/message`, {
  message: 'hello there',
  orchestrator_metadata: {
    user_ip: '192.168.1.100',
    timestamp: Date.now()
  }
}, {
  headers: {
    'X-Orchestrator-Id': 'blabin-backend'
  }
});

// Enhanced Response
{
  "success": true,
  "response": "hey whats up",
  "debug_info": {
    "exchange_count": 1,
    "response_limit": 6,
    "enthusiasm": 4
  },
  "terminated": false,
  "on_seen": false,
  "microservice": {
    "processing_time_ms": 1250.3,
    "avg_response_time_ms": 1100.5
  }
}
```

## 📊 Enhanced Monitoring

### **Service Health Check**
```bash
curl http://localhost:8000/api/v1/microservice/health/detailed
```

Response:
```json
{
  "status": "healthy",
  "service": "Chatify Chatbot Microservice",
  "version": "2.0.0",
  "uptime_seconds": 3600,
  "uptime_formatted": "1h 0m",
  "dependencies": {
    "session_service": true,
    "openai_service": true,
    "firebase_service": true
  },
  "metrics": {
    "total_sessions_created": 42,
    "total_messages_processed": 156,
    "active_sessions": 8,
    "avg_response_time_ms": 1200.5,
    "errors_count": 2
  }
}
```

### **Service Statistics**
```bash
curl http://localhost:8000/api/v1/microservice/stats
```

Response:
```json
{
  "service": "Chatify Chatbot Microservice",
  "metrics": {
    "total_sessions_created": 42,
    "total_messages_processed": 156,
    "avg_response_time_ms": 1200.5
  },
  "session_stats": {
    "active_sessions": 8,
    "sessions_by_personality": {
      "flirty-romantic": 3,
      "energetic-fun": 2,
      "anime-kawaii": 1,
      "mysterious-dark": 2
    }
  }
}
```

## 🔧 Service Configuration

### **Environment Variables**
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...

# Firebase Configuration  
FIREBASE_PROJECT_ID=chat-app-3a529
FIREBASE_DATABASE_URL=https://chat-app-3a529-default-rtdb.firebaseio.com

# Service Configuration
PROJECT_NAME=Chatify Chatbot Microservice
VERSION=2.0.0
API_V1_STR=/api/v1
```

### **Startup Command**
```bash
cd S:\Projects\chatify_chatbot
python start_simple.py
```

Service will start on: **http://localhost:8000**

## 📋 Service Logs

### **Microservice Adapter Logs**
```
🤖 [MICROSERVICE] Chatify Chatbot Microservice v2.0.0 initialized
🚀 [MICROSERVICE] Creating session for user user_123, template: flirty-romantic
✅ [MICROSERVICE] Session created: session_789 (took 45.2ms)
💬 [MICROSERVICE] Processing message for session session_789 (length: 11)
✅ [MICROSERVICE] Message processed for session session_789 (took 1250.3ms)
🔚 [MICROSERVICE] Ending session session_789
✅ [MICROSERVICE] Session ended: session_789
🧹 [MICROSERVICE] Starting cleanup operations...
✅ [MICROSERVICE] Cleanup completed in 23.1ms
```

### **Session Service Logs** (Enhanced)
```
[SESSION] Created session session_789 with response limit: 6, enthusiasm: 3
[EXCHANGE] 🔄 Exchange 1/6 | Responses left: 5 | Session: session_789
[ENTHUSIASM] 💖 Level: 3 -> 4 | Session: session_789 | Message: 'hello there...'
[SEEN] 👁️ Session session_789: Going 'on seen' - ignored message #1
[TERMINATION] 🚪 Session session_789 terminated: Response limit (6) reached | Final enthusiasm: 4
```

## 🔄 Integration Flow

### **1. Backend → Microservice Communication**
```
Backend Orchestrator (Node.js) 
        ↓ HTTP POST
Microservice Adapter (Python)
        ↓ Internal Call  
Session Service (Python)
        ↓ HTTP API Call
OpenAI Service (Python)
        ↓ Response Chain
Backend ← Enhanced Response with Metadata
```

### **2. Enhanced Response Flow**
- **Standard Response**: AI message content
- **Debug Info**: Exchange count, enthusiasm, session limits
- **Microservice Metadata**: Processing time, service version, orchestrator info
- **Session State**: Termination status, "on seen" behavior

## 🧪 Testing Microservice Endpoints

### **1. Health Check**
```bash
curl http://localhost:8000/api/v1/microservice/health/detailed
```

### **2. Create Session**
```bash
curl -X POST http://localhost:8000/api/v1/microservice/session \
  -H "Content-Type: application/json" \
  -H "X-Orchestrator-Id: blabin-backend" \
  -d '{
    "user_id": "test_user",
    "template_id": "flirty-romantic",
    "orchestrator_metadata": {
      "test": true
    }
  }'
```

### **3. Send Message**
```bash
curl -X POST http://localhost:8000/api/v1/microservice/session/SESSION_ID/message \
  -H "Content-Type: application/json" \
  -H "X-Orchestrator-Id: blabin-backend" \
  -d '{
    "message": "hello beautiful"
  }'
```

### **4. Get Statistics**
```bash
curl http://localhost:8000/api/v1/microservice/stats
```

### **5. Trigger Cleanup**
```bash
curl -X POST http://localhost:8000/api/v1/microservice/cleanup
```

## 🔍 Key Improvements

### **Performance Tracking**
- Response time monitoring per request
- Average response time calculation
- Session creation and message processing metrics

### **Enhanced Error Handling**
- Detailed error messages with microservice context
- Error counting and tracking
- Graceful degradation for dependency failures

### **Orchestrator Integration**
- Metadata passing through request headers
- Enhanced response structure with service information
- Processing time tracking for performance optimization

### **Service Monitoring**
- Comprehensive health checks including dependencies
- Active session tracking by personality type
- Service uptime and version information

This microservice architecture provides a robust, monitored, and optimized foundation for the modular AI chatbot system while maintaining full compatibility with existing functionality.

