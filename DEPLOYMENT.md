# Chatify Chatbot - Deployment Guide

## 🚀 Production Deployment

### Prerequisites

- Python 3.9+
- Firebase project with Realtime Database
- OpenAI API key
- Render account (or similar hosting)

---

## 📋 Step-by-Step Deployment

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file (or set in Render dashboard):

```bash
# Application Settings
PROJECT_NAME=Chatify Chatbot
VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# API Configuration
API_V1_STR=/api/v1

# CORS - Add your Node.js backend URL
BACKEND_CORS_ORIGINS=http://node-backend:8000,https://your-backend.com

# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_DATABASE_URL=https://your-project-id-default-rtdb.firebaseio.com
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_CLIENT_EMAIL=your-service-account@your-project-id.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour-Private-Key-Here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3. Run the Application

**Development:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

---

## 🔧 Render Deployment

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables

Set all the variables from the `.env` file in Render dashboard.

---

## 🤖 Background Jobs

The application automatically runs these background jobs:

### Session Cleanup (Every 10 minutes)

- Cleans up expired sessions from memory
- Removes old sessions from Firebase
- Deletes conversation history for ended sessions

**What it does:**

- Sessions older than 30 minutes → Removed from memory
- Ended sessions older than 1 hour → Removed from Firebase
- Frees up memory and database space

**Monitoring:**
Check logs for cleanup activity:

```
✅ Cleaned 5 expired sessions from Firebase
🗑️ Cleaned expired Firebase session: abc123
```

---

## 📊 Health Monitoring

### Health Check Endpoint

```bash
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "service": "Chatify Chatbot"
}
```

### Detailed Stats

```bash
GET /api/v1/chatbot/stats
```

**Response:**

```json
{
  "success": true,
  "stats": {
    "active_sessions": 42,
    "session_timeout_minutes": 30,
    "sessions": ["session-id-1", "session-id-2"]
  }
}
```

---

## 🔥 Firebase Setup

### 1. Create Collections/Paths

The application automatically uses these Firebase paths:

```
/templates/                    # AI personality templates
  /{templateId}/
    - name
    - personalityPrompt
    - welcomeMessage
    - model
    - temperature
    - maxTokens

/userSessions/                 # Active chatbot sessions
  /{sessionId}/
    - user_id
    - template_id
    - status
    - conversation_history
    - created_at

/conversations/                # Message history
  /{sessionId}/
    /messages/
      - role
      - content
      - timestamp

/settings/                     # Global settings
  /universalRules/
    - rules
    - enabled
    - version
```

### 2. Populate Templates

Use the provided script to populate default templates:

```bash
node app/populate-templates.js
```

---

## 🧪 Testing

### Test Session Creation

```bash
curl -X POST http://localhost:8000/api/v1/chatbot/session \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user-123", "template_id": "general"}'
```

### Test Message Sending

```bash
curl -X POST http://localhost:8000/api/v1/chatbot/session/{session_id}/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### Test Cleanup

```bash
curl -X POST http://localhost:8000/api/v1/chatbot/cleanup
```

---

## 📝 Logs

### What to Monitor

**Session Creation:**

```
✅ Session created successfully for user: user123
```

**Message Processing:**

```
📝 System prompt added to OpenAI messages (length: 450 chars)
💬 Conversation history: 5 messages
⏱️ Typing delay: 2.5s
```

**Cleanup Activity:**

```
✅ Background cleanup job started - runs every 10 minutes
🗑️ Cleaned expired Firebase session: abc123
✅ Cleaned 3 expired sessions from Firebase
```

**Errors to Watch:**

```
⚠️ Firebase not available, storing in memory only
❌ OpenAI API error: insufficient_quota
🔍 No system prompt provided - using default OpenAI behavior
```

---

## 🚨 Troubleshooting

### Issue: Sessions not cleaning up

**Check:** Background job is running

```bash
# Look for this in logs:
✅ Background cleanup job started - runs every 10 minutes
```

**Solution:** Restart the server

---

### Issue: OpenAI API errors

**Error:** `insufficient_quota` or `429` errors

**Solutions:**

1. Check OpenAI account has credits
2. Verify API key is correct
3. Check rate limits in OpenAI dashboard

---

### Issue: Firebase connection failed

**Error:** `Firebase not available`

**Solutions:**

1. Verify all Firebase env vars are set
2. Check private key formatting (include `\n` for newlines)
3. Ensure service account has correct permissions

---

## 💰 Cost Monitoring

### OpenAI Usage

- Model: `gpt-4o-mini` (~$0.15 per 1M input tokens)
- Average conversation: ~500 tokens ($0.000075)
- 1000 messages/day: ~$2.25/month

### Firebase Usage

- Free tier: 100K reads/day, 20K writes/day
- Typical usage: ~1000 operations/day (well within free tier)

### Render Hosting

- Starter plan: $7/month
- Pro plan: $25/month (recommended for production)

**Total estimated cost for 1000 active users:**

- OpenAI: $50-100/month
- Firebase: $0-10/month (within free tier)
- Hosting: $25/month
- **Total: ~$75-135/month**

---

## ✅ Production Checklist

Before going live:

- [ ] All environment variables set
- [ ] Firebase project configured
- [ ] OpenAI API key has credits
- [ ] CORS origins configured for your backend
- [ ] Health check endpoint responding
- [ ] Background cleanup job running
- [ ] Test session creation works
- [ ] Test message sending works
- [ ] Monitor logs for errors
- [ ] Set up cost alerts (OpenAI dashboard)

---

## 🔄 Updates & Maintenance

### Updating the Application

```bash
git pull
pip install -r requirements.txt
# Restart service
```

### Database Maintenance

- Cleanup runs automatically every 10 minutes
- Manual cleanup: `POST /api/v1/chatbot/cleanup`
- Sessions expire after 30 minutes of inactivity

### Monitoring

- Check health endpoint regularly
- Monitor OpenAI token usage
- Watch Firebase quota
- Track active session count

---

## 📞 Support

For issues or questions:

1. Check logs first
2. Verify environment variables
3. Test with simple curl commands
4. Check Firebase/OpenAI service status

---

## 🎯 Next Steps

After successful deployment:

1. Integrate with Node.js backend
2. Add rate limiting (optional)
3. Set up monitoring alerts
4. Implement analytics tracking
5. Add more personality templates
