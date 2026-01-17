import React, { useState, useEffect } from 'react';
import { Mail, Play, Clock, Database, Search, ToggleLeft, ToggleRight, Trash2, FileText, Activity, X, ChevronRight } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface HistoryItem {
  id: number;
  url: string;
  topic: string;
  summary: string;
  data_json: string;
  timestamp: string;
  status: string;
}

const ManualView: React.FC = () => {
  // const [scraperType, setScraperType] = useState<'AI' | 'CSS'>('AI'); // Removed
  // const [extractTopic, setExtractTopic] = useState(true); // Removed
  // const [extractHint, setExtractHint] = useState(''); // Removed
  const [targetUrl, setTargetUrl] = useState('');
  const [email, setEmail] = useState('yeecc9598409@gmail.com');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [selectedHistory, setSelectedHistory] = useState<HistoryItem | null>(null);

  // Metrics
  const [lastTime, setLastTime] = useState<string | null>(null);
  const [lastCount, setLastCount] = useState<number | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/history?limit=10`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (e) {
      console.error("Failed to fetch history");
    }
  };

  const handleStartExtraction = async () => {
    if (!targetUrl) {
      alert('請輸入目標 URL');
      return;
    }
    setLoading(true);
    setLastTime(null);
    setLastCount(null);
    const startTime = Date.now();
    try {
      const response = await fetch(`${API_BASE_URL}/api/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: targetUrl,
          email: email
        })
      });
      // ...

      const endTime = Date.now();
      const duration = (endTime - startTime) / 1000;
      setLastTime(`${duration.toFixed(2)}s`);

      const data = await response.json();
      if (response.ok) {
        setLastCount(data.count);
        alert(`成功! 找到 ${data.count} 筆資料`);
        fetchHistory(); // Refresh history
      } else {
        alert(`失敗: ${data.detail}`);
      }
    } catch (e) {
      alert('連線錯誤');
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="glass-panel rounded-3xl p-8 h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500 border-t border-cyber-500/20 shadow-[0_0_40px_-10px_rgba(20,184,166,0.1)]">

      {/* Title Section */}
      <div className="mb-8 border-b border-slate-800 pb-4">
        <h2 className="text-2xl font-bold text-white flex items-center gap-3">
          <Search className="text-cyber-400" />
          立即執行
        </h2>
        <p className="text-slate-400 mt-1">設定即時爬取參數。</p>
      </div>

      <div className="space-y-8 flex-1">

        {/* URL Input */}
        <div className="bg-slate-900/50 p-5 rounded-2xl border border-slate-800 group hover:border-cyber-500/30 transition-colors">
          <label className="text-slate-300 font-medium block mb-3 flex items-center gap-2">
            <ToggleRight size={16} /> 目標網站 URL
          </label>
          <input
            type="text"
            list="history-urls"
            value={targetUrl}
            onChange={(e) => setTargetUrl(e.target.value)}
            placeholder="https://example.com"
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-cyber-500 focus:ring-1 focus:ring-cyber-500 transition-all placeholder:text-slate-600"
          />
          <datalist id="history-urls">
            {history.map((item, idx) => (
              <option key={idx} value={item.url} />
            ))}
          </datalist>
        </div>

        {/* Email Input */}
        <div className="bg-slate-900/50 p-5 rounded-2xl border border-slate-800 group hover:border-cyber-500/30 transition-colors">
          <label className="text-slate-300 font-medium block mb-3 flex items-center gap-2">
            <Mail size={16} /> 通知 Email (選填)
          </label>
          <input
            type="email"
            list="history-emails"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="your@email.com"
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:border-cyber-500 focus:ring-1 focus:ring-cyber-500 transition-all placeholder:text-slate-600"
          />
          <datalist id="history-emails">
            {/*  Ideally we store used emails in history too, but for now reuse URL history purely as a source or empty? 
                      Actually history object doesn't have email. Let's leave empty or implement email history later. 
                 */}
          </datalist>
        </div>
      </div>

      {/* Main Action & History Split */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        {/* Start Action (Takes 2 cols) */}
        <div className="md:col-span-2 flex flex-col gap-4">
          <button
            onClick={handleStartExtraction}
            disabled={loading}
            className="group relative w-full bg-gradient-to-r from-cyber-600 to-blue-600 hover:from-cyber-500 hover:to-blue-500 text-white rounded-2xl p-4 transition-all duration-300 shadow-lg shadow-cyber-900/50 hover:shadow-cyber-500/20 active:scale-[0.99] overflow-hidden disabled:opacity-70 disabled:cursor-not-allowed">
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 group-hover:opacity-30 transition-opacity"></div>
            <div className="relative flex items-center justify-center gap-3">
              <span className="font-bold text-lg tracking-wide">{loading ? '處理中...' : '啟動爬取程序'}</span>
              {!loading && <Play size={20} className="fill-current" />}
            </div>
          </button>

          {/* Status / Output Preview Box */}
          <div className="flex-1 bg-black/40 rounded-2xl border border-slate-800 p-5 font-mono text-sm relative overflow-hidden">
            <div className="absolute top-0 right-0 p-2 opacity-50">
              <Activity size={16} className={`text-emerald-500 ${loading ? 'animate-pulse' : ''}`} />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-slate-500">
                <span>實際時間</span>
                <span className="text-slate-200">{lastTime || '--'}</span>
              </div>
              <div className="flex justify-between text-slate-500">
                <span>當前數量</span>
                <span className="text-slate-200">{lastCount !== null ? `${lastCount} Items` : '--'}</span>
              </div>
              {loading && (
                <div className="w-full bg-slate-800 h-1.5 rounded-full mt-4 overflow-hidden">
                  <div className="bg-cyber-500 h-full w-[0%] animate-[width_2s_ease-in-out_infinite]"></div>
                </div>
              )}
              <div className="mt-4 text-xs text-slate-600">
                {loading ? '> 系統正在擷取中...' : '> 等待指令...'}
              </div>
            </div>
          </div>
        </div>

        {/* History / Recent (Takes 1 col) */}
        <div className="md:col-span-1 bg-slate-900/50 rounded-2xl border border-slate-800 p-5 flex flex-col">
          <div className="flex justify-between items-center mb-4">
            <span className="text-sm font-bold text-slate-400 uppercase tracking-wider">歷史紀錄</span>
            <span className="text-xs text-slate-600 font-mono">最近 {history.length} 筆</span>
          </div>
          <div className="space-y-3 flex-1 overflow-y-auto pr-1 custom-scrollbar max-h-[300px]">
            {history.map((item) => (
              <div
                key={item.id}
                onClick={() => setSelectedHistory(item)}
                className="flex items-center justify-between p-2 rounded hover:bg-slate-800/80 transition-colors cursor-pointer group"
              >
                <div className="flex items-center gap-2 overflow-hidden">
                  <FileText size={14} className={`shrink-0 ${item.status === 'success' ? 'text-emerald-500' : 'text-red-500'}`} />
                  <div className="overflow-hidden">
                    <div className="text-xs text-slate-300 truncate font-medium">{item.summary}</div>
                    <div className="text-[10px] text-slate-500 truncate">{item.url}</div>
                  </div>
                </div>
                <ChevronRight size={12} className="text-slate-700 group-hover:text-slate-400" />
              </div>
            ))}
            {history.length === 0 && (
              <div className="text-center text-slate-600 py-4 text-xs">暫無紀錄</div>
            )}
          </div>
          <button
            onClick={fetchHistory}
            className="mt-3 w-full text-xs text-center text-slate-500 hover:text-slate-300 py-2 border-t border-slate-800"
          >
            重新整理
          </button>
        </div>

      </div>


      {/* Data Modal */}
      {
        selectedHistory && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl">
              <div className="flex justify-between items-center p-4 border-b border-slate-800">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Database size={18} className="text-cyber-400" />
                  擷取資料預覽
                </h3>
                <button
                  onClick={() => setSelectedHistory(null)}
                  className="p-1 hover:bg-slate-800 rounded-full transition-colors"
                >
                  <X size={20} className="text-slate-400" />
                </button>
              </div>
              <div className="p-4 overflow-auto custom-scrollbar flex-1 font-mono text-xs text-slate-300 bg-black/20">
                <pre>{JSON.stringify(JSON.parse(selectedHistory.data_json || '[]'), null, 2)}</pre>
              </div>
              <div className="p-3 border-t border-slate-800 flex justify-end">
                <span className="text-xs text-slate-500">ID: {selectedHistory.id} | {selectedHistory.timestamp}</span>
              </div>
            </div>
          </div>
        )
      }
    </div >
  );
};

export default ManualView;