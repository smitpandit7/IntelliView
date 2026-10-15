import axios from 'axios';

const BASE = 'http://localhost:8000';

export const startInterview = async (resumeFile, jdText, targetRole, experienceLevel) => {
  const form = new FormData();
  form.append('resume', resumeFile);
  form.append('jd_text', jdText);
  form.append('target_role', targetRole);
  form.append('experience_level', experienceLevel);

  const res = await axios.post(`${BASE}/interview/start`, form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
};

export const submitAnswer = async (sessionId, answer) => {
  const res = await axios.post(`${BASE}/interview/answer`, {
    session_id: sessionId,
    answer: answer
  });
  return res.data;
};

export const getReport = async (sessionId) => {
  const res = await axios.get(`${BASE}/interview/report/${sessionId}`);
  return res.data;
};

export const getStatus = async (sessionId) => {
  const res = await axios.get(`${BASE}/interview/status/${sessionId}`);
  return res.data;
};