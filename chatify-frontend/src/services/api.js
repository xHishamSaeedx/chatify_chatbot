import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// API Service
export const chatbotAPI = {
  // Get available personalities
  getPersonalities: async () => {
    const response = await api.get("/chatbot/personalities");
    return response.data;
  },

  // Create a new session
  createSession: async (userId, templateId) => {
    const response = await api.post("/chatbot/session", {
      user_id: userId,
      template_id: templateId,
    });
    return response.data;
  },

  // Send a message
  sendMessage: async (sessionId, message) => {
    const response = await api.post(`/chatbot/session/${sessionId}/message`, {
      message,
    });
    return response.data;
  },

  // Get session details
  getSession: async (sessionId) => {
    const response = await api.get(`/chatbot/session/${sessionId}`);
    return response.data;
  },

  // End a session
  endSession: async (sessionId) => {
    const response = await api.delete(`/chatbot/session/${sessionId}`);
    return response.data;
  },
};

export default api;
