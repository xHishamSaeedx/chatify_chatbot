import { useState } from "react";
import ChatInterface from "./components/ChatInterface";
import SessionManager from "./components/SessionManager";
import "./App.css";

function App() {
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);

  const handleSessionCreated = (sessionData) => {
    setSession(sessionData);
    setMessages([
      {
        role: "system",
        content: `Session created! You're now chatting with the AI.`,
        timestamp: new Date(),
      },
    ]);
  };

  const handleSessionEnded = () => {
    setSession(null);
    setMessages([
      {
        role: "system",
        content: "Session ended. Create a new session to continue chatting.",
        timestamp: new Date(),
      },
    ]);
  };

  const handleNewMessage = (message) => {
    setMessages((prev) => [...prev, message]);
  };

  return (
    <div className="app-container">
      <div className="chat-card">
        <div className="header">
          <h1>🤖 Chatify AI Chatbot</h1>
          {session && (
            <div className="session-info">
              <div className="info-item">
                <span className="label">Session:</span>
                <span className="value">
                  {session.session_id?.slice(0, 8)}...
                </span>
              </div>
              <div className="info-item">
                <span className="label">User:</span>
                <span className="value">{session.user_id}</span>
              </div>
              <div className="info-item">
                <span className="label">Messages:</span>
                <span className="value">
                  {messages.filter((m) => m.role !== "system").length}
                </span>
              </div>
            </div>
          )}
        </div>

        <SessionManager
          session={session}
          onSessionCreated={handleSessionCreated}
          onSessionEnded={handleSessionEnded}
        />

        <ChatInterface
          session={session}
          messages={messages}
          onNewMessage={handleNewMessage}
        />
      </div>
    </div>
  );
}

export default App;
