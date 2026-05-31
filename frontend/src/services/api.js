import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
});

export const sendMessage = async (message, history = [], options = {}) => {
  const { data } = await api.post('/chat', {
    message,
    history,
    use_rag: options.useRag ?? true,
    use_sympy: options.useSympy ?? false,
    sympy_tool: options.sympyTool || null,
    sympy_args: options.sympyArgs || {},
    stream: false,
  });
  return data;
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

export const healthCheck = async () => {
  const { data } = await api.get('/health');
  return data;
};

export default api;
