import { useState, useEffect } from "react";
import { personalityAPI } from "../services/api";
import "./PersonalityManager.css";

function PersonalityManager() {
  const [personalities, setPersonalities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    title: "",
    description: "",
    category: "general",
    personalityPrompt: "",
    welcomeMessage: "Hello! How can I help you?",
    model: "gpt-4o-mini",
    temperature: 0.9,
    maxTokens: 150,
    tags: [],
    isPublic: true,
    isDefault: false,
  });

  useEffect(() => {
    loadPersonalities();
  }, []);

  const loadPersonalities = async () => {
    try {
      setLoading(true);
      const data = await personalityAPI.getAllPersonalities();
      setPersonalities(data);
      setError(null);
    } catch (err) {
      setError("Failed to load personalities: " + err.message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleTagsChange = (e) => {
    const tags = e.target.value.split(",").map((tag) => tag.trim());
    setFormData((prev) => ({ ...prev, tags }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await personalityAPI.updatePersonality(editingId, formData);
      } else {
        await personalityAPI.createPersonality(formData);
      }
      await loadPersonalities();
      resetForm();
      setError(null);
    } catch (err) {
      setError(
        `Failed to ${editingId ? "update" : "create"} personality: ${
          err.response?.data?.detail || err.message
        }`
      );
      console.error(err);
    }
  };

  const handleEdit = (personality) => {
    setFormData({
      name: personality.name,
      title: personality.title,
      description: personality.description,
      category: personality.category || "general",
      personalityPrompt: personality.personalityPrompt || "",
      welcomeMessage: personality.welcomeMessage,
      model: personality.model || "gpt-4o-mini",
      temperature: personality.temperature || 0.9,
      maxTokens: personality.maxTokens || 150,
      tags: personality.tags || [],
      isPublic: personality.isPublic !== false,
      isDefault: personality.isDefault || false,
    });
    setEditingId(personality.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this personality?")) {
      return;
    }
    try {
      await personalityAPI.deletePersonality(id);
      await loadPersonalities();
      setError(null);
    } catch (err) {
      setError(
        `Failed to delete personality: ${
          err.response?.data?.detail || err.message
        }`
      );
      console.error(err);
    }
  };

  const resetForm = () => {
    setFormData({
      name: "",
      title: "",
      description: "",
      category: "general",
      personalityPrompt: "",
      welcomeMessage: "Hello! How can I help you?",
      model: "gpt-4o-mini",
      temperature: 0.9,
      maxTokens: 150,
      tags: [],
      isPublic: true,
      isDefault: false,
    });
    setEditingId(null);
    setShowForm(false);
  };

  if (loading) {
    return <div className="personality-manager loading">Loading...</div>;
  }

  return (
    <div className="personality-manager">
      <div className="manager-header">
        <h2>🎭 AI Personality Management</h2>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "+ New Personality"}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {showForm && (
        <div className="personality-form">
          <h3>{editingId ? "Edit Personality" : "Create New Personality"}</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="name">
                  Name (ID) <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., friendly-assistant"
                  required
                  disabled={editingId !== null}
                />
                <small>Unique identifier (lowercase, use dashes)</small>
              </div>

              <div className="form-group">
                <label htmlFor="title">
                  Title <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  placeholder="e.g., Friendly Assistant"
                  required
                />
              </div>

              <div className="form-group full-width">
                <label htmlFor="description">
                  Description <span className="required">*</span>
                </label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Describe this personality..."
                  required
                  rows="2"
                />
              </div>

              <div className="form-group full-width">
                <label htmlFor="personalityPrompt">
                  Personality Description <span className="required">*</span>
                </label>
                <textarea
                  id="personalityPrompt"
                  name="personalityPrompt"
                  value={formData.personalityPrompt}
                  onChange={handleInputChange}
                  placeholder="Describe the unique personality traits and behavior... (Universal rules are applied automatically)"
                  required
                  rows="6"
                />
                <small>
                  Describe this personality&apos;s unique traits. Universal
                  rules apply to all personalities automatically.
                </small>
              </div>

              <div className="form-group">
                <label htmlFor="welcomeMessage">Welcome Message</label>
                <input
                  type="text"
                  id="welcomeMessage"
                  name="welcomeMessage"
                  value={formData.welcomeMessage}
                  onChange={handleInputChange}
                  placeholder="Hello! How can I help you?"
                />
              </div>

              <div className="form-group">
                <label htmlFor="category">Category</label>
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                >
                  <option value="general">General</option>
                  <option value="dating">Dating</option>
                  <option value="support">Support</option>
                  <option value="creative">Creative</option>
                  <option value="professional">Professional</option>
                  <option value="entertainment">Entertainment</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="model">AI Model</label>
                <select
                  id="model"
                  name="model"
                  value={formData.model}
                  onChange={handleInputChange}
                >
                  <option value="gpt-4o-mini">GPT-4o Mini</option>
                  <option value="gpt-4o">GPT-4o</option>
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="temperature">
                  Temperature: {formData.temperature}
                </label>
                <input
                  type="range"
                  id="temperature"
                  name="temperature"
                  min="0"
                  max="2"
                  step="0.1"
                  value={formData.temperature}
                  onChange={handleInputChange}
                />
                <small>0 = Focused, 2 = Creative</small>
              </div>

              <div className="form-group">
                <label htmlFor="maxTokens">Max Tokens</label>
                <input
                  type="number"
                  id="maxTokens"
                  name="maxTokens"
                  min="10"
                  max="4000"
                  value={formData.maxTokens}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group full-width">
                <label htmlFor="tags">Tags</label>
                <input
                  type="text"
                  id="tags"
                  name="tags"
                  value={formData.tags.join(", ")}
                  onChange={handleTagsChange}
                  placeholder="friendly, casual, helpful (comma-separated)"
                />
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="isPublic"
                    checked={formData.isPublic}
                    onChange={handleInputChange}
                  />{" "}
                  Public (visible to all users)
                </label>
              </div>

              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="isDefault"
                    checked={formData.isDefault}
                    onChange={handleInputChange}
                  />{" "}
                  Default (cannot be deleted)
                </label>
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-primary">
                {editingId ? "Update Personality" : "Create Personality"}
              </button>
              <button
                type="button"
                className="btn-secondary"
                onClick={resetForm}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="personalities-list">
        <h3>Existing Personalities ({personalities.length})</h3>
        {personalities.length === 0 ? (
          <div className="empty-state">
            No personalities found. Create your first one!
          </div>
        ) : (
          <div className="personalities-grid">
            {personalities.map((personality) => (
              <div key={personality.id} className="personality-card">
                <div className="card-header">
                  <h4>{personality.title}</h4>
                  {personality.isDefault && (
                    <span className="badge badge-default">Default</span>
                  )}
                  {!personality.isPublic && (
                    <span className="badge badge-private">Private</span>
                  )}
                </div>
                <p className="card-description">{personality.description}</p>
                <div className="card-meta">
                  <span className="meta-item">
                    <strong>ID:</strong> {personality.id}
                  </span>
                  <span className="meta-item">
                    <strong>Category:</strong> {personality.category}
                  </span>
                  <span className="meta-item">
                    <strong>Model:</strong> {personality.model}
                  </span>
                  <span className="meta-item">
                    <strong>Temperature:</strong> {personality.temperature}
                  </span>
                </div>
                {personality.tags && personality.tags.length > 0 && (
                  <div className="card-tags">
                    {personality.tags.map((tag) => (
                      <span key={`${personality.id}-${tag}`} className="tag">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
                <div className="card-actions">
                  <button
                    className="btn-edit"
                    onClick={() => handleEdit(personality)}
                  >
                    Edit
                  </button>
                  <button
                    className="btn-delete"
                    onClick={() => handleDelete(personality.id)}
                    disabled={personality.isDefault}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default PersonalityManager;
