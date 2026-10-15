import { useState, useEffect, useRef } from "react";
import { submitAnswer, getReport, speakQuestion, transcribeAudio } from "../api/interview";

export default function InterviewPage({ session, onComplete }) {
  const [question,  setQuestion]  = useState(session.firstQuestion);
  const [qType,     setQType]     = useState(session.questionType);
  const [qNum,      setQNum]      = useState(session.questionNumber);
  const [answer,    setAnswer]    = useState("");
  const [loading,   setLoading]   = useState(false);
  const [speaking,  setSpeaking]  = useState(false);
  const [recording, setRecording] = useState(false);
  const [timer,     setTimer]     = useState(0);
  const [scores,    setScores]    = useState([]);
  const videoRef    = useRef(null);
  const mediaRecRef = useRef(null);
  const chunksRef   = useRef([]);
  const hasSpoken   = useRef(false);
  const canvasRef   = useRef(null);
  const animRef     = useRef(null);
  const frameRef    = useRef(0);

  const formatTime = (s) =>
    `${String(Math.floor(s/60)).padStart(2,"0")}:${String(s%60).padStart(2,"0")}`;

  // Timer
  useEffect(() => {
    const t = setInterval(() => setTimer(t => t+1), 1000);
    return () => clearInterval(t);
  }, []);

  // Webcam
  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video:true })
      .then(stream => { if (videoRef.current) videoRef.current.srcObject = stream; })
      .catch(() => {});
    return () => {
      if (videoRef.current?.srcObject)
        videoRef.current.srcObject.getTracks().forEach(t => t.stop());
    };
  }, []);

  // Speak first question once
  useEffect(() => {
    if (!hasSpoken.current) {
      hasSpoken.current = true;
      handleSpeak(session.firstQuestion);
    }
  }, []);

  // Wave animation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.width;
    const H = canvas.height;

    function draw() {
      ctx.clearRect(0, 0, W, H);
      const bars = 40;
      const barW = 3;
      const gap  = (W - bars * barW) / (bars + 1);

      for (let i = 0; i < bars; i++) {
        const x = gap + i * (barW + gap);
        let h;
        if (speaking) {
          // Animated wave when speaking
          const wave1 = Math.sin(frameRef.current * 0.08 + i * 0.4) * 0.5 + 0.5;
          const wave2 = Math.sin(frameRef.current * 0.12 + i * 0.6) * 0.3;
          const wave3 = Math.sin(frameRef.current * 0.05 + i * 0.2) * 0.2;
          h = Math.max(4, (wave1 + wave2 + wave3) * (H * 0.7));
        } else {
          // Idle small pulse
          h = 4 + Math.sin(frameRef.current * 0.03 + i * 0.3) * 3;
        }

        const centerY = H / 2;
        const alpha   = speaking ? 0.8 : 0.3;

        // Gradient per bar
        const grad = ctx.createLinearGradient(x, centerY - h/2, x, centerY + h/2);
        grad.addColorStop(0, `rgba(139,92,246,${alpha})`);
        grad.addColorStop(0.5, `rgba(236,72,153,${alpha})`);
        grad.addColorStop(1, `rgba(139,92,246,${alpha})`);

        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.roundRect(x, centerY - h/2, barW, h, 2);
        ctx.fill();
      }

      frameRef.current++;
      animRef.current = requestAnimationFrame(draw);
    }

    draw();
    return () => cancelAnimationFrame(animRef.current);
  }, [speaking]);

  const handleSpeak = async (text) => {
    setSpeaking(true);
    try {
      if (window._currentAudio) {
        window._currentAudio.pause();
        window._currentAudio = null;
      }
      const res = await fetch("http://localhost:8000/voice/speak", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ text })
      });
      const blob = await res.blob();
      const url  = URL.createObjectURL(blob);
      const audio = new Audio(url);
      window._currentAudio = audio;
      await new Promise((resolve) => {
        audio.onended = () => { URL.revokeObjectURL(url); resolve(); };
        audio.onerror = resolve;
        audio.play();
      });
    } catch(e) { console.error(e); }
    setSpeaking(false);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio:true });
      const mr = new MediaRecorder(stream, { mimeType:"audio/webm" });
      chunksRef.current = [];
      mr.ondataavailable = e => { if (e.data.size > 0) chunksRef.current.push(e.data); };
      mr.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type:"audio/webm" });
        try {
          const t = await transcribeAudio(blob);
          setAnswer(t);
        } catch(e) { console.error(e); }
        stream.getTracks().forEach(t => t.stop());
      };
      mr.start();
      mediaRecRef.current = mr;
      setRecording(true);
    } catch(e) { console.error(e); }
  };

  const stopRecording = () => {
    if (mediaRecRef.current) {
      mediaRecRef.current.stop();
      mediaRecRef.current = null;
      setRecording(false);
    }
  };

  const handleSubmit = async () => {
    if (!answer.trim() || loading) return;
    const userAnswer = answer.trim();
    setAnswer("");
    setLoading(true);
    try {
      const data = await submitAnswer(session.sessionId, userAnswer);
      setScores(s => [...s, data.last_score]);
      if (data.is_complete) {
        const report = await getReport(session.sessionId);
        onComplete({ ...report, scores:[...scores, data.last_score] });
      } else {
        setQuestion(data.question);
        setQType(data.question_type);
        setQNum(data.question_number);
        handleSpeak(data.question);
      }
    } catch(e) { console.error(e); }
    finally { setLoading(false); }
  };

  const progress = Math.round((qNum / 9) * 100);

  return (
    <div style={{
      height:"100vh", display:"flex", flexDirection:"column",
      background:"linear-gradient(135deg,#0F0A1E 0%,#1A0F35 50%,#0D1B2A 100%)",
      fontFamily:"'Inter',-apple-system,sans-serif", color:"#fff",
      overflow:"hidden"
    }}>

      {/* Blobs */}
      <div style={{position:"fixed",top:"-10%",left:"-10%",width:500,height:500,borderRadius:"50%",background:"radial-gradient(circle,rgba(139,92,246,0.1) 0%,transparent 70%)",pointerEvents:"none"}}/>
      <div style={{position:"fixed",bottom:"-10%",right:"-5%",width:600,height:600,borderRadius:"50%",background:"radial-gradient(circle,rgba(236,72,153,0.07) 0%,transparent 70%)",pointerEvents:"none"}}/>

      {/* ── TOP BAR ── */}
      <div style={{
        display:"flex", alignItems:"center",
        justifyContent:"space-between",
        padding:"0 28px", height:56, flexShrink:0,
        background:"rgba(255,255,255,0.03)",
        borderBottom:"1px solid rgba(255,255,255,0.06)",
        backdropFilter:"blur(10px)", zIndex:10
      }}>
        <div style={{display:"flex", alignItems:"center", gap:10}}>
          <div style={{
            width:8, height:8, borderRadius:"50%",
            background:"#8B5CF6", boxShadow:"0 0 10px #8B5CF6"
          }}/>
          <span style={{fontSize:14, fontWeight:700}}>AI Interview Simulator</span>
        </div>

        {/* Progress bar */}
        <div style={{
          flex:1, maxWidth:320, height:3,
          background:"rgba(255,255,255,0.06)",
          borderRadius:2, margin:"0 32px", overflow:"hidden"
        }}>
          <div style={{
            height:3, borderRadius:2,
            width:`${progress}%`,
            background:"linear-gradient(90deg,#8B5CF6,#EC4899)",
            transition:"width 0.5s ease"
          }}/>
        </div>

        <div style={{display:"flex", alignItems:"center", gap:12}}>
          <span style={{
            background:"rgba(139,92,246,0.15)",
            border:"1px solid rgba(139,92,246,0.3)",
            borderRadius:20, padding:"4px 14px",
            fontSize:12, color:"#C4B5FD", fontWeight:600
          }}>
            {qNum} / 9
          </span>
          <span style={{
            background: qType==="technical"
              ? "rgba(99,102,241,0.15)"
              : "rgba(236,72,153,0.15)",
            border: qType==="technical"
              ? "1px solid rgba(99,102,241,0.3)"
              : "1px solid rgba(236,72,153,0.3)",
            borderRadius:20, padding:"4px 14px",
            fontSize:12, fontWeight:700,
            textTransform:"uppercase",
            color: qType==="technical" ? "#818CF8" : "#F472B6"
          }}>
            {qType}
          </span>
          <span style={{
            fontSize:12, color:"rgba(255,255,255,0.3)",
            fontVariantNumeric:"tabular-nums",
            background:"rgba(255,255,255,0.04)",
            padding:"4px 10px", borderRadius:8,
            border:"1px solid rgba(255,255,255,0.06)"
          }}>
            {formatTime(timer)}
          </span>
        </div>
      </div>

      {/* ── MAIN ── */}
      <div style={{
        flex:1, display:"grid",
        gridTemplateColumns:"1fr 1fr",
        minHeight:0
      }}>

        {/* LEFT — Wave + Question */}
        <div style={{
          display:"flex", flexDirection:"column",
          alignItems:"center", justifyContent:"center",
          padding:"32px 40px", gap:28
        }}>

          {/* Wave visualizer */}
          <div style={{
            display:"flex", flexDirection:"column",
            alignItems:"center", gap:12
          }}>
            <canvas
              ref={canvasRef}
              width={300}
              height={80}
              style={{display:"block"}}
            />
            <p style={{
              fontSize:12, color:"rgba(255,255,255,0.3)",
              margin:0, letterSpacing:0.5
            }}>
              {speaking
                ? "🎙 Aria is speaking..."
                : loading
                ? "⏳ Processing..."
                : "Listening to your answer"}
            </p>
          </div>

          {/* Question card — full width, no cut */}
          <div style={{
            width:"100%",
            background:"rgba(255,255,255,0.05)",
            backdropFilter:"blur(20px)",
            border:"1px solid rgba(255,255,255,0.1)",
            borderRadius:20, padding:"24px 28px"
          }}>
            <div style={{
              display:"flex", alignItems:"center",
              gap:8, marginBottom:14
            }}>
              <div style={{
                width:6, height:6, borderRadius:"50%",
                background: qType==="technical" ? "#818CF8" : "#F472B6",
                boxShadow:`0 0 6px ${qType==="technical" ? "#818CF8" : "#F472B6"}`
              }}/>
              <span style={{
                fontSize:10, fontWeight:700,
                textTransform:"uppercase", letterSpacing:1.5,
                color: qType==="technical" ? "#818CF8" : "#F472B6"
              }}>
                {qType} · Question {qNum}
              </span>
            </div>

            <p style={{
              fontSize:15, color:"rgba(255,255,255,0.92)",
              lineHeight:1.75, margin:0, fontWeight:400
            }}>
              {loading
                ? <span style={{color:"rgba(255,255,255,0.35)"}}>Processing your answer...</span>
                : question
              }
            </p>
          </div>

          {/* Replay */}
          {!speaking && !loading && (
            <button
              onClick={() => handleSpeak(question)}
              style={{
                display:"flex", alignItems:"center", gap:6,
                padding:"8px 18px", borderRadius:20,
                border:"1px solid rgba(255,255,255,0.1)",
                background:"transparent",
                color:"rgba(255,255,255,0.35)",
                fontSize:12, cursor:"pointer"
              }}
            >
              🔊 Replay question
            </button>
          )}
        </div>

        {/* RIGHT — Camera + Progress */}
        <div style={{
          display:"flex", flexDirection:"column",
          padding:"32px 40px 32px 20px", gap:20,
          borderLeft:"1px solid rgba(255,255,255,0.04)",
          minHeight:0
        }}>

          {/* Camera */}
          <div style={{flex:1, minHeight:0}}>
            <p style={{
              fontSize:10, fontWeight:700, letterSpacing:1.5,
              textTransform:"uppercase",
              color:"rgba(255,255,255,0.2)", marginBottom:12
            }}>
              Your Camera
            </p>
            <div style={{
              width:"100%", height:"calc(100% - 30px)",
              borderRadius:20, overflow:"hidden",
              background:"rgba(255,255,255,0.03)",
              border:"1px solid rgba(255,255,255,0.06)",
              position:"relative"
            }}>
              <video
                ref={videoRef} autoPlay muted
                style={{
                  width:"100%", height:"100%",
                  objectFit:"cover", display:"block"
                }}
              />
              <div style={{
                position:"absolute", top:12, right:12,
                display:"flex", alignItems:"center", gap:5,
                background:"rgba(0,0,0,0.5)",
                backdropFilter:"blur(8px)",
                borderRadius:20, padding:"4px 10px",
                fontSize:10, fontWeight:700
              }}>
                <div style={{
                  width:5, height:5, borderRadius:"50%",
                  background:"#EF4444",
                  boxShadow:"0 0 6px #EF4444",
                  animation:"blink 1.5s ease-in-out infinite"
                }}/>
                LIVE
              </div>
              {recording && (
                <div style={{
                  position:"absolute", bottom:12, left:12, right:12,
                  background:"rgba(239,68,68,0.2)",
                  border:"1px solid rgba(239,68,68,0.4)",
                  borderRadius:10, padding:"8px 12px",
                  display:"flex", alignItems:"center", gap:8,
                  fontSize:12, color:"#FCA5A5"
                }}>
                  <div style={{
                    width:7, height:7, borderRadius:"50%",
                    background:"#EF4444",
                    animation:"blink 0.8s ease-in-out infinite"
                  }}/>
                  Recording...
                </div>
              )}
            </div>
          </div>

          {/* Progress dots */}
          <div style={{flexShrink:0}}>
            <p style={{
              fontSize:10, fontWeight:700, letterSpacing:1.5,
              textTransform:"uppercase",
              color:"rgba(255,255,255,0.2)", marginBottom:10
            }}>
              Progress
            </p>
            <div style={{display:"flex", gap:6, flexWrap:"wrap"}}>
              {Array.from({length:9},(_,i) => (
                <div key={i} style={{
                  width:26, height:26, borderRadius:8,
                  display:"flex", alignItems:"center",
                  justifyContent:"center", fontSize:10, fontWeight:700,
                  background: i < qNum-1
                    ? "linear-gradient(135deg,#8B5CF6,#EC4899)"
                    : i === qNum-1
                    ? "rgba(139,92,246,0.2)"
                    : "rgba(255,255,255,0.04)",
                  border: i === qNum-1
                    ? "1px solid rgba(139,92,246,0.5)"
                    : "1px solid rgba(255,255,255,0.06)",
                  color: i < qNum-1 ? "#fff"
                    : i === qNum-1 ? "#C4B5FD"
                    : "rgba(255,255,255,0.2)"
                }}>
                  {i < qNum-1 ? "✓" : i+1}
                </div>
              ))}
            </div>
            <p style={{
              fontSize:11, color:"rgba(255,255,255,0.2)", marginTop:8
            }}>
              {qNum-1} of 9 answered
            </p>
          </div>
        </div>
      </div>

      {/* ── BOTTOM INPUT ── */}
      <div style={{
        padding:"14px 28px",
        background:"rgba(255,255,255,0.02)",
        backdropFilter:"blur(20px)",
        borderTop:"1px solid rgba(255,255,255,0.05)",
        flexShrink:0, zIndex:10
      }}>
        <div style={{
          display:"flex", gap:10,
          maxWidth:700, margin:"0 auto"
        }}>
          <button
            onClick={recording ? stopRecording : startRecording}
            disabled={loading}
            style={{
              width:48, height:48, borderRadius:12,
              border: recording
                ? "1px solid rgba(239,68,68,0.5)"
                : "1px solid rgba(139,92,246,0.3)",
              background: recording
                ? "rgba(239,68,68,0.15)"
                : "rgba(139,92,246,0.1)",
              color: recording ? "#EF4444" : "#A78BFA",
              fontSize:18, cursor:"pointer", flexShrink:0,
              display:"flex", alignItems:"center", justifyContent:"center"
            }}
          >
            {recording ? "⏹" : "🎙"}
          </button>

          <textarea
            rows={2}
            placeholder={recording
              ? "Recording... click ⏹ when done"
              : "Type your answer or click 🎙 to speak..."}
            value={answer}
            onChange={e => setAnswer(e.target.value)}
            onKeyDown={e => { if (e.key==="Enter" && e.ctrlKey) handleSubmit(); }}
            disabled={loading}
            style={{
              flex:1, background:"rgba(255,255,255,0.05)",
              border:"1px solid rgba(255,255,255,0.08)",
              borderRadius:12, padding:"12px 16px",
              color:"#fff", fontSize:13, resize:"none",
              outline:"none", fontFamily:"inherit", lineHeight:1.5
            }}
          />

          <button
            onClick={handleSubmit}
            disabled={loading || !answer.trim()}
            style={{
              width:48, height:48, borderRadius:12, border:"none",
              background: loading || !answer.trim()
                ? "rgba(255,255,255,0.06)"
                : "linear-gradient(135deg,#8B5CF6,#EC4899)",
              color: loading || !answer.trim()
                ? "rgba(255,255,255,0.2)" : "#fff",
              cursor: loading || !answer.trim() ? "not-allowed" : "pointer",
              fontSize:18, flexShrink:0,
              display:"flex", alignItems:"center", justifyContent:"center"
            }}
          >
            {loading
              ? <div style={{
                  width:16,height:16,borderRadius:"50%",
                  border:"2px solid rgba(255,255,255,0.2)",
                  borderTopColor:"#fff",
                  animation:"spin 0.8s linear infinite"
                }}/>
              : "→"
            }
          </button>
        </div>
        <p style={{
          textAlign:"center", fontSize:11,
          color:"rgba(255,255,255,0.15)", marginTop:8
        }}>
          Ctrl+Enter to submit
        </p>
      </div>

      <style>{`
        @keyframes spin{to{transform:rotate(360deg)}}
        @keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
        textarea::placeholder{color:rgba(255,255,255,0.2)!important}
        textarea:focus{border-color:rgba(139,92,246,0.4)!important;outline:none!important}
      `}</style>
    </div>
  );
}