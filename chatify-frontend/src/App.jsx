import { useState } from "react";
import ChatInterface from "./components/ChatInterface";
import SessionManager from "./components/SessionManager";
import PersonalityManager from "./components/PersonalityManager";
import "./App.css";

function App() {
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [activeTab, setActiveTab] = useState("chat"); // 'chat' or 'personalities'

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
          {session && activeTab === "chat" && (
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

        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button
            className={`tab-button ${activeTab === "chat" ? "active" : ""}`}
            onClick={() => setActiveTab("chat")}
          >
            💬 Chat
          </button>
          <button
            className={`tab-button ${
              activeTab === "personalities" ? "active" : ""
            }`}
            onClick={() => setActiveTab("personalities")}
          >
            🎭 Manage Personalities
          </button>
        </div>

        {/* Conditional Content */}
        {activeTab === "chat" ? (
          <>
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
          </>
        ) : (
          <PersonalityManager />
        )}
      </div>
    </div>
  );
}

export default App;
