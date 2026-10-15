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

export const speakQuestion = async (text) => {
  try {
    // Cancel any currently playing audio first
    if (window._currentAudio) {
      window._currentAudio.pause();
      window._currentAudio = null;
    }

    const res = await axios.post(
      `${BASE}/voice/speak`,
      { text },
      { responseType: "blob" }
    );

    const audioBlob = new Blob([res.data], { type: "audio/mpeg" });
    const audioUrl  = URL.createObjectURL(audioBlob);
    const audio     = new Audio(audioUrl);
    window._currentAudio = audio;

    return new Promise((resolve, reject) => {
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        window._currentAudio = null;
        resolve();
      };
      audio.onerror = reject;
      audio.play();
    });
  } catch(err) {
    console.error("TTS failed:", err);
  }
};

export const transcribeAudio = async (audioBlob) => {
  const form = new FormData();
  form.append("audio", audioBlob, "recording.webm");
  const res = await axios.post(`${BASE}/voice/transcribe`, form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return res.data.transcript;
};