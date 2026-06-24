import { useState } from "react";
import SetupPage    from "./components/SetupPage";
import InterviewPage from "./components/InterviewPage";
import ReportPage   from "./components/ReportPage";

export default function App() {
  const [page, setPage]       = useState("setup");   // setup | interview | report
  const [session, setSession] = useState(null);       // { sessionId, firstQuestion, ... }
  const [report,  setReport]  = useState(null);

  return (
    <div className="min-h-screen bg-[#0f0f1a]">
      {page === "setup"     && (
        <SetupPage onStart={(data) => { setSession(data); setPage("interview"); }} />
      )}
      {page === "interview" && (
        <InterviewPage
          session={session}
          onComplete={(r) => { setReport(r); setPage("report"); }}
        />
      )}
      {page === "report"    && (
        <ReportPage report={report} onRestart={() => { setSession(null); setPage("setup"); }} />
      )}
    </div>
  );
}