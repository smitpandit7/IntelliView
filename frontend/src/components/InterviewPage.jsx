import { useState, useEffect, useRef } from "react";
import { submitAnswer, getReport }     from "../api/interview";

export default function InterviewPage({ session, onComplete }) {
  const [question,   setQuestion]   = useState(session.firstQuestion);
  const [qType,      setQType]      = useState(session.questionType);
  const [qNum,       setQNum]       = useState(session.questionNumber);
  const [answer,     setAnswer]     = useState("");
  const [loading,    setLoading]    = useState(false);
  const [lastScore,  setLastScore]  = useState(null);
  const [lastFb,     setLastFb]     = useState("");
  const [scores,     setScores]     = useState([]);
  const [history,    setHistory]    = useState([]);
  const [camReady,   setCamReady]   = useState(false);
  const videoRef   = useRef(null);
  const chatEndRef = useRef(null);

  // Start webcam
  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setCamReady(true);
        }
      })
      .catch(() => setCamReady(false));

    return () => {
      if (videoRef.current?.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(t => t.stop());
      }
    };
  }, []);

  // Auto scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, question]);

  const handleSubmit = async () => {
    if (!answer.trim() || loading) return;

    const userAnswer = answer.trim();
    setAnswer("");
    setLoading(true);

    // Add to chat history
    setHistory(h => [
      ...h,
      { role: "agent",     content: question,   type: qType },
      { role: "candidate", content: userAnswer              },
    ]);

    try {
      const data = await submitAnswer(session.sessionId, userAnswer);

      setLastScore(data.last_score);
      setLastFb(data.last_feedback);
      setScores(s => [...s, data.last_score]);

      if (data.is_complete) {
        // Get report then go to report page
        const report = await getReport(session.sessionId);
        onComplete({ ...report, scores: [...scores, data.last_score] });
      } else {
        setQuestion(data.question);
        setQType(data.question_type);
        setQNum(data.question_number);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const avg = scores.length
    ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)
    : null;

  const scoreColor = (s) =>
    s >= 7 ? "text-green-400" : s >= 5 ? "text-yellow-400" : "text-red-400";

  return (
    <div className="min-h-screen flex flex-col bg-[#0f0f1a]">

      {/* Top bar */}
      <div className="flex items-center justify-between px-6 py-3
                      bg-[#16213e] border-b border-[#ffffff10]">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🤖</span>
          <div>
            <p className="text-white font-bold text-sm">AI Interview Simulator</p>
            <p className="text-gray-500 text-xs">{session.openingMessage}</p>
          </div>
        </div>
        <div className="flex items-center gap-6">
          <div className="text-center">
            <p className="text-gray-500 text-xs">Question</p>
            <p className="text-white font-bold">{qNum}</p>
          </div>
          {avg && (
            <div className="text-center">
              <p className="text-gray-500 text-xs">Avg Score</p>
              <p className={`font-bold ${scoreColor(parseFloat(avg))}`}>{avg}/10</p>
            </div>
          )}
          <div className={`px-3 py-1 rounded-full text-xs font-bold
            ${qType === "technical"
              ? "bg-blue-900/40 text-blue-400 border border-blue-500/30"
              : "bg-purple-900/40 text-purple-400 border border-purple-500/30"
            }`}>
            {qType?.toUpperCase()}
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">

        {/* LEFT — Chat / Interview */}
        <div className="flex-1 flex flex-col">

          {/* Chat history */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">

            {/* Opening message */}
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-[#1a7a4a] flex items-center
                              justify-center text-sm flex-shrink-0">🤖</div>
              <div className="bg-[#16213e] rounded-2xl rounded-tl-none p-4
                              max-w-lg border border-[#ffffff10]">
                <p className="text-gray-200 text-sm">{session.openingMessage}</p>
              </div>
            </div>

            {/* Chat messages */}
            {history.map((msg, i) => (
              <div key={i}
                className={`flex gap-3 ${msg.role === "candidate" ? "flex-row-reverse" : ""}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center
                                 text-sm flex-shrink-0
                  ${msg.role === "agent"
                    ? "bg-[#1a7a4a]"
                    : "bg-[#2e6da4]"
                  }`}>
                  {msg.role === "agent" ? "🤖" : "👤"}
                </div>
                <div className={`rounded-2xl p-4 max-w-lg text-sm
                  ${msg.role === "agent"
                    ? "bg-[#16213e] rounded-tl-none border border-[#ffffff10] text-gray-200"
                    : "bg-[#2e6da4]/30 rounded-tr-none border border-[#2e6da4]/30 text-gray-100"
                  }`}>
                  {msg.type && (
                    <span className={`text-xs font-bold mr-2
                      ${msg.type === "technical" ? "text-blue-400" : "text-purple-400"}`}>
                      [{msg.type.toUpperCase()}]
                    </span>
                  )}
                  {msg.content}
                </div>
              </div>
            ))}

            {/* Current question */}
            {!loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-[#1a7a4a] flex items-center
                                justify-center text-sm flex-shrink-0">🤖</div>
                <div className="bg-[#16213e] rounded-2xl rounded-tl-none p-4
                                max-w-lg border border-[#1a7a4a]/40
                                shadow-lg shadow-[#1a7a4a]/10">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full
                      ${qType === "technical"
                        ? "bg-blue-900/40 text-blue-400"
                        : "bg-purple-900/40 text-purple-400"
                      }`}>
                      Q{qNum} • {qType?.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-gray-100 text-sm leading-relaxed">{question}</p>
                </div>
              </div>
            )}

            {/* Loading indicator */}
            {loading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-[#1a7a4a] flex items-center
                                justify-center text-sm flex-shrink-0">🤖</div>
                <div className="bg-[#16213e] rounded-2xl rounded-tl-none p-4
                                border border-[#ffffff10]">
                  <div className="flex gap-1 items-center">
                    <div className="w-2 h-2 bg-[#1a7a4a] rounded-full animate-bounce"
                         style={{animationDelay:"0ms"}}/>
                    <div className="w-2 h-2 bg-[#1a7a4a] rounded-full animate-bounce"
                         style={{animationDelay:"150ms"}}/>
                    <div className="w-2 h-2 bg-[#1a7a4a] rounded-full animate-bounce"
                         style={{animationDelay:"300ms"}}/>
                    <span className="text-gray-500 text-xs ml-2">Evaluating...</span>
                  </div>
                </div>
              </div>
            )}

            {/* Score badge after each answer */}
            {lastScore !== null && !loading && (
              <div className={`flex items-center gap-3 p-3 rounded-xl border mx-12
                ${lastScore >= 7
                  ? "bg-green-900/20 border-green-500/30"
                  : lastScore >= 5
                  ? "bg-yellow-900/20 border-yellow-500/30"
                  : "bg-red-900/20 border-red-500/30"
                }`}>
                <span className={`text-2xl font-bold ${scoreColor(lastScore)}`}>
                  {lastScore}/10
                </span>
                <p className="text-gray-400 text-xs">{lastFb}</p>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Answer input */}
          <div className="p-4 bg-[#16213e] border-t border-[#ffffff10]">
            <div className="flex gap-3">
              <textarea
                rows={3}
                placeholder="Type your answer here... (Press Ctrl+Enter to submit)"
                className="flex-1 bg-[#0f0f1a] border border-[#ffffff15]
                           rounded-xl p-4 text-gray-200 text-sm
                           placeholder-gray-600 focus:outline-none
                           focus:border-[#1a7a4a] resize-none transition-colors"
                value={answer}
                onChange={e => setAnswer(e.target.value)}
                onKeyDown={e => {
                  if (e.key === "Enter" && e.ctrlKey) handleSubmit();
                }}
                disabled={loading}
              />
              <button
                onClick={handleSubmit}
                disabled={loading || !answer.trim()}
                className="px-6 bg-[#1a7a4a] hover:bg-[#156a3e]
                           disabled:bg-gray-700 disabled:cursor-not-allowed
                           text-white font-bold rounded-xl transition-colors
                           flex flex-col items-center justify-center gap-1"
              >
                <span className="text-lg">📤</span>
                <span className="text-xs">Send</span>
              </button>
            </div>
            <p className="text-gray-600 text-xs mt-2 text-center">
              Ctrl+Enter to submit
            </p>
          </div>
        </div>

        {/* RIGHT — Webcam */}
        <div className="w-72 bg-[#16213e] border-l border-[#ffffff10]
                        flex flex-col p-4 gap-4">

          {/* Webcam feed */}
          <div>
            <p className="text-gray-500 text-xs font-semibold mb-2 uppercase tracking-wider">
              Your Camera
            </p>
            <div className="relative rounded-xl overflow-hidden bg-[#0f0f1a]
                            border border-[#ffffff10] aspect-video">
              <video
                ref={videoRef}
                autoPlay
                muted
                className="w-full h-full object-cover"
              />
              {!camReady && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-3xl mb-2">📷</div>
                    <p className="text-gray-600 text-xs">Camera not available</p>
                  </div>
                </div>
              )}
              {/* Recording indicator */}
              {camReady && (
                <div className="absolute top-2 right-2 flex items-center gap-1
                                bg-black/60 rounded-full px-2 py-1">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"/>
                  <span className="text-white text-xs">LIVE</span>
                </div>
              )}
            </div>
          </div>

          {/* Score history */}
          <div>
            <p className="text-gray-500 text-xs font-semibold mb-2 uppercase tracking-wider">
              Score History
            </p>
            <div className="space-y-2">
              {scores.length === 0 && (
                <p className="text-gray-600 text-xs">Scores appear after each answer</p>
              )}
              {scores.map((s, i) => (
                <div key={i} className="flex items-center gap-2">
                  <span className="text-gray-500 text-xs w-6">Q{i+1}</span>
                  <div className="flex-1 bg-[#0f0f1a] rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full transition-all duration-500
                        ${s >= 7 ? "bg-green-500" : s >= 5 ? "bg-yellow-500" : "bg-red-500"}`}
                      style={{ width: `${s * 10}%` }}
                    />
                  </div>
                  <span className={`text-xs font-bold w-8 ${scoreColor(s)}`}>
                    {s}/10
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Tips */}
          <div className="mt-auto">
            <div className="bg-[#0f0f1a] rounded-xl p-3 border border-[#ffffff08]">
              <p className="text-gray-500 text-xs font-semibold mb-2">💡 Tips</p>
              <ul className="text-gray-600 text-xs space-y-1">
                <li>• Be specific with examples</li>
                <li>• Mention actual tools used</li>
                <li>• Explain your reasoning</li>
                <li>• Keep answers focused</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}