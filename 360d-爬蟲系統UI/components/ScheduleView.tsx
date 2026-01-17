import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Mail, Power, Repeat, Sliders, CheckCircle2, ToggleLeft, ToggleRight, FileText, Pause, Play, StopCircle } from 'lucide-react';
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

const ScheduleView: React.FC = () => {
  // Removed AI State
  // const [scraperType, setScraperType] = useState<'AI' | 'CSS'>('AI');
  const [frequency, setFrequency] = useState(2); // 0: Daily, 1: Weekly, 2: Custom
  const [customMinutes, setCustomMinutes] = useState(1); // Default to 1 for testing
  const [targetUrl, setTargetUrl] = useState('');
  // const [extractTopic, setExtractTopic] = useState(true);
  // const [extractHint, setExtractHint] = useState('');
  const [email, setEmail] = useState('yeecc9598409@gmail.com');
  const [history, setHistory] = useState<HistoryItem[]>([]);

  // Scheduling state
  const [isScheduled, setIsScheduled] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [scheduleId, setScheduleId] = useState<number | null>(null);
  const [countdownSeconds, setCountdownSeconds] = useState(0);
  const [isContinuous, setIsContinuous] = useState(true); // Default: continuous scheduling

  useEffect(() => {
    fetchHistory();
  }, []);

  // Countdown timer - stops when paused or not scheduled
  useEffect(() => {
    if (!isScheduled || isPaused || countdownSeconds <= 0) return;

    const interval = setInterval(() => {
      setCountdownSeconds(prev => {
        if (prev <= 1) {
          // Countdown finished, reset for next cycle if continuous
          if (isContinuous) {
            let resetSeconds = 0;
            if (frequency === 0) resetSeconds = 24 * 60 * 60;
            else if (frequency === 1) resetSeconds = 7 * 24 * 60 * 60;
            else resetSeconds = customMinutes * 60;
            return resetSeconds;
          } else {
            // One-time schedule - stop counting
            setIsScheduled(false);
            return 0;
          }
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isScheduled, isPaused, countdownSeconds, frequency, customMinutes, isContinuous]);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/history?limit=3`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
      }
    } catch (e) {
      console.error("Failed to fetch history");
    }
  };

  // Format seconds to HH:MM:SS
  const formatCountdown = (totalSeconds: number): string => {
    const hrs = Math.floor(totalSeconds / 3600);
    const mins = Math.floor((totalSeconds % 3600) / 60);
    const secs = totalSeconds % 60;
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSchedule = async () => {
    if (!targetUrl || !email) {
      alert('請輸入 URL 和 Email');
      return;
    }
    // Removed confirm dialog as it can block execution in some browser contexts

    let payload;
    let initialCountdownSeconds = 0;

    if (frequency === 0) {
      // Daily -> 1 day
      payload = { frequency: 1, unit: 'days', email, url: targetUrl, is_continuous: isContinuous };
      initialCountdownSeconds = 24 * 60 * 60; // 24 hours
    } else if (frequency === 1) {
      // Weekly -> 7 days
      payload = { frequency: 7, unit: 'days', email, url: targetUrl, is_continuous: isContinuous };
      initialCountdownSeconds = 7 * 24 * 60 * 60; // 7 days
    } else {
      // Custom -> customMinutes minutes
      const mins = customMinutes || 1; // Fallback to 1 if undefined
      console.log('[DEBUG] Using customMinutes:', mins);
      payload = { frequency: mins, unit: 'minutes', email, url: targetUrl, is_continuous: isContinuous };
      initialCountdownSeconds = mins * 60;
    }

    console.log('[DEBUG] Payload:', payload);
    console.log('[DEBUG] initialCountdownSeconds:', initialCountdownSeconds);

    try {
      const res = await fetch(`${API_BASE_URL}/api/schedule`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        setScheduleId(data.schedule_id);
        setIsScheduled(true);
        setCountdownSeconds(initialCountdownSeconds);
        alert('排程已啟動！');
      } else {
        alert('排程失敗');
      }
    } catch (e) {
      alert('排程失敗 - 連線錯誤');
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

        {/* URL Input */}
        <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 hover:border-purple-500/30 transition-colors">
          <label className="text-slate-300 font-medium block mb-3 flex items-center gap-2">
            <ToggleRight size={16} /> 目標網站 URL
          </label>
          <input
            type="text"
            list="history-urls-schedule"
            value={targetUrl}
            onChange={(e) => setTargetUrl(e.target.value)}
            placeholder="https://example.com"
            disabled={isScheduled}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all placeholder:text-slate-600 disabled:opacity-50"
          />
          <datalist id="history-urls-schedule">
            {history.map((item, idx) => (
              <option key={idx} value={item.url} />
            ))}
          </datalist>
        </div>

        {/* Email Input */}
        <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800 hover:border-purple-500/30 transition-colors">
          <label className="text-slate-300 font-medium block mb-3 flex items-center gap-2">
            <Mail size={16} /> 報告接收信箱
          </label>
          <input
            type="email"
            list="history-emails-schedule"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="reports@example.com"
            disabled={isScheduled}
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all placeholder:text-slate-600 disabled:opacity-50"
          />
          <datalist id="history-emails-schedule">
            {/* Placeholder for email history */}
          </datalist>
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
                  onClick={() => !isScheduled && setFrequency(idx)}
                  disabled={isScheduled}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${frequency === idx
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'text-slate-500 hover:text-slate-300'
                    } disabled:opacity-50`}
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
                    <label className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-1 block">間隔 (分鐘)</label>
                    <input
                      type="range"
                      min="1"
                      max="1440"
                      value={customMinutes}
                      onChange={(e) => setCustomMinutes(Number(e.target.value))}
                      disabled={isScheduled}
                      className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
                    />
                  </div>
                  <input
                    type="number"
                    min="1"
                    max="1440"
                    value={customMinutes}
                    onChange={(e) => {
                      const val = parseInt(e.target.value, 10);
                      if (!isNaN(val) && val >= 1 && val <= 1440) {
                        setCustomMinutes(val);
                      }
                    }}
                    disabled={isScheduled}
                    className="w-20 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-right text-purple-400 font-mono font-bold focus:outline-none focus:border-purple-500 disabled:opacity-50"
                  />
                  <span className="text-slate-500 text-sm">min</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Start Button */}
        <div className="pt-2">
          <button
            onClick={handleSchedule}
            disabled={isScheduled}
            className={`group w-full rounded-2xl p-4 transition-all duration-300 shadow-lg flex items-center justify-between px-8
              ${isScheduled
                ? 'bg-gradient-to-r from-emerald-700 to-teal-700 cursor-not-allowed opacity-90'
                : 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 shadow-purple-900/50 hover:shadow-purple-500/20 active:scale-[0.99]'
              } text-white`}>
            <div className="flex flex-col items-start">
              <span className="font-bold text-lg tracking-wide">
                {isScheduled ? '排程已啟動' : '啟動排程'}
              </span>
              <span className="text-xs text-purple-200/80 font-mono">
                {isScheduled
                  ? `下次執行倒數: ${formatCountdown(countdownSeconds)}`
                  : (
                    <>
                      {frequency === 0 && "下次執行: 明日"}
                      {frequency === 1 && "下次執行: 下週"}
                      {frequency === 2 && `下次執行: ${customMinutes} 分鐘後`}
                    </>
                  )
                }
              </span>
            </div>
            <div className={`h-10 w-10 rounded-full flex items-center justify-center transition-transform duration-500
              ${isScheduled ? 'bg-emerald-500/30' : 'bg-white/20 group-hover:rotate-90'}`}>
              {isScheduled ? <CheckCircle2 size={20} /> : <Power size={20} className="fill-current" />}
            </div>
          </button>

          {/* Stop Button - Only show when scheduled */}
          {isScheduled && (
            <button
              onClick={async () => {
                try {
                  const res = await fetch(`${API_BASE_URL}/api/schedules/stop-all`, {
                    method: 'DELETE'
                  });
                  if (res.ok) {
                    const data = await res.json();
                    setIsScheduled(false);
                    setIsPaused(false);
                    setCountdownSeconds(0);
                    setScheduleId(null);
                    alert(`已停止 ${data.count} 個排程`);
                  } else {
                    alert('停止失敗');
                  }
                } catch (e) {
                  alert('停止失敗 - 連線錯誤');
                }
              }}
              className="mt-2 w-full bg-red-900/50 hover:bg-red-700/60 text-red-200 border border-red-700/50 rounded-xl p-3 flex items-center justify-center gap-2 transition-colors"
            >
              <StopCircle size={18} />
              <span className="font-medium">停止排程</span>
            </button>
          )}
        </div>

        {/* Continuous Scheduling Toggle */}
        <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 flex items-center justify-between">
          <label className="text-slate-300 flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={isContinuous}
              onChange={(e) => setIsContinuous(e.target.checked)}
              disabled={isScheduled}
              className="w-4 h-4 accent-purple-500"
            />
            <span>持續執行 (重複排程)</span>
          </label>
          <span className="text-xs text-slate-500">
            {isContinuous ? '排程將持續循環執行' : '排程執行一次後停止'}
          </span>
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

      </div>
    </div>
  );
};

export default ScheduleView;