# Deploy Backend for Public Access

## Why You Need This

Currently, your backend runs on `localhost:8000` - only accessible on your computer.

When users install your APK, they can't reach `localhost:8000` on your machine.

**You need to deploy the backend to a public server first.**

---

## Option 1: Render.com (Free Tier Available) ⭐ RECOMMENDED

### Step 1: Prepare Your Backend
Already done! You have `render.yaml` configured.

### Step 2: Deploy to Render

1. Go to https://render.com and sign up/login

2. Click "New +" → "Web Service"

3. Connect your GitHub repository (push this code to GitHub first)

4. Render will auto-detect `render.yaml`

5. Add Environment Variables:
   ```
   OPENAI_API_KEY=your-actual-key
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_DATABASE_URL=your-firebase-url
   (and other env vars from env.example)
   ```

6. Click "Create Web Service"

7. Wait for deployment (5-10 minutes)

8. **Copy your public URL**: `https://chatify-chatbot-xxxx.onrender.com`

---

## Option 2: Railway.app (Easy, Free Tier)

1. Go to https://railway.app

2. Click "Start a New Project" → "Deploy from GitHub repo"

3. Select your repository

4. Add environment variables (same as Render)

5. Get your URL: `https://your-app.railway.app`

---

## Option 3: Other Services

- **Heroku**: Easy but costs money now
- **AWS/Google Cloud**: More complex, powerful
- **DigitalOcean**: Good for production
- **Fly.io**: Fast, global deployment

---

## After Deploying Backend

### Update Flutter App

1. Open: `S:\Projects\Blabinn-Frontend\lib\core\env_config.dart`

2. Change this:
```dart
// OLD (localhost - only works on your machine)
static const String apiBaseUrlAndroid = 'http://10.0.2.2:8000';
static const String apiBaseUrlIos = 'http://localhost:8000';
static const String apiBaseUrlWeb = 'http://localhost:8000';
static const String apiBaseUrlDefault = 'http://localhost:8000';

static const String wsUrlAndroid = 'http://10.0.2.2:8000';
static const String wsUrlIos = 'http://localhost:8000';
static const String wsUrlWeb = 'http://localhost:8000';
static const String wsUrlDefault = 'http://localhost:8000';
```

3. To this (your actual deployed URL):
```dart
// NEW (your public backend URL)
static const String apiBaseUrlAndroid = 'https://your-app.railway.app';
static const String apiBaseUrlIos = 'https://your-app.railway.app';
static const String apiBaseUrlWeb = 'https://your-app.railway.app';
static const String apiBaseUrlDefault = 'https://your-app.railway.app';

static const String wsUrlAndroid = 'https://your-app.railway.app';
static const String wsUrlIos = 'https://your-app.railway.app';
static const String wsUrlWeb = 'https://your-app.railway.app';
static const String wsUrlDefault = 'https://your-app.railway.app';
```

4. Build your APK:
```bash
cd S:\Projects\Blabinn-Frontend
flutter build apk --release
```

5. Your APK is now at: `build/app/outputs/flutter-apk/app-release.apk`

---

## Testing Before Release

### Test your deployed backend:

```powershell
# Health check
Invoke-WebRequest https://your-app.railway.app/health -UseBasicParsing

# API check
Invoke-WebRequest https://your-app.railway.app/api/v1/health -UseBasicParsing
```

Should return: `{"status":"healthy"}`

---

## Important Notes

### Free Tier Limitations:

**Render.com Free Tier:**
- Spins down after 15 mins of inactivity
- First request after sleep takes ~30 seconds to wake up
- Good for testing, not ideal for production

**Railway.app Free Tier:**
- $5 free credit per month
- No sleep time
- Better for active development

### For Production (Paid):
- Upgrade to paid tier ($7-20/month)
- Add Redis for better performance
- Set up proper monitoring
- Configure autoscaling

---

## Cost Estimates

- **Free tier**: $0 (with limitations)
- **Render Basic**: $7/month
- **Railway Hobby**: $5/month usage-based
- **DigitalOcean Droplet**: $6-12/month

---

## Environment Variables You'll Need

When deploying, set these in your hosting service:

```bash
# Required
OPENAI_API_KEY=sk-proj-your-key
ENVIRONMENT=production
PORT=10000  # or whatever your host requires

# Optional (for full features)
FIREBASE_PROJECT_ID=your-project
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com

# Redis (if using)
REDIS_URL=redis://your-redis-host:6379

# CORS
BACKEND_CORS_ORIGINS=["https://your-frontend-domain.com"]
```

---

## Summary

1. ✅ Push code to GitHub
2. ✅ Deploy to Render/Railway (10 mins)
3. ✅ Add environment variables
4. ✅ Get public URL
5. ✅ Update Flutter app with URL
6. ✅ Build APK
7. ✅ Test on real device
8. ✅ Distribute APK

**Now users can use AI anywhere! 🚀**











