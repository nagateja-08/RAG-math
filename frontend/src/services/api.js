import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 1. Core Combined Graph-Enhanced RAG Ask Endpoint
export const askQuestion = async (question, history = [], userId = 'default_student') => {
  const response = await client.post('/ask', {
    question,
    history,
    user_id: userId,
    use_vector_search: true,
    use_graph_retrieval: true,
    use_sympy_verification: true,
  });
  return response.data;
};

// 2. Chat endpoint (standard / backward compatible)
export const sendMessage = async (message, history = []) => {
  const response = await client.post('/chat', {
    message,
    history,
  });
  return response.data;
};

// 3. Knowledge Graph
export const fetchGraph = async (subject = null) => {
  const params = subject && subject !== 'All' ? { subject } : {};
  const response = await client.get('/graph', { params });
  return response.data;
};

export const fetchConceptDetails = async (concept) => {
  const response = await client.get(`/graph/${encodeURIComponent(concept)}`);
  return response.data;
};

export const fetchTopics = async () => {
  const response = await client.get('/topics');
  return response.data;
};

// 4. Prerequisites
export const fetchPrerequisites = async (concept) => {
  const response = await client.get(`/prerequisites/${encodeURIComponent(concept)}`);
  return response.data;
};

// 5. SymPy Formula Verification
export const verifyExpression = async (payload) => {
  const response = await client.post('/verify', payload);
  return response.data;
};

// 6. Diagnostic Assessment
export const fetchAssessment = async (concept) => {
  const response = await client.get(`/assessment/${encodeURIComponent(concept)}`);
  return response.data;
};

export const submitAssessment = async (targetConcept, answers, userId = 'default_student') => {
  const response = await client.post('/assessment', {
    user_id: userId,
    target_concept: targetConcept,
    answers,
  });
  return response.data;
};

// 7. Learning Progress Analytics
export const fetchProgress = async (userId = 'default_student') => {
  const response = await client.get('/progress', {
    params: { user_id: userId },
  });
  return response.data;
};

// 8. Document Ingestion
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await client.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

// 9. Health Check
export const healthCheck = async () => {
  const response = await client.get('/health');
  return response.data;
};
