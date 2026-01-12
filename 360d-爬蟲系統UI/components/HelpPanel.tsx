import React from 'react';
import { Info, Command, ShieldCheck, Cpu } from 'lucide-react';

const HelpPanel: React.FC = () => {
  return (
    <div className="glass-panel h-full rounded-3xl p-8 flex flex-col border-l border-slate-700/50">
      
      <div className="flex items-center gap-2 mb-8">
        <Info className="text-slate-400" />
        <h3 className="text-xl font-bold text-slate-200">使用說明</h3>
      </div>

      <div className="space-y-8 flex-1 overflow-y-auto custom-scrollbar pr-2">
        
        <div className="group">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-cyber-500/10 flex items-center justify-center text-cyber-400 group-hover:bg-cyber-500 group-hover:text-white transition-colors">
              <Command size={16} />
            </div>
            <h4 className="font-semibold text-slate-200">手動擷取</h4>
          </div>
          <p className="text-slate-400 text-sm leading-relaxed pl-11">
            切換 <strong>智能主題</strong> 以啟用 AI 過濾功能。輸入您的 Email 以接收結構化的 JSON 數據集。點擊啟動後將立即開始執行。
          </p>
        </div>

        <div className="h-px bg-slate-800/50" />

        <div className="group">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400 group-hover:bg-purple-500 group-hover:text-white transition-colors">
              <Cpu size={16} />
            </div>
            <h4 className="font-semibold text-slate-200">排程器</h4>
          </div>
          <p className="text-slate-400 text-sm leading-relaxed pl-11">
            設定週期性爬取任務。低於 1 小時的頻率需要 <strong>Pro 方案</strong> 授權。請確保目標網域允許機器人流量。
          </p>
        </div>

        <div className="h-px bg-slate-800/50" />

        <div className="group">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 group-hover:bg-emerald-500 group-hover:text-white transition-colors">
              <ShieldCheck size={16} />
            </div>
            <h4 className="font-semibold text-slate-200">安全與限制</h4>
          </div>
          <ul className="text-slate-400 text-sm leading-relaxed pl-11 list-disc list-outside ml-4 space-y-1">
            <li>單次會話上限 5,000 頁</li>
            <li>自動遵守 robots.txt 協議</li>
            <li>結果保留 48 小時</li>
          </ul>
        </div>
      </div>
      
      <div className="mt-8 pt-6 border-t border-slate-800 text-center">
        <p className="text-xs text-slate-600 font-mono">
            SYSTEM_ID: <span className="text-slate-400">HK-47-BETA</span>
        </p>
      </div>
    </div>
  );
};

export default HelpPanel;