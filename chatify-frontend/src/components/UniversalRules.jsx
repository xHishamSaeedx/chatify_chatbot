import { useState, useEffect } from "react";
import { settingsAPI } from "../services/api";
import "./UniversalRules.css";

function UniversalRules() {
  const [rules, setRules] = useState("");
  const [version, setVersion] = useState("1.0");
  const [enabled, setEnabled] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    try {
      setLoading(true);
      const data = await settingsAPI.getUniversalRules();
      setRules(data.rules || "");
      setVersion(data.version || "1.0");
      setEnabled(data.enabled !== false);
      setError(null);
    } catch (err) {
      setError("Failed to load universal rules: " + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setError(null);
      setSuccess(null);
      await settingsAPI.updateUniversalRules({
        rules,
        version,
        enabled,
      });
      setSuccess("Universal rules updated successfully!");
      setIsEditing(false);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(
        `Failed to update universal rules: ${
          err.response?.data?.detail || err.message
        }`
      );
      console.error(err);
    }
  };

  const handleCancel = () => {
    loadRules();
    setIsEditing(false);
    setError(null);
    setSuccess(null);
  };

  if (loading) {
    return <div className="universal-rules loading">Loading...</div>;
  }

  return (
    <div className="universal-rules">
      <div className="rules-header">
        <div>
          <h2>📋 Universal Rules</h2>
          <p className="rules-subtitle">
            These rules apply to ALL AI personalities automatically
          </p>
        </div>
        {!isEditing && (
          <button className="btn-primary" onClick={() => setIsEditing(true)}>
            ✏️ Edit Rules
          </button>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="rules-content">
        <div className="rules-info">
          <div className="info-badge">
            <span className="badge-label">Version:</span>
            {isEditing ? (
              <input
                type="text"
                value={version}
                onChange={(e) => setVersion(e.target.value)}
                className="version-input"
                placeholder="e.g., 1.0"
              />
            ) : (
              <span className="badge-value">{version}</span>
            )}
          </div>
          <div className="info-badge">
            <span className="badge-label">Status:</span>
            {isEditing ? (
              <label
                className="toggle-switch"
                aria-label="Toggle universal rules"
              >
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={(e) => setEnabled(e.target.checked)}
                  aria-label="Enable or disable universal rules"
                />
                <span className="slider"></span>
              </label>
            ) : (
              <span
                className={`badge-value ${enabled ? "enabled" : "disabled"}`}
              >
                {enabled ? "Enabled" : "Disabled"}
              </span>
            )}
          </div>
        </div>

        <div className="rules-editor">
          {isEditing ? (
            <>
              <textarea
                value={rules}
                onChange={(e) => setRules(e.target.value)}
                placeholder="Enter universal rules that apply to all personalities..."
                rows="15"
                className="rules-textarea"
              />
              <div className="editor-actions">
                <button className="btn-save" onClick={handleSave}>
                  💾 Save Rules
                </button>
                <button className="btn-cancel" onClick={handleCancel}>
                  Cancel
                </button>
              </div>
            </>
          ) : (
            <div className="rules-display">
              <pre>{rules || "No universal rules defined yet."}</pre>
            </div>
          )}
        </div>

        <div className="rules-explanation">
          <h3>💡 How Universal Rules Work</h3>
          <ul>
            <li>
              <strong>Automatically Applied:</strong> These rules are
              automatically prepended to every personality&apos;s description
            </li>
            <li>
              <strong>Global Changes:</strong> Update rules here once, and they
              apply to all personalities instantly
            </li>
            <li>
              <strong>Personality-Specific:</strong> Each personality still has
              its own unique description
            </li>
            <li>
              <strong>Combined Prompt:</strong> Final prompt = Universal Rules +
              Personality Description
            </li>
            <li>
              <strong>Toggle Control:</strong> Disable to use only
              personality-specific descriptions
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default UniversalRules;
