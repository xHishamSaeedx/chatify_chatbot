# Render Deployment Guide

## Quick Fix Summary

The deployment error was caused by Python 3.13 compatibility issues. I've created the following files to fix this:

1. **`.python-version`** - Locks Python to version 3.11 (stable with all dependencies)
2. **`render-build.sh`** - Build script for Render
3. **`render-start.sh`** - Start script for Render
4. **`render.yaml`** - Optional Render configuration file
5. **`env.example`** - Template for required environment variables

## Step-by-Step Deployment

### 1. Commit and Push Changes

```bash
git add .
git commit -m "Add Render deployment configuration and fix Python 3.13 compatibility"
git push origin main
```

### 2. Create a New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the `chatify_chatbot` repository

### 3. Configure Build Settings

**Option A: Using render.yaml (Automatic)**

- Render will automatically detect the `render.yaml` file
- Click "Apply" to use these settings

**Option B: Manual Configuration**

- **Name**: `chatify-chatbot` (or your preferred name)
- **Environment**: `Python 3`
- **Build Command**: `./render-build.sh`
- **Start Command**: `./render-start.sh`
- **Plan**: Choose your plan (Free tier available)

### 4. Set Environment Variables

In the Render dashboard, go to **Environment** tab and add these variables:

#### Required Variables:

```
ENVIRONMENT=production
DEBUG=False
BACKEND_CORS_ORIGINS=https://your-frontend-domain.com

# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@your-project-id.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nYour-Key-Here\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk%40your-project-id.iam.gserviceaccount.com

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Important Notes:**

- For `FIREBASE_PRIVATE_KEY`, make sure to include the full key with `\n` for newlines
- Get your Firebase credentials from the Firebase Console → Project Settings → Service Accounts
- Keep your `OPENAI_API_KEY` secure

### 5. Deploy

1. Click **"Create Web Service"**
2. Render will automatically build and deploy your app
3. Monitor the build logs for any issues
4. Once deployed, you'll get a URL like: `https://chatify-chatbot.onrender.com`

### 6. Verify Deployment

Test your endpoints:

- Health check: `https://your-app.onrender.com/health`
- API docs: `https://your-app.onrender.com/docs`
- Root: `https://your-app.onrender.com/`

## Troubleshooting

### Issue: Build still fails with Rust/Cargo errors

**Solution**: Make sure the `.python-version` file is committed and pushed to your repository.

### Issue: App starts but crashes

**Solution**: Check that all environment variables are set correctly, especially Firebase credentials.

### Issue: CORS errors when calling from frontend

**Solution**: Add your frontend URL to the `BACKEND_CORS_ORIGINS` environment variable.

### Issue: Firebase initialization fails

**Solution**:

- Verify all Firebase credentials are correct
- Make sure `FIREBASE_PRIVATE_KEY` includes `\n` characters for newlines
- Check that your Firebase service account has the correct permissions

## Alternative: Using Render Blueprint

If you prefer, you can deploy using the `render.yaml` blueprint:

1. In Render Dashboard, click **"New +"** → **"Blueprint"**
2. Connect your repository
3. Render will automatically detect `render.yaml` and configure everything
4. Just add your environment variables and deploy!

## Monitoring

After deployment:

- Monitor your app in the Render dashboard
- Check logs for any runtime errors
- Set up alerts for downtime (available in paid plans)

## Free Tier Limitations

If using Render's free tier:

- Apps spin down after 15 minutes of inactivity
- Cold starts can take 30-60 seconds
- 750 hours/month of usage
- Consider upgrading for production use

## Need Help?

- Check Render docs: https://render.com/docs
- FastAPI docs: https://fastapi.tiangolo.com/
- Firebase Admin SDK: https://firebase.google.com/docs/admin/setup
