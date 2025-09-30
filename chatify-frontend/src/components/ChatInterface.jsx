import { useState, useRef, useEffect } from "react";
import { chatbotAPI } from "../services/api";
import "./ChatInterface.css";

const ChatInterface = ({ session, messages, onNewMessage }) => {
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showScrollIndicator, setShowScrollIndicator] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const handleScroll = () => {
      if (messagesContainerRef.current) {
        const { scrollTop, scrollHeight, clientHeight } =
          messagesContainerRef.current;
        const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
        setShowScrollIndicator(!isAtBottom && messages.length > 5);
      }
    };

    const container = messagesContainerRef.current;
    if (container) {
      container.addEventListener("scroll", handleScroll);
      return () => container.removeEventListener("scroll", handleScroll);
    }
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !session || isLoading) return;

    const userMessage = {
      role: "user",
      content: inputMessage,
      timestamp: new Date(),
    };

    onNewMessage(userMessage);
    setInputMessage("");
    setIsLoading(true);

    try {
      const response = await chatbotAPI.sendMessage(
        session.session_id,
        inputMessage
      );

      if (response.success) {
        const assistantMessage = {
          role: "assistant",
          content: response.response,
          timestamp: new Date(),
        };
        onNewMessage(assistantMessage);
      } else {
        throw new Error(response.error || "Failed to send message");
      }
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        role: "system",
        content: `Error: ${error.message}`,
        timestamp: new Date(),
      };
      onNewMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="chat-interface">
      <div className="messages-container" ref={messagesContainerRef}>
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <h3>No messages yet</h3>
            <p>Create a session and start chatting with the AI!</p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.role}`}>
                <div className="message-content">{message.content}</div>
                <div className="message-time">
                  {formatTime(message.timestamp)}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {showScrollIndicator && (
        <div className="scroll-indicator" onClick={scrollToBottom}>
          <span>↓ New messages</span>
        </div>
      )}

      <div className="input-container">
        <input
          type="text"
          className="message-input"
          placeholder={
            session
              ? "Type your message..."
              : "Create a session to start chatting"
          }
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={!session || isLoading}
        />
        <button
          className="send-button"
          onClick={handleSendMessage}
          disabled={!session || !inputMessage.trim() || isLoading}
        >
          {isLoading ? (
            <div className="loading-spinner"></div>
          ) : (
            <span>Send</span>
          )}
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
