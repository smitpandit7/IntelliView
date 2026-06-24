import { useState } from "react";
import { startInterview } from "../api/interview";

const ROLES   = ["AI Engineer", "Data Scientist", "Backend Developer", "ML Engineer"];
const LEVELS  = ["Fresher", "1-3 years", "Senior"];

export default function SetupPage({ onStart }) {
  const [resume,  setResume]  = useState(null);
  const [jd,      setJd]      = useState("");
  const [role,    setRole]    = useState(ROLES[0]);
  const [level,   setLevel]   = useState(LEVELS[0]);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState("");

  const handleStart = async () => {
    if (!resume)      return setError("Please upload your resume PDF.");
    if (!jd.trim())   return setError("Please paste the job description.");
    setError("");
    setLoading(true);
    try {
      const data = await startInterview(resume, jd, role, level);
      onStart({
        sessionId:       data.session_id,
        openingMessage:  data.opening_message,
        firstQuestion:   data.question,
        questionType:    data.question_type,
        questionNumber:  data.question_number,
      });
    } catch (e) {
      setError("Failed to start interview. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-2xl">

        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16
                          bg-[#1a7a4a] rounded-2xl mb-4">
            <span className="text-3xl">🤖</span>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">
            AI Interview Simulator
          </h1>
          <p className="text-gray-400 text-lg">
            Upload your resume and job description to start a personalised interview
          </p>
        </div>

        {/* Card */}
        <div className="bg-[#16213e] rounded-2xl p-8 border border-[#ffffff15]
                        shadow-2xl space-y-6">

          {/* Resume upload */}
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Resume (PDF)
            </label>
            <label className="flex flex-col items-center justify-center w-full h-32
                               border-2 border-dashed border-[#ffffff25] rounded-xl
                               cursor-pointer hover:border-[#1a7a4a] transition-colors
                               bg-[#0f0f1a]">
              <input
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={e => setResume(e.target.files[0])}
              />
              {resume ? (
                <div className="text-center">
                  <div className="text-2xl mb-1">📄</div>
                  <p className="text-[#1a7a4a] font-medium">{resume.name}</p>
                  <p className="text-gray-500 text-xs mt-1">Click to change</p>
                </div>
              ) : (
                <div className="text-center">
                  <div className="text-2xl mb-1">⬆️</div>
                  <p className="text-gray-400">Click to upload resume PDF</p>
                  <p className="text-gray-600 text-xs mt-1">PDF files only</p>
                </div>
              )}
            </label>
          </div>

          {/* JD text */}
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Job Description
            </label>
            <textarea
              rows={5}
              placeholder="Paste the job description here..."
              className="w-full bg-[#0f0f1a] border border-[#ffffff15] rounded-xl
                         p-4 text-gray-200 text-sm placeholder-gray-600
                         focus:outline-none focus:border-[#1a7a4a] resize-none
                         transition-colors"
              value={jd}
              onChange={e => setJd(e.target.value)}
            />
          </div>

          {/* Role + Level */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Target Role
              </label>
              <select
                className="w-full bg-[#0f0f1a] border border-[#ffffff15] rounded-xl
                           p-3 text-gray-200 text-sm focus:outline-none
                           focus:border-[#1a7a4a] transition-colors"
                value={role}
                onChange={e => setRole(e.target.value)}
              >
                {ROLES.map(r => <option key={r}>{r}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Experience Level
              </label>
              <select
                className="w-full bg-[#0f0f1a] border border-[#ffffff15] rounded-xl
                           p-3 text-gray-200 text-sm focus:outline-none
                           focus:border-[#1a7a4a] transition-colors"
                value={level}
                onChange={e => setLevel(e.target.value)}
              >
                {LEVELS.map(l => <option key={l}>{l}</option>)}
              </select>
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="bg-red-900/30 border border-red-500/40 rounded-xl
                            p-3 text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Start button */}
          <button
            onClick={handleStart}
            disabled={loading}
            className="w-full bg-[#1a7a4a] hover:bg-[#156a3e] disabled:bg-gray-700
                       text-white font-bold py-4 rounded-xl text-lg
                       transition-colors duration-200 flex items-center justify-center gap-3"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white
                                rounded-full animate-spin" />
                Setting up your interview...
              </>
            ) : (
              <>🚀 Start Interview</>
            )}
          </button>
        </div>

        <p className="text-center text-gray-600 text-xs mt-6">
          Powered by LangGraph • Groq • RAG
        </p>
      </div>
    </div>
  ); 
}