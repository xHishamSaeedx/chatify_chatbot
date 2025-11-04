# 🔧 Chatbot Keep-Alive Solution

**Problem:** Chatbot service returns 503 and shuts down immediately after handling requests  
**Solution:** Multi-layered approach to keep service alive

---

## 🚨 **CURRENT STATUS**

```
✗ Chatbot: 503 (Service Unavailable)
✗ Keep-alive monitor: Shows red
✗ Health check: Fails
✗ Service status: Likely suspended/crashed
```

---

## 🎯 **ROOT CAUSE ANALYSIS**

Based on the logs and behavior:

1. **Environment Variable Validation Error** (from logs):
   ```
   ValidationError: 1 validation error for Settings
   BACKEND_CORS_ORIGINS: Extra data at position 88
   ```
   - You fixed this, but service hasn't redeployed with fix
   
2. **Service Keeps Shutting Down**:
   - Even after creating session successfully
   - Logs show: "INFO: Shutting down"
   - Not normal sleeping behavior (would wake in 30-60s)
   - Indicates startup failure or crash loop

3. **Health Check Not Responding**:
   - `/health` endpoint returns 503
   - Means service isn't fully started
   - Or Render has suspended it

---

## ✅ **SOLUTION: 4-LAYER KEEP-ALIVE STRATEGY**

### **Layer 1: Fix Environment Variables (CRITICAL)**

**Action Required in Render Dashboard:**

1. Go to https://dashboard.render.com
2. Click `chatify-chatbot` service
3. Go to **Environment** tab
4. Verify these values are **EXACTLY** as shown:

```env
BACKEND_CORS_ORIGINS=["https://blabinn-frontend.onrender.com", "https://blabbin-backend-rsss.onrender.com"]

REDIS_URL=redis://default:Aa3TAAIjcDE4MjdjYWVmYmE4ODQ0MGUxYWZhMzU1YjI4MDFiZWQzOHAxMA@stable-jackal-44499.upstash.io:6379

DEBUG=true
ENVIRONMENT=production
HOST=0.0.0.0
LOG_LEVEL=info
OPENAI_API_KEY=your_openai_api_key_here
PORT=8000
PYTHON_VERSION=3.11.0
```

**CRITICAL:**
- NO quotes around values
- NO ` -rsss` at the end
- Exact JSON format for BACKEND_CORS_ORIGINS
- Exact URL for REDIS_URL

5. Click **Save Changes**
6. Service will auto-redeploy (2-3 minutes)

---

### **Layer 2: Manual Redeploy (If Auto-Deploy Fails)**

If service still shows 503 after saving env vars:

1. In Render dashboard, click **Manual Deploy** button
2. Select **"Deploy latest commit"**
3. Wait for deployment to complete
4. **Monitor the logs** - watch for:
   ```
   ✓ Server started successfully on 0.0.0.0:8000
   ✓ Redis service initialized
   ✓ Firebase service initialized
   ```

**If you see errors:**
- Copy the error message
- We'll fix the specific issue

---

### **Layer 3: Add WebSocket Keep-Alive Endpoint**

Add persistent connection to prevent Render from shutting down:

**File: `chatify_chatbot/app/main.py`**

Add after line 146 (after health check):

```python
import asyncio
from fastapi import WebSocket, WebSocketDisconnect

@fastapi_app.websocket("/ws/keepalive")
async def keepalive_websocket(websocket: WebSocket):
    """
    WebSocket endpoint to maintain persistent connection
    Prevents Render from shutting down the service
    """
    await websocket.accept()
    print("🔌 Keep-alive WebSocket connected")
    
    try:
        while True:
            # Send ping every 30 seconds
            await websocket.send_json({
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "alive"
            })
            await asyncio.sleep(30)
            
            # Receive pong (optional)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                print(f"📥 Keep-alive pong: {data}")
            except asyncio.TimeoutError:
                pass  # No pong received, that's ok
                
    except WebSocketDisconnect:
        print("🔌 Keep-alive WebSocket disconnected")
    except Exception as e:
        print(f"❌ Keep-alive WebSocket error: {e}")
```

Add import at top:
```python
from datetime import datetime
```

**Commit and push:**
```bash
cd S:\Projects\chatify_chatbot
git add app/main.py
git commit -m "feat: Add WebSocket keep-alive endpoint to prevent service shutdown"
git push
```

---

### **Layer 4: Enhanced Keep-Alive Monitor**

Update the HTML monitor to use WebSocket:

**File: `blabin-redis/keep-alive.html`**

Add after the existing SERVICES constant (around line 330):

```javascript
// WebSocket keep-alive for chatbot
let chatbotWs = null;

function connectChatbotWebSocket() {
    try {
        chatbotWs = new WebSocket('wss://chatify-chatbot.onrender.com/ws/keepalive');
        
        chatbotWs.onopen = () => {
            addLog('🔌 Chatbot WebSocket connected (keeps service alive)', 'success');
        };
        
        chatbotWs.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'ping') {
                // Send pong back
                chatbotWs.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }));
                addLog('💓 Chatbot heartbeat (service alive)', 'success');
            }
        };
        
        chatbotWs.onerror = (error) => {
            addLog('❌ Chatbot WebSocket error (will retry)', 'error');
        };
        
        chatbotWs.onclose = () => {
            addLog('⚠️ Chatbot WebSocket closed (reconnecting in 10s)', 'warning');
            // Reconnect after 10 seconds
            setTimeout(() => {
                if (intervalId) { // Only reconnect if monitoring is active
                    connectChatbotWebSocket();
                }
            }, 10000);
        };
    } catch (error) {
        addLog(`❌ Failed to connect Chatbot WebSocket: ${error.message}`, 'error');
    }
}

// Update startKeepAlive function
function startKeepAlive() {
    if (intervalId) return;
    
    addLog('🚀 Architecture monitoring started', 'success');
    updateOverallStatus();
    
    // Connect WebSocket for persistent chatbot keep-alive
    connectChatbotWebSocket();
    
    pingAllNow();
    intervalId = setInterval(pingAllServices, PING_INTERVAL);
    countdownId = setInterval(updateCountdown, 1000);
    
    document.getElementById('startBtn').disabled = true;
    document.getElementById('stopBtn').disabled = false;
}

// Update stopKeepAlive function
function stopKeepAlive() {
    if (!intervalId) return;
    
    clearInterval(intervalId);
    clearInterval(countdownId);
    intervalId = null;
    countdownId = null;
    
    // Close WebSocket
    if (chatbotWs) {
        chatbotWs.close();
        chatbotWs = null;
    }
    
    addLog('⏸️ Architecture monitoring stopped', 'info');
    updateOverallStatus();
    
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;
    document.getElementById('nextPing').textContent = '--';
}
```

**Commit and push:**
```bash
cd S:\Projects\blabin-redis
git add keep-alive.html
git commit -m "feat: Add WebSocket keep-alive for chatbot service"
git push
```

---

## 📋 **STEP-BY-STEP EXECUTION PLAN**

### **Step 1: Fix Environment Variables (5 minutes)**

1. Open Render dashboard
2. Go to `chatify-chatbot` → Environment
3. Fix `BACKEND_CORS_ORIGINS` (remove ` -rsss` from end)
4. Fix `REDIS_URL` (remove ` -rsss` from end)
5. Save changes
6. Wait for auto-redeploy (2-3 min)

### **Step 2: Verify Deployment (2 minutes)**

Watch deployment logs for:
```
✓ Starting Chatify Chatbot on 0.0.0.0:8000
✓ Redis service initialized
✓ Firebase service initialized  
✓ Server started successfully
```

**NOT:**
```
✗ ValidationError
✗ Shutting down
✗ Failed to start
```

### **Step 3: Test Health Check (1 minute)**

```powershell
Invoke-WebRequest -Uri "https://chatify-chatbot.onrender.com/health" -TimeoutSec 30
```

**Expected:** 200 OK with `{"status":"healthy","service":"chatify_chatbot"}`  
**If 503:** Service still crashed, check logs for new errors

### **Step 4: Add WebSocket Keep-Alive (10 minutes)**

1. Add WebSocket endpoint to chatbot (code above)
2. Update keep-alive monitor (code above)
3. Commit and push both changes
4. Wait for Render to redeploy

### **Step 5: Test Complete System (5 minutes)**

1. Open updated keep-alive.html
2. Click "Start Monitoring"
3. Should see:
   - HTTP health checks every 3 minutes
   - WebSocket heartbeats every 30 seconds
   - Chatbot showing green
   - "Chatbot heartbeat (service alive)" logs

---

## 🔍 **DEBUGGING CHECKLIST**

If chatbot still shows 503 after all fixes:

### **Check 1: Render Dashboard Status**
- [ ] Go to https://dashboard.render.com
- [ ] Click `chatify-chatbot` service
- [ ] Status shows "Live" (not "Deploy Failed")
- [ ] No red error indicators

### **Check 2: Deployment Logs**
- [ ] Click "Logs" tab
- [ ] Latest deploy shows success
- [ ] No "Shutting down" messages
- [ ] See "Server started successfully"

### **Check 3: Environment Variables**
- [ ] Go to Environment tab
- [ ] `BACKEND_CORS_ORIGINS` - NO ` -rsss` at end
- [ ] `REDIS_URL` - NO ` -rsss` at end
- [ ] All other vars present

### **Check 4: Health Endpoint**
```powershell
$response = Invoke-WebRequest -Uri "https://chatify-chatbot.onrender.com/health" -UseBasicParsing
Write-Host "Status: $($response.StatusCode)"
Write-Host "Content: $($response.Content)"
```
- [ ] Returns 200 OK
- [ ] Returns JSON: `{"status":"healthy"}`

### **Check 5: Manual Test**
```powershell
# Test session creation
$body = @{
    user_id = "test-user"
    personality_id = "general-assistant"
} | ConvertTo-Json

Invoke-WebRequest `
    -Uri "https://chatify-chatbot.onrender.com/api/v1/chatbot/session" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```
- [ ] Returns 200 OK
- [ ] Returns session ID
- [ ] Service doesn't shut down after

---

## 📊 **EXPECTED RESULTS**

### **After Fixes:**

**Keep-Alive Monitor:**
```
[11:30:00] ✅ Backend Service is alive! (200 - 300ms)
[11:30:00] ✅ Redis Service is alive! (200 - 400ms)
[11:30:00] ✅ Chatbot Service is alive! (200 - 500ms)
[11:30:00] 💓 Chatbot heartbeat (service alive)
[11:30:30] 💓 Chatbot heartbeat (service alive)
[11:31:00] 💓 Chatbot heartbeat (service alive)
```

**Backend Logs:**
```json
{"level":"INFO","message":"✅ [AI_ORCHESTRATOR] AI session created for user XXX"}
{"level":"INFO","message":"✅ [AI_ORCHESTRATOR] Message sent to AI successfully"}
{"level":"INFO","message":"✅ [AI_ORCHESTRATOR] AI response received"}
```

**Chatbot Logs:**
```
[SESSION] Created session abc-123 with response limit: 20
INFO: "POST /api/v1/chatbot/session HTTP/1.1" 200 OK
INFO: "POST /api/v1/chatbot/session/abc-123/message HTTP/1.1" 200 OK
🔌 Keep-alive WebSocket connected
💓 Keep-alive heartbeat received
```

**NOT:**
```
INFO: Shutting down ❌
INFO: Application shutdown complete ❌
ValidationError ❌
503 Server Unavailable ❌
```

---

## 🎯 **SUCCESS CRITERIA**

Chatbot is considered "alive" when:

1. ✅ Health endpoint returns 200 OK consistently
2. ✅ Keep-alive monitor shows green for chatbot
3. ✅ WebSocket heartbeat every 30 seconds
4. ✅ Can create sessions without shutdown
5. ✅ Can send messages and get responses
6. ✅ Service stays up for >15 minutes
7. ✅ No "Shutting down" in logs

---

## 💡 **WHY THIS WORKS**

### **HTTP Keep-Alive (Current)**
```
Monitor → Chatbot: GET /health (every 3 min)
Chatbot: Wakes up, responds, goes back to sleep
Problem: Short-lived, Render may still suspend
```

### **WebSocket Keep-Alive (New)**
```
Monitor → Chatbot: WebSocket connection (persistent)
Chatbot: Connection stays open permanently
Heartbeat: Every 30 seconds (both directions)
Result: Render sees active connection, keeps service alive
```

### **Combined Approach**
```
✅ HTTP health checks (verify service health)
✅ WebSocket connection (maintain persistent link)
✅ Regular heartbeats (prove service is active)
= Service never sleeps, always ready!
```

---

## 🚀 **FINAL NOTES**

**Remember:**
- Fix environment variables FIRST (most critical)
- Then add WebSocket keep-alive (most effective)
- Keep monitor running in browser (24/7 if possible)
- Monitor logs to verify service stays up

**Once working:**
- Backend can communicate with chatbot anytime
- No 502/503 errors
- AI chat flows work end-to-end
- Users get AI responses immediately

---

Generated: 2025-11-04  
Status: ⚠️ **READY TO IMPLEMENT - FOLLOW STEPS ABOVE**

