import { useState } from "react";
import { startInterview } from "../api/interview";

const ROLES  = ["AI Engineer","Data Scientist","Backend Developer","ML Engineer","Full Stack Developer"];
const LEVELS = ["Fresher","1-3 years","Senior"];

export default function SetupPage({ onStart }) {
  const [resume,  setResume]  = useState(null);
  const [jd,      setJd]      = useState("");
  const [role,    setRole]    = useState(ROLES[0]);
  const [level,   setLevel]   = useState(LEVELS[0]);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState("");
  const [step,    setStep]    = useState(1); // 1=upload 2=details

  const handleStart = async () => {
    if (!resume)    return setError("Please upload your resume PDF.");
    if (!jd.trim()) return setError("Please enter the job description.");
    setError("");
    setLoading(true);
    try {
      const data = await startInterview(resume, jd, role, level);
      onStart({
        sessionId:      data.session_id,
        openingMessage: data.opening_message,
        firstQuestion:  data.question,
        questionType:   data.question_type,
        questionNumber: data.question_number,
      });
    } catch(e) {
      setError("Could not connect to backend. Make sure it's running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight:"100vh",
      background:"linear-gradient(135deg, #0F0A1E 0%, #1A0F35 40%, #0D1B2A 100%)",
      display:"flex", alignItems:"center", justifyContent:"center",
      padding:24, fontFamily:"'Inter',-apple-system,sans-serif", color:"#fff"
    }}>
      {/* Background blobs */}
      <div style={{
        position:"fixed", top:"10%", left:"5%",
        width:400, height:400, borderRadius:"50%",
        background:"radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%)",
        pointerEvents:"none"
      }}/>
      <div style={{
        position:"fixed", bottom:"10%", right:"5%",
        width:500, height:500, borderRadius:"50%",
        background:"radial-gradient(circle, rgba(236,72,153,0.1) 0%, transparent 70%)",
        pointerEvents:"none"
      }}/>

      <div style={{width:"100%", maxWidth:520, position:"relative", zIndex:1}}>

        {/* Header */}
        <div style={{textAlign:"center", marginBottom:36}}>
          <div style={{
            display:"inline-flex", alignItems:"center", gap:8,
            background:"rgba(139,92,246,0.15)",
            border:"1px solid rgba(139,92,246,0.3)",
            borderRadius:30, padding:"6px 16px",
            fontSize:12, color:"#A78BFA",
            fontWeight:600, letterSpacing:1,
            textTransform:"uppercase", marginBottom:20
          }}>
            <span style={{
              width:6, height:6, borderRadius:"50%",
              background:"#A78BFA",
              boxShadow:"0 0 6px #A78BFA",
              display:"inline-block"
            }}/>
            AI Powered Interview
          </div>

          <h1 style={{
            fontSize:36, fontWeight:800, margin:"0 0 10px",
            background:"linear-gradient(135deg, #fff 0%, #C4B5FD 100%)",
            WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent"
          }}>
            Interview Simulator
          </h1>
          <p style={{fontSize:15, color:"rgba(255,255,255,0.45)", margin:0, lineHeight:1.6}}>
            Upload your resume and get a personalised AI interview<br/>tailored to your experience and target role
          </p>
        </div>

        {/* Steps */}
        <div style={{
          display:"flex", alignItems:"center",
          justifyContent:"center", gap:0, marginBottom:28
        }}>
          {[{n:1,l:"Upload"},{n:2,l:"Details"}].map((s,i) => (
            <div key={s.n} style={{display:"flex", alignItems:"center"}}>
              <div
                onClick={() => s.n < step || resume ? setStep(s.n) : null}
                style={{
                  display:"flex", flexDirection:"column",
                  alignItems:"center", gap:4, cursor:"pointer"
                }}
              >
                <div style={{
                  width:32, height:32, borderRadius:"50%",
                  display:"flex", alignItems:"center", justifyContent:"center",
                  fontSize:13, fontWeight:700,
                  background: step >= s.n
                    ? "linear-gradient(135deg,#8B5CF6,#EC4899)"
                    : "rgba(255,255,255,0.06)",
                  color: step >= s.n ? "#fff" : "rgba(255,255,255,0.3)",
                  border: step >= s.n ? "none" : "1px solid rgba(255,255,255,0.1)"
                }}>
                  {step > s.n ? "✓" : s.n}
                </div>
                <span style={{
                  fontSize:11, fontWeight:600,
                  color: step >= s.n ? "#A78BFA" : "rgba(255,255,255,0.3)"
                }}>
                  {s.l}
                </span>
              </div>
              {i === 0 && (
                <div style={{
                  width:80, height:1, margin:"0 8px",
                  background: step > 1
                    ? "linear-gradient(90deg,#8B5CF6,#EC4899)"
                    : "rgba(255,255,255,0.08)",
                  marginBottom:20
                }}/>
              )}
            </div>
          ))}
        </div>

        {/* Card */}
        <div style={{
          background:"rgba(255,255,255,0.04)",
          backdropFilter:"blur(20px)",
          border:"1px solid rgba(255,255,255,0.08)",
          borderRadius:24, padding:32,
          boxShadow:"0 25px 60px rgba(0,0,0,0.4)"
        }}>

          {step === 1 && (
            <div style={{display:"flex", flexDirection:"column", gap:20}}>
              <div>
                <label style={{
                  display:"block", fontSize:11, fontWeight:700,
                  color:"rgba(255,255,255,0.4)", marginBottom:10,
                  textTransform:"uppercase", letterSpacing:1.2
                }}>
                  Resume PDF
                </label>
                <label style={{
                  display:"flex", flexDirection:"column",
                  alignItems:"center", justifyContent:"center",
                  width:"100%", height:140,
                  border: resume
                    ? "1px solid rgba(139,92,246,0.5)"
                    : "1px dashed rgba(255,255,255,0.12)",
                  borderRadius:16, cursor:"pointer",
                  background: resume
                    ? "rgba(139,92,246,0.08)"
                    : "rgba(255,255,255,0.02)",
                  transition:"all 0.2s", gap:8
                }}>
                  <input
                    type="file" accept=".pdf"
                    style={{display:"none"}}
                    onChange={e => setResume(e.target.files[0])}
                  />
                  {resume ? (
                    <>
                      <div style={{
                        width:48, height:48, borderRadius:12,
                        background:"rgba(139,92,246,0.2)",
                        display:"flex", alignItems:"center",
                        justifyContent:"center", fontSize:22
                      }}>📄</div>
                      <span style={{fontSize:13, color:"#A78BFA", fontWeight:600}}>
                        {resume.name}
                      </span>
                      <span style={{fontSize:11, color:"rgba(255,255,255,0.3)"}}>
                        Click to change file
                      </span>
                    </>
                  ) : (
                    <>
                      <div style={{
                        width:48, height:48, borderRadius:12,
                        background:"rgba(255,255,255,0.04)",
                        display:"flex", alignItems:"center",
                        justifyContent:"center", fontSize:22, opacity:0.5
                      }}>📤</div>
                      <span style={{fontSize:13, color:"rgba(255,255,255,0.4)"}}>
                        Click to upload your resume
                      </span>
                      <span style={{fontSize:11, color:"rgba(255,255,255,0.2)"}}>
                        PDF format only
                      </span>
                    </>
                  )}
                </label>
              </div>

              <div>
                <label style={{
                  display:"block", fontSize:11, fontWeight:700,
                  color:"rgba(255,255,255,0.4)", marginBottom:10,
                  textTransform:"uppercase", letterSpacing:1.2
                }}>
                  Job Description
                </label>
                <textarea
                  rows={5}
                  placeholder="Paste the full job description here..."
                  value={jd}
                  onChange={e => setJd(e.target.value)}
                  style={{
                    width:"100%", background:"rgba(255,255,255,0.04)",
                    border:"1px solid rgba(255,255,255,0.08)",
                    borderRadius:12, padding:"12px 16px",
                    color:"#fff", fontSize:13, resize:"none",
                    outline:"none", fontFamily:"inherit", lineHeight:1.6
                  }}
                />
              </div>

              <button
                onClick={() => {
                  if (!resume) return setError("Please upload your resume first.");
                  if (!jd.trim()) return setError("Please add the job description.");
                  setError("");
                  setStep(2);
                }}
                style={{
                  width:"100%", padding:"14px",
                  borderRadius:12, border:"none",
                  background:"linear-gradient(135deg,#8B5CF6,#EC4899)",
                  color:"#fff", fontSize:14, fontWeight:700,
                  cursor:"pointer", letterSpacing:0.3
                }}
              >
                Continue →
              </button>
            </div>
          )}

          {step === 2 && (
            <div style={{display:"flex", flexDirection:"column", gap:20}}>
              <div style={{display:"grid", gridTemplateColumns:"1fr 1fr", gap:16}}>
                <div>
                  <label style={{
                    display:"block", fontSize:11, fontWeight:700,
                    color:"rgba(255,255,255,0.4)", marginBottom:10,
                    textTransform:"uppercase", letterSpacing:1.2
                  }}>
                    Target Role
                  </label>
                  <select
                    value={role}
                    onChange={e => setRole(e.target.value)}
                    style={{
                      width:"100%", background:"rgba(255,255,255,0.04)",
                      border:"1px solid rgba(255,255,255,0.08)",
                      borderRadius:12, padding:"12px 16px",
                      color:"#fff", fontSize:13, outline:"none"
                    }}
                  >
                    {ROLES.map(r => <option key={r} style={{background:"#1A0F35"}}>{r}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{
                    display:"block", fontSize:11, fontWeight:700,
                    color:"rgba(255,255,255,0.4)", marginBottom:10,
                    textTransform:"uppercase", letterSpacing:1.2
                  }}>
                    Experience Level
                  </label>
                  <select
                    value={level}
                    onChange={e => setLevel(e.target.value)}
                    style={{
                      width:"100%", background:"rgba(255,255,255,0.04)",
                      border:"1px solid rgba(255,255,255,0.08)",
                      borderRadius:12, padding:"12px 16px",
                      color:"#fff", fontSize:13, outline:"none"
                    }}
                  >
                    {LEVELS.map(l => <option key={l} style={{background:"#1A0F35"}}>{l}</option>)}
                  </select>
                </div>
              </div>

              {/* Summary card */}
              <div style={{
                background:"rgba(139,92,246,0.08)",
                border:"1px solid rgba(139,92,246,0.2)",
                borderRadius:12, padding:16
              }}>
                <p style={{
                  fontSize:11, color:"#A78BFA", fontWeight:700,
                  textTransform:"uppercase", letterSpacing:1, marginBottom:10
                }}>
                  Interview Summary
                </p>
                <div style={{display:"flex", flexDirection:"column", gap:6}}>
                  {[
                    ["Resume", resume?.name],
                    ["Role", role],
                    ["Level", level],
                  ].map(([k,v]) => (
                    <div key={k} style={{
                      display:"flex", justifyContent:"space-between",
                      fontSize:12
                    }}>
                      <span style={{color:"rgba(255,255,255,0.4)"}}>{k}</span>
                      <span style={{color:"rgba(255,255,255,0.8)", fontWeight:500}}>{v}</span>
                    </div>
                  ))}
                </div>
              </div>

              {error && (
                <div style={{
                  background:"rgba(239,68,68,0.1)",
                  border:"1px solid rgba(239,68,68,0.25)",
                  borderRadius:10, padding:"10px 14px",
                  fontSize:13, color:"#FCA5A5"
                }}>
                  {error}
                </div>
              )}

              <div style={{display:"flex", gap:10}}>
                <button
                  onClick={() => setStep(1)}
                  style={{
                    padding:"14px 20px", borderRadius:12,
                    border:"1px solid rgba(255,255,255,0.1)",
                    background:"transparent", color:"rgba(255,255,255,0.5)",
                    fontSize:14, cursor:"pointer"
                  }}
                >
                  ← Back
                </button>
                <button
                  onClick={handleStart}
                  disabled={loading}
                  style={{
                    flex:1, padding:"14px",
                    borderRadius:12, border:"none",
                    background: loading
                      ? "rgba(255,255,255,0.06)"
                      : "linear-gradient(135deg,#8B5CF6,#EC4899)",
                    color: loading ? "rgba(255,255,255,0.3)" : "#fff",
                    fontSize:14, fontWeight:700,
                    cursor: loading ? "not-allowed" : "pointer",
                    display:"flex", alignItems:"center",
                    justifyContent:"center", gap:8
                  }}
                >
                  {loading ? (
                    <>
                      <div style={{
                        width:16, height:16, borderRadius:"50%",
                        border:"2px solid rgba(255,255,255,0.2)",
                        borderTopColor:"#fff",
                        animation:"spin 0.8s linear infinite"
                      }}/>
                      Preparing interview...
                    </>
                  ) : "🚀 Start Interview"}
                </button>
              </div>
            </div>
          )}
        </div>

        <p style={{
          textAlign:"center", fontSize:11,
          color:"rgba(255,255,255,0.18)", marginTop:20
        }}>
          Powered by LangGraph • Groq • Deepgram Aura • Whisper STT
        </p>
      </div>

      <style>{`
        @keyframes spin{to{transform:rotate(360deg)}}
        textarea::placeholder{color:rgba(255,255,255,0.2)!important}
        textarea:focus,select:focus{border-color:rgba(139,92,246,0.5)!important;outline:none!important}
        select option{background:#1A0F35;color:#fff}
      `}</style>
    </div>
  );
}