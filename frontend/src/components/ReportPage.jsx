export default function ReportPage({ report, onRestart }) {
  const scores = report?.scores || [];
  const avg    = report?.average_score || 0;

  const grade = avg >= 8 ? {l:"Excellent",c:"#10B981",bg:"rgba(16,185,129,0.1)"}
              : avg >= 7 ? {l:"Good",     c:"#8B5CF6",bg:"rgba(139,92,246,0.1)"}
              : avg >= 5 ? {l:"Average",  c:"#F59E0B",bg:"rgba(245,158,11,0.1)"}
              :            {l:"Keep Practicing",c:"#EF4444",bg:"rgba(239,68,68,0.1)"};

  const emoji = avg >= 7 ? "🎉" : avg >= 5 ? "📊" : "📚";

  return (
    <div style={{
      minHeight:"100vh",
      background:"linear-gradient(135deg,#0F0A1E 0%,#1A0F35 50%,#0D1B2A 100%)",
      display:"flex", alignItems:"center", justifyContent:"center",
      padding:24, fontFamily:"'Inter',-apple-system,sans-serif", color:"#fff"
    }}>
      <div style={{position:"fixed",top:"10%",left:"5%",width:400,height:400,borderRadius:"50%",background:"radial-gradient(circle,rgba(139,92,246,0.12) 0%,transparent 70%)",pointerEvents:"none"}}/>
      <div style={{position:"fixed",bottom:"10%",right:"5%",width:500,height:500,borderRadius:"50%",background:"radial-gradient(circle,rgba(236,72,153,0.08) 0%,transparent 70%)",pointerEvents:"none"}}/>

      <div style={{width:"100%", maxWidth:560, position:"relative", zIndex:1}}>

        {/* Header */}
        <div style={{textAlign:"center", marginBottom:28}}>
          <div style={{fontSize:56, marginBottom:12}}>{emoji}</div>
          <h1 style={{
            fontSize:28, fontWeight:800, margin:"0 0 8px",
            background:"linear-gradient(135deg,#fff,#C4B5FD)",
            WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent"
          }}>
            Interview Complete
          </h1>
          <p style={{fontSize:14, color:"rgba(255,255,255,0.4)", margin:0}}>
            Here's your full performance breakdown
          </p>
        </div>

        {/* Score card */}
        <div style={{
          background:"rgba(255,255,255,0.04)",
          backdropFilter:"blur(20px)",
          border:"1px solid rgba(255,255,255,0.08)",
          borderRadius:24, padding:28, marginBottom:16,
          boxShadow:"0 25px 60px rgba(0,0,0,0.4)"
        }}>
          {/* Overall */}
          <div style={{
            textAlign:"center", marginBottom:24,
            padding:"20px 0",
            borderBottom:"1px solid rgba(255,255,255,0.06)"
          }}>
            <div style={{
              display:"inline-flex", alignItems:"baseline",
              gap:4, marginBottom:8
            }}>
              <span style={{
                fontSize:64, fontWeight:800,
                color: grade.c,
                lineHeight:1
              }}>
                {avg.toFixed(1)}
              </span>
              <span style={{
                fontSize:20, color:"rgba(255,255,255,0.3)",
                fontWeight:400
              }}>
                /10
              </span>
            </div>
            <div style={{
              display:"inline-block",
              background: grade.bg,
              border:`1px solid ${grade.c}40`,
              borderRadius:20, padding:"4px 16px",
              fontSize:13, fontWeight:700, color:grade.c
            }}>
              {grade.l}
            </div>
          </div>

          {/* Stats row */}
          <div style={{
            display:"grid", gridTemplateColumns:"repeat(3,1fr)",
            gap:12, marginBottom:24
          }}>
            {[
              ["Total Questions", scores.length],
              ["Best Score", scores.length ? Math.max(...scores) + "/10" : "—"],
              ["Worst Score", scores.length ? Math.min(...scores) + "/10" : "—"],
            ].map(([l,v]) => (
              <div key={l} style={{
                background:"rgba(255,255,255,0.04)",
                border:"1px solid rgba(255,255,255,0.06)",
                borderRadius:12, padding:"12px 16px", textAlign:"center"
              }}>
                <p style={{fontSize:11,color:"rgba(255,255,255,0.3)",margin:"0 0 4px",textTransform:"uppercase",letterSpacing:0.8}}>{l}</p>
                <p style={{fontSize:18,fontWeight:700,color:"#fff",margin:0}}>{v}</p>
              </div>
            ))}
          </div>

          {/* Per question scores */}
          <p style={{
            fontSize:10, fontWeight:700, letterSpacing:1.5,
            textTransform:"uppercase", color:"rgba(255,255,255,0.3)",
            marginBottom:14
          }}>
            Question Scores
          </p>
          <div style={{display:"flex", flexDirection:"column", gap:10}}>
            {scores.map((s,i) => {
              const c = s>=7?"#10B981":s>=5?"#F59E0B":"#EF4444";
              return (
                <div key={i} style={{display:"flex",alignItems:"center",gap:12}}>
                  <span style={{
                    fontSize:11, color:"rgba(255,255,255,0.3)",
                    width:24, flexShrink:0
                  }}>
                    Q{i+1}
                  </span>
                  <div style={{
                    flex:1, height:6,
                    background:"rgba(255,255,255,0.06)",
                    borderRadius:3, overflow:"hidden"
                  }}>
                    <div style={{
                      height:6, borderRadius:3,
                      width:`${s*10}%`,
                      background:`linear-gradient(90deg,${c}99,${c})`,
                      transition:"width 0.8s ease"
                    }}/>
                  </div>
                  <span style={{
                    fontSize:12, fontWeight:700, color:c,
                    width:36, textAlign:"right", flexShrink:0
                  }}>
                    {s}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Report path */}
        {report?.report_path && (
          <div style={{
            background:"rgba(139,92,246,0.08)",
            border:"1px solid rgba(139,92,246,0.2)",
            borderRadius:14, padding:"12px 16px", marginBottom:16,
            display:"flex", alignItems:"center",
            justifyContent:"space-between"
          }}>
            <div>
              <p style={{fontSize:11,color:"#A78BFA",fontWeight:700,margin:"0 0 2px",textTransform:"uppercase",letterSpacing:0.8}}>
                PDF Report
              </p>
              <p style={{fontSize:12,color:"rgba(255,255,255,0.4)",margin:0}}>
                Saved at: {report.report_path}
              </p>
            </div>
            <span style={{fontSize:20}}>📄</span>
          </div>
        )}

        {/* Actions */}
        <div style={{display:"grid", gridTemplateColumns:"1fr 1fr", gap:12}}>
          <button
            onClick={onRestart}
            style={{
              padding:"14px", borderRadius:14,
              border:"1px solid rgba(255,255,255,0.1)",
              background:"rgba(255,255,255,0.04)",
              color:"rgba(255,255,255,0.7)",
              fontSize:14, fontWeight:600, cursor:"pointer"
            }}
          >
            🔄 New Interview
          </button>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding:"14px", borderRadius:14, border:"none",
              background:"linear-gradient(135deg,#8B5CF6,#EC4899)",
              color:"#fff", fontSize:14, fontWeight:700, cursor:"pointer"
            }}
          >
            🏠 Home
          </button>
        </div>
      </div>
    </div>
  );
}