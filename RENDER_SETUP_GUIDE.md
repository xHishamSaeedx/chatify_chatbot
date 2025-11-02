# 🔗 Guide: Linking Projects to a New Render Account

This guide will walk you through connecting all 4 configured projects to your new Render account.

---

## 📋 Prerequisites

- ✅ GitHub account with access to these repositories
- ✅ New Render account (sign up at https://render.com if needed)
- ✅ Environment variables/secrets ready (see section below)

---

## 🚀 Step-by-Step Setup Process

### **Step 1: Create/Login to Render Account**

1. Go to **https://render.com**
2. Click **"Get Started"** or **"Sign Up"**
3. Sign up with GitHub (recommended) or email
4. Verify your email if required

---

### **Step 2: Connect GitHub Account**

1. In Render dashboard, go to **Settings** → **Connected Accounts**
2. Click **"Connect GitHub"** or **"Add GitHub"**
3. Authorize Render to access your GitHub repositories
4. Grant access to repositories (or select **"All repositories"**)

---

### **Step 3: Deploy Services (In Order)**

Deploy services in this order to handle dependencies correctly:

#### **🔴 IMPORTANT: Deploy Order**
1. **blabin-redis** (first - no dependencies)
2. **chatify-chatbot** (depends on Redis)
3. **blabin-backend** (depends on chatbot & redis)
4. **chatify-chatbot_frontend** (depends on chatbot)

---

### **Step 4: Deploy Each Service**

For each service, follow these steps:

#### **Option A: Using render.yaml (Recommended - Auto-detects)**

1. Go to **Dashboard** → **New** → **Blueprint**
2. Click **"Connect repository"**
3. Select your GitHub repository (e.g., `xHishamSaeedx/blabbin-redis`)
4. Render will **auto-detect** the `render.yaml` file
5. Click **"Apply"** or **"Create Resources"**
6. Render will create the service automatically

#### **Option B: Manual Setup (If auto-detect doesn't work)**

1. Go to **Dashboard** → **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: Use the name from `render.yaml` (e.g., `blabin-redis`)
   - **Environment**: Select from `render.yaml` (e.g., `node`, `python`)
   - **Build Command**: Copy from `render.yaml`
   - **Start Command**: Copy from `render.yaml`
   - **Health Check Path**: Copy from `render.yaml` (if present)

---

### **Step 5: Configure Environment Variables**

For each service, add environment variables from your `env.cloud.example` files:

#### **1. blabin-redis**

Go to service → **Environment** tab → Add:

```bash
NODE_ENV=production
PORT=10000
HOST=0.0.0.0
LOG_LEVEL=info
REDIS_FREE_MODE=true
BACKEND_URL=https://blabbin-backend.onrender.com  # Update after backend deploys
```

#### **2. chatify-chatbot**

Go to service → **Environment** tab → Add:

```bash
PYTHON_VERSION=3.11
ENVIRONMENT=production
HOST=0.0.0.0
LOG_LEVEL=info
PORT=8000

# Redis (Upstash Redis - use your actual URL)
REDIS_URL=redis://default:YOUR_PASSWORD@YOUR_HOST:6379

# CORS Origins (update after frontend deploys)
BACKEND_CORS_ORIGINS=["https://blabinn-frontend.onrender.com", "https://blabbin-backend.onrender.com"]

# Firebase (use your actual values)
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_CLIENT_EMAIL=your-service-account@your-project-id.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour key\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com

# OpenAI
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
```

#### **3. blabin-backend**

Go to service → **Environment** tab → Add:

```bash
NODE_ENV=production
PORT=10000
HOST=0.0.0.0
LOG_LEVEL=info

# Redis (Upstash Redis - use your actual URL)
REDIS_URL=redis://default:YOUR_PASSWORD@YOUR_HOST:6379

# Service URLs (update after other services deploy)
REDIS_SERVICE_URL=https://blabbin-redis.onrender.com
CHATBOT_SERVICE_URL=https://chatify-chatbot.onrender.com
REDIS_MICROSERVICE_URL=https://blabbin-redis.onrender.com

# CORS (update after frontend deploys)
CORS_ORIGIN=https://blabinn-frontend.onrender.com

# Firebase (use your actual values)
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_CLIENT_EMAIL=your-service-account@your-project-id.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour key\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

#### **4. chatify-chatbot_frontend**

Go to service → **Environment** tab → Add:

```bash
NODE_ENV=production
VITE_API_URL=https://chatify-chatbot.onrender.com/api/v1
```

---

### **Step 6: Update Service URLs (After Deployment)**

After all services are deployed, update environment variables with actual Render URLs:

1. **Get URLs** from each service's dashboard (format: `https://service-name.onrender.com`)
2. **Update environment variables** in dependent services:
   - Update `BACKEND_URL` in `blabin-redis` with `blabin-backend` URL
   - Update `CHATBOT_SERVICE_URL` in `blabin-backend` with `chatify-chatbot` URL
   - Update `REDIS_SERVICE_URL` in `blabin-backend` with `blabin-redis` URL
   - Update `CORS_ORIGIN` in `blabin-backend` with frontend URL
   - Update `BACKEND_CORS_ORIGINS` in `chatify-chatbot` with frontend and backend URLs

---

### **Step 7: Enable Auto-Deploy**

1. Go to each service → **Settings** → **Build & Deploy**
2. Ensure **"Auto-Deploy"** is enabled (should be `true` from `render.yaml`)
3. Select branch: **`main`** or **`master`** (whichever you use)

---

## 🔄 Quick Reference: Service Details

| Service | Repo | Type | Build Command | Start Command |
|---------|------|------|---------------|---------------|
| **blabin-redis** | `xHishamSaeedx/blabbin-redis` | Web Service (Node) | `npm install` | `node start-redis-free.js` |
| **chatify-chatbot** | `xHishamSaeedx/chatify_chatbot` | Web Service (Python) | `./render-build.sh` | `./render-start.sh` |
| **blabin-backend** | `xHishamSaeedx/blabbin-backend` | Web Service (Node) | `npm install` | `npm start` |
| **chatify-chatbot_frontend** | `xHishamSaeedx/chatify-chatbot-frontend` | Static Site | `npm install && npm run build` | N/A |

---

## ⚠️ Important Notes

### **Service URLs**
- URLs will be: `https://service-name.onrender.com`
- Free tier URLs include random suffix: `https://service-name-xxxx.onrender.com`
- Update `render.yaml` service names if you want custom URLs

### **Environment Variables**
- Use **Environment** tab in Render dashboard (not `.env` files)
- For private keys, paste the entire key including `-----BEGIN PRIVATE KEY-----`
- Render encrypts environment variables automatically

### **Dependencies**
- Services reference each other by URL
- Deploy in order: redis → chatbot → backend → frontend
- Update URLs after each service deploys

### **Free Tier Limitations**
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- Upgrade to paid tier for always-on services

---

## 🧪 Testing After Deployment

1. **Check Health Endpoints**:
   - `https://blabbin-redis.onrender.com/health`
   - `https://chatify-chatbot.onrender.com/health`
   - `https://blabbin-backend.onrender.com/health`

2. **Check Logs**:
   - Go to each service → **Logs** tab
   - Look for errors or startup messages

3. **Test Endpoints**:
   - Verify API endpoints respond correctly
   - Check inter-service communication

---

## 🆘 Troubleshooting

### **Service Won't Start**
- Check logs for error messages
- Verify environment variables are set correctly
- Ensure build/start commands match your `render.yaml`

### **Services Can't Connect**
- Verify service URLs are correct in environment variables
- Check CORS settings match your frontend URL
- Ensure all services are deployed and running

### **Build Fails**
- Check build logs for dependency errors
- Verify `package.json` or `requirements.txt` are correct
- Ensure build commands match your project structure

### **render.yaml Not Detected**
- Ensure file is named exactly `render.yaml` (lowercase)
- File must be in repository root
- Use manual setup if auto-detect fails

---

## 📞 Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
- Render Status: https://status.render.com

---

## ✅ Checklist

- [ ] Render account created
- [ ] GitHub account connected to Render
- [ ] blabin-redis deployed
- [ ] chatify-chatbot deployed
- [ ] blabin-backend deployed
- [ ] chatify-chatbot_frontend deployed
- [ ] Environment variables configured
- [ ] Service URLs updated in environment variables
- [ ] Auto-deploy enabled
- [ ] Health endpoints tested
- [ ] Services communicating correctly

---

**🎉 You're all set! Your services should now be deploying automatically on every push to your main branch.**

