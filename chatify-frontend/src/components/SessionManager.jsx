import { useState, useEffect } from "react";
import { chatbotAPI } from "../services/api";
import "./SessionManager.css";

const SessionManager = ({ session, onSessionCreated, onSessionEnded }) => {
  const [userId, setUserId] = useState("user123");
  const [personalities, setPersonalities] = useState({});
  const [selectedPersonality, setSelectedPersonality] = useState("general");
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadPersonalities();
  }, []);

  const loadPersonalities = async () => {
    try {
      const response = await chatbotAPI.getPersonalities();
      if (response.success) {
        setPersonalities(response.personalities);
        // Set first personality as default if general doesn't exist
        if (!response.personalities.general) {
          const firstKey = Object.keys(response.personalities)[0];
          setSelectedPersonality(firstKey);
        }
      }
    } catch (error) {
      console.error("Error loading personalities:", error);
      // Set default personalities if API fails
      setPersonalities({
        general: "Friendly and casual conversation",
        baddie: "Confident and sassy personality",
        "hot-bold-slutty": "Bold and flirty character",
        "party-girl": "Fun and energetic vibe",
        "career-driven": "Ambitious and focused",
      });
    }
  };

  const handleCreateSession = async () => {
    if (!userId.trim()) {
      setError("Please enter a User ID");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await chatbotAPI.createSession(
        userId,
        selectedPersonality
      );

      if (response.success) {
        onSessionCreated({
          session_id: response.session_id,
          user_id: userId,
          template_id: selectedPersonality,
        });
        setShowSuccess(true);
        setTimeout(() => setShowSuccess(false), 3000);
      } else {
        throw new Error(response.error || "Failed to create session");
      }
    } catch (error) {
      console.error("Error creating session:", error);
      setError(
        error.message ||
          "Failed to create session. Make sure the backend is running."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleEndSession = async () => {
    if (!session) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await chatbotAPI.endSession(session.session_id);

      if (response.success) {
        onSessionEnded();
      } else {
        throw new Error(response.error || "Failed to end session");
      }
    } catch (error) {
      console.error("Error ending session:", error);
      setError(error.message || "Failed to end session");
      // End session anyway in the UI
      onSessionEnded();
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefreshPersonalities = async () => {
    setIsLoading(true);
    await loadPersonalities();
    setIsLoading(false);
  };

  return (
    <div className="session-manager">
      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">⚠️</span>
          <span>{error}</span>
          <button className="alert-close" onClick={() => setError(null)}>
            ×
          </button>
        </div>
      )}

      {showSuccess && (
        <div className="alert alert-success">
          <span className="alert-icon">✓</span>
          <span>Session created successfully!</span>
        </div>
      )}

      {!session ? (
        <div className="session-form">
          <div className="form-group">
            <label htmlFor="userId">User ID</label>
            <input
              id="userId"
              type="text"
              className="form-input"
              placeholder="Enter your user ID (e.g., user123)"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="personality">AI Personality</label>
            <div className="personality-selector">
              <select
                id="personality"
                className="form-select"
                value={selectedPersonality}
                onChange={(e) => setSelectedPersonality(e.target.value)}
                disabled={isLoading}
              >
                {Object.entries(personalities).map(([id, description]) => (
                  <option key={id} value={id}>
                    {formatPersonalityName(id)} - {description}
                  </option>
                ))}
              </select>
              <button
                className="refresh-button"
                onClick={handleRefreshPersonalities}
                disabled={isLoading}
                title="Refresh personalities"
              >
                🔄
              </button>
            </div>
          </div>

          <button
            className="primary-button"
            onClick={handleCreateSession}
            disabled={isLoading || !userId.trim()}
          >
            {isLoading ? (
              <>
                <div className="button-spinner"></div>
                <span>Creating...</span>
              </>
            ) : (
              <>
                <span>🚀</span>
                <span>Start Chatting</span>
              </>
            )}
          </button>
        </div>
      ) : (
        <div className="session-active">
          <div className="session-badge">
            <span className="badge-icon">✓</span>
            <span>Session Active</span>
          </div>
          <button
            className="secondary-button"
            onClick={handleEndSession}
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="button-spinner"></div>
                <span>Ending...</span>
              </>
            ) : (
              <>
                <span>🛑</span>
                <span>End Session</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

const formatPersonalityName = (id) => {
  return id
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

export default SessionManager;
