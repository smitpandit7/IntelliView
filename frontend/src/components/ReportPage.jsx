export default function ReportPage({ report, onRestart }) {
  const scores = report?.scores || [];
  const avg    = report?.average_score || 0;

  const scoreColor = (s) =>
    s >= 7 ? "text-green-400" : s >= 5 ? "text-yellow-400" : "text-red-400";

  const label = avg >= 8 ? "Excellent 🏆"
              : avg >= 7 ? "Good ✅"
              : avg >= 5 ? "Average 📈"
              : "Needs Work 📚";

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-[#0f0f1a]">
      <div className="w-full max-w-2xl">

        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">
            {avg >= 7 ? "🎉" : avg >= 5 ? "📊" : "📚"}
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Interview Complete</h1>
          <p className="text-gray-400">Here's how you performed</p>
        </div>

        {/* Score card */}
        <div className="bg-[#16213e] rounded-2xl p-8 border border-[#ffffff10]
                        shadow-2xl mb-6">

          <div className="text-center mb-6">
            <p className={`text-7xl font-bold ${scoreColor(avg)}`}>
              {avg.toFixed(1)}
            </p>
            <p className="text-gray-400 text-lg mt-1">out of 10</p>
            <p className={`text-xl font-bold mt-2 ${scoreColor(avg)}`}>{label}</p>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-[#0f0f1a] rounded-xl p-4 text-center">
              <p className="text-gray-500 text-xs mb-1">Total Questions</p>
              <p className="text-white text-2xl font-bold">{report?.total_questions || scores.length}</p>
            </div>
            <div className="bg-[#0f0f1a] rounded-xl p-4 text-center">
              <p className="text-gray-500 text-xs mb-1">Best Score</p>
              <p className={`text-2xl font-bold ${scoreColor(Math.max(...scores))}`}>
                {scores.length ? Math.max(...scores) : 0}/10
              </p>
            </div>
          </div>

          {/* Score bars */}
          <div className="space-y-3">
            <p className="text-gray-400 text-sm font-semibold">Score per question</p>
            {scores.map((s, i) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-gray-500 text-xs w-6">Q{i+1}</span>
                <div className="flex-1 bg-[#0f0f1a] rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-700
                      ${s >= 7 ? "bg-green-500" : s >= 5 ? "bg-yellow-500" : "bg-red-500"}`}
                    style={{ width: `${s * 10}%` }}
                  />
                </div>
                <span className={`text-xs font-bold w-10 ${scoreColor(s)}`}>
                  {s}/10
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="grid grid-cols-2 gap-4">
          <button
            onClick={onRestart}
            className="bg-[#16213e] hover:bg-[#1a2a50] border border-[#ffffff15]
                       text-white font-bold py-4 rounded-xl transition-colors"
          >
            🔄 New Interview
          </button>
          <button
            onClick={() => alert("Report saved at: " + report?.report_path)}
            className="bg-[#1a7a4a] hover:bg-[#156a3e] text-white font-bold
                       py-4 rounded-xl transition-colors"
          >
            📄 View Report Path
          </button>
        </div>

        <p className="text-center text-gray-600 text-xs mt-6">
          Detailed PDF report generated at backend/reports/
        </p>
      </div>
    </div>
  );
}