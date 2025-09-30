# Chatify Frontend - React + Vite

A modern, beautiful chat interface for the Chatify AI Chatbot built with React and Vite.

## 🚀 Features

- **Modern UI/UX**: Beautiful gradient design with smooth animations
- **Real-time Chat**: Seamless messaging with AI personalities
- **Multiple Personalities**: Choose from various AI personalities
- **Session Management**: Create and manage chat sessions easily
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Auto-scroll**: Smart scrolling with scroll indicators
- **Loading States**: Clear feedback for all user actions
- **Error Handling**: User-friendly error messages

## 📋 Prerequisites

Before you begin, ensure you have:

- **Node.js** (v16 or higher)
- **npm** or **yarn**
- **Chatify Backend** running on `http://localhost:8000`

## 🛠️ Installation

1. **Navigate to the frontend directory:**

   ```bash
   cd chatify-frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

   or

   ```bash
   yarn install
   ```

3. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` if your backend runs on a different URL:

   ```
   VITE_API_URL=http://localhost:8000/api/v1
   ```

## 🎯 Running the Application

### Development Mode

Start the development server with hot-reload:

```bash
npm run dev
```

The app will open automatically at `http://localhost:3000`

### Build for Production

Create an optimized production build:

```bash
npm run build
```

### Preview Production Build

Preview the production build locally:

```bash
npm run preview
```

## 📱 Usage

1. **Start the Backend**: Make sure the Chatify backend is running at `http://localhost:8000`

2. **Open the App**: Navigate to `http://localhost:3000`

3. **Create a Session**:

   - Enter a User ID (e.g., `user123`)
   - Select an AI personality from the dropdown
   - Click "🚀 Start Chatting"

4. **Chat with AI**:

   - Type your message in the input box
   - Press Enter or click "Send"
   - View AI responses in real-time

5. **End Session**:
   - Click "🛑 End Session" when done
   - Start a new session anytime

## 🎨 Available AI Personalities

- **General** - Friendly and casual conversation
- **Baddie** - Confident and sassy personality
- **Party Girl** - Fun and energetic vibe
- **Career-Driven** - Ambitious and focused
- **Hippie** - Peaceful and spiritual
- **Content Creator** - Creative and trendy
- **Innocent** - Sweet and cute
- **Sarcastic** - Witty and savage
- **Romantic** - Dreamy and loving
- **Mysterious** - Quiet and intriguing
- And more...

## 🏗️ Project Structure

```
chatify-frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.jsx       # Main chat component
│   │   ├── ChatInterface.css
│   │   ├── SessionManager.jsx      # Session controls
│   │   └── SessionManager.css
│   ├── services/
│   │   └── api.js                  # API service layer
│   ├── App.jsx                     # Main app component
│   ├── App.css
│   ├── main.jsx                    # Entry point
│   └── index.css                   # Global styles
├── public/
├── index.html
├── vite.config.js                  # Vite configuration
├── package.json
└── README.md
```

## 🔧 Configuration

### API Proxy

The Vite dev server is configured to proxy API requests:

```javascript
// vite.config.js
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

### Environment Variables

- `VITE_API_URL`: Backend API base URL (default: `http://localhost:8000/api/v1`)

## 🎨 Customization

### Styling

All styles are in separate CSS files for easy customization:

- `src/index.css` - Global styles and gradients
- `src/App.css` - Main layout and header
- `src/components/ChatInterface.css` - Chat messages and input
- `src/components/SessionManager.css` - Session controls

### Theme Colors

Main gradient colors can be changed in CSS:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

## 🐛 Troubleshooting

### Backend Connection Issues

If you see connection errors:

1. Verify the backend is running: `http://localhost:8000/docs`
2. Check the API URL in `.env`
3. Ensure CORS is properly configured on the backend

### Port Already in Use

If port 3000 is busy, Vite will automatically use the next available port.

### Build Errors

Clear the cache and reinstall:

```bash
rm -rf node_modules dist
npm install
```

## 📦 Dependencies

### Core

- **React 18.2** - UI framework
- **Vite 5.0** - Build tool and dev server

### HTTP Client

- **Axios 1.6** - Promise-based HTTP client

### Dev Dependencies

- **@vitejs/plugin-react** - React plugin for Vite
- **ESLint** - Code linting

## 🚀 Deployment

### Netlify / Vercel

1. Build the project:

   ```bash
   npm run build
   ```

2. Deploy the `dist` folder

3. Set environment variable:
   ```
   VITE_API_URL=https://your-backend-url.com/api/v1
   ```

### Docker

Create a `Dockerfile`:

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:

```bash
docker build -t chatify-frontend .
docker run -p 80:80 chatify-frontend
```

## 📝 Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Lint code with ESLint

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the Chatify ecosystem.

## 🆘 Support

For issues and questions:

- Check the backend is running correctly
- Review browser console for errors
- Ensure all dependencies are installed
- Verify environment variables are set

---

Made with ❤️ using React + Vite
