import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Mail, Power, Repeat, Sliders, CheckCircle2, ToggleLeft, ToggleRight, FileText } from 'lucide-react';

interface HistoryItem {
  id: number;
  url: string;
  topic: string;
  summary: string;
  data_json: string;
  timestamp: string;
  status: string;
}

const ScheduleView: React.FC = () => {
  const [frequency, setFrequency] = useState(2); // 0: Daily, 1: Weekly, 2: Custom
  const [targetUrl, setTargetUrl] = useState('');
  const [extractTopic, setExtractTopic] = useState(true);
  const [extractHint, setExtractHint] = useState('');
  const [email, setEmail] = useState('');
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/history?limit=3');
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (e) {
      console.error("Failed to fetch history");
    }
  };

  const handleSchedule = async () => {
    if (!targetUrl || !email) {
      alert('請輸入 URL 和 Email');
      return;
    }
    if (!confirm('確認啟動排程?')) return;
    try {
      await fetch('http://localhost:8000/api/schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          frequency: frequency,
          email: email,
          url: targetUrl,
          topic: extractTopic ? (extractHint || "News/Articles") : "Raw"
        })
      });
      alert('排程已啟動');
    } catch (e) {
      alert('排程失敗');
    }
  };

  return (
    <div className="glass-panel rounded-3xl p-8 h-full flex flex-col animate-in fade-in slide-in-from-right-4 duration-500 border-t border-purple-500/20 shadow-[0_0_40px_-10px_rgba(168,85,247,0.1)]">

      {/* Title Section */}
      <div className="mb-8 border-b border-slate-800 pb-4">
        <h2 className="text-2xl font-bold text-white flex items-center gap-3">
          <Calendar className="text-purple-400" />
          任務排程器
        </h2>
        <p className="text-slate-400 mt-1">自動化擷取流程。</p>
      </div>

      <div className="space-y-8">

        {/* URL Input (New) */}
        <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 hover:border-purple-500/30 transition-colors">
          <label className="text-slate-300 font-medium block mb-3 flex items-center gap-2">
            <ToggleRight size={16} /> 目標網站 URL
          </label>
          <input
            type="text"
            value={targetUrl}
            onChange={(e) => setTargetUrl(e.target.value)}
            placeholder="https://example.com"
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all placeholder:text-slate-600"
          />
        </div>

        {/* Topic Toggle */}
        <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 flex flex-col justify-between hover:border-purple-500/30 transition-colors">
          <div className="flex justify-between items-start mb-4">
            <span className="text-slate-300 font-medium">智能主題擷取</span>
            <button
              onClick={() => setExtractTopic(!extractTopic)}
              className="text-purple-400 transition-transform active:scale-95"
            >
              {extractTopic ? <ToggleRight size={32} /> : <ToggleLeft size={32} className="text-slate-600" />}
            </button>
          </div>

          {extractTopic && (
            <input
              type="text"
              value={extractHint}
              onChange={(e) => setExtractHint(e.target.value)}
              placeholder="輸入主題關鍵字 (例如: 最新新聞)..."
              className="w-full bg-slate-950/50 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-purple-500 mb-2 placeholder:text-slate-600"
            />
          )}
          <p className="text-xs text-slate-500">
            {extractTopic ? "AI 將依據關鍵字進行週期性擷取。" : "將回傳未經分析的原始 HTML 內容。"}
          </p>
        </div>

        {/* Email Input */}
        <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 hover:border-purple-500/30 transition-colors">
          <label className="text-slate-300 font-medium block mb-3 flex items-center gap-2">
            <Mail size={16} /> 報告接收信箱
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="reports@example.com"
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all placeholder:text-slate-600"
          />
        </div>

        {/* Frequency Settings */}
        <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
          <label className="text-slate-300 font-medium block mb-6 flex items-center gap-2">
            <Repeat size={16} /> 執行頻率
          </label>

          {/* Custom Range Slider Lookalike */}
          <div className="space-y-6">
            <div className="flex justify-between items-center bg-slate-950 p-1 rounded-xl">
              {['每日', '每週', '自訂'].map((label, idx) => (
                <button
                  key={label}
                  onClick={() => setFrequency(idx)}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${frequency === idx
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'text-slate-500 hover:text-slate-300'
                    }`}
                >
                  {label}
                </button>
              ))}
            </div>

            {frequency === 2 && (
              <div className="animate-in fade-in zoom-in duration-300 bg-slate-950/50 p-4 rounded-xl border border-dashed border-slate-800">
                <div className="flex items-center gap-4">
                  <Clock className="text-slate-500" size={18} />
                  <div className="flex-1">
                    <label className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-1 block">間隔 (小時)</label>
                    <input type="range" className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500" />
                  </div>
                  <span className="font-mono text-purple-400 font-bold text-lg">12h</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* History Preview Section */}
        <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
          <div className="flex justify-between items-center mb-4">
            <span className="text-sm font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
              <FileText size={14} /> 最近活動
            </span>
          </div>
          <div className="space-y-3">
            {history.map((item) => (
              <div key={item.id} className="flex items-center justify-between p-3 rounded bg-slate-950/50 border border-slate-800/50">
                <div className="flex items-center gap-3 overflow-hidden">
                  <div className={`w-2 h-2 rounded-full ${item.status === 'success' ? 'bg-emerald-500' : 'bg-red-500'}`} />
                  <span className="text-xs text-slate-300 truncate max-w-[200px]">{item.url}</span>
                </div>
                <span className="text-[10px] text-slate-600 font-mono">{new Date(item.timestamp).toLocaleTimeString()}</span>
              </div>
            ))}
            {history.length === 0 && <div className="text-center text-slate-600 text-xs py-2">無近期活動</div>}
          </div>
        </div>

        {/* Start Button */}
        <div className="pt-2">
          <button
            onClick={handleSchedule}
            className="group w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-2xl p-4 transition-all duration-300 shadow-lg shadow-purple-900/50 hover:shadow-purple-500/20 active:scale-[0.99] flex items-center justify-between px-8">
            <div className="flex flex-col items-start">
              <span className="font-bold text-lg tracking-wide">啟動排程</span>
              <span className="text-xs text-purple-200/60 font-mono">下次執行: 倒數 12:00:00</span>
            </div>
            <div className="h-10 w-10 bg-white/20 rounded-full flex items-center justify-center group-hover:rotate-90 transition-transform duration-500">
              <Power size={20} className="fill-current" />
            </div>
          </button>
        </div>

      </div>
    </div>
  );
};

export default ScheduleView;