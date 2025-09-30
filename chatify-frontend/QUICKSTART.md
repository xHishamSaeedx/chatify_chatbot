# Quick Start Guide - Chatify Frontend

Get up and running in 5 minutes! 🚀

## Step 1: Install Dependencies

```bash
cd chatify-frontend
npm install
```

## Step 2: Start the Backend

Make sure the Chatify backend is running:

```bash
cd ../app
python -m app.main
# or
uvicorn app.main:app --reload
```

Backend should be available at: `http://localhost:8000`

## Step 3: Start the Frontend

```bash
cd chatify-frontend
npm run dev
```

Frontend will open at: `http://localhost:3000`

## Step 4: Start Chatting!

1. Enter a User ID (default: `user123`)
2. Select an AI personality
3. Click "🚀 Start Chatting"
4. Start messaging!

## Troubleshooting

### Backend not connecting?

- Check if backend is running: Visit `http://localhost:8000/docs`
- Check `.env` file has correct API URL

### Port 3000 already in use?

- Vite will automatically use next available port
- Or specify a different port in `vite.config.js`:
  ```javascript
  server: {
    port: 3001,
  }
  ```

### Installation issues?

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Default Configuration

- **Frontend**: `http://localhost:3000`
- **Backend**: `http://localhost:8000`
- **API Endpoint**: `http://localhost:8000/api/v1`

That's it! You're ready to chat with AI! 💬
