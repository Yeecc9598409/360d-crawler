import React, { useState } from 'react';
import { 
  Terminal, 
  Settings, 
  Clock, 
  Mail, 
  Play, 
  Database, 
  Activity, 
  Info,
  Layers,
  Calendar,
  Zap
} from 'lucide-react';
import ManualView from './components/ManualView';
import ScheduleView from './components/ScheduleView';
import HelpPanel from './components/HelpPanel';

enum TabMode {
  MANUAL = 'MANUAL',
  SCHEDULE = 'SCHEDULE'
}

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabMode>(TabMode.MANUAL);

  return (
    <div className="min-h-screen relative overflow-hidden text-slate-200 selection:bg-cyber-500/30">
      
      {/* Background Decor */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
        <div className="absolute top-[-20%] right-[-10%] w-[600px] h-[600px] bg-cyber-500/10 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-20%] left-[-10%] w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[100px]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20" />
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 lg:py-12 h-full flex flex-col">
        
        {/* Header */}
        <header className="mb-10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyber-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyber-500/20">
              <Terminal className="text-white w-7 h-7" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-white">
                360D <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyber-400 to-blue-400">智能爬蟲</span>
              </h1>
              <p className="text-slate-400 text-sm font-mono tracking-wide">自動化數據擷取套件</p>
            </div>
          </div>
          
          <div className="hidden md:flex items-center gap-4 text-sm font-medium text-slate-400">
             <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                <span>系統運作中</span>
             </div>
             <div className="h-4 w-px bg-slate-700"></div>
             <span>v2.4.0</span>
          </div>
        </header>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 flex-1">
          
          {/* Left Column: Controls (Span 8) */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            
            {/* Mode Switcher (Tab Navigation) */}
            <div className="glass-panel p-2 rounded-2xl flex gap-2">
              <button 
                onClick={() => setActiveTab(TabMode.MANUAL)}
                className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-semibold transition-all duration-300 ${
                  activeTab === TabMode.MANUAL 
                    ? 'bg-slate-800 text-white shadow-lg ring-1 ring-white/10' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                <Zap size={18} className={activeTab === TabMode.MANUAL ? 'text-cyber-400' : ''} />
                手動擷取
              </button>
              <button 
                onClick={() => setActiveTab(TabMode.SCHEDULE)}
                className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-semibold transition-all duration-300 ${
                  activeTab === TabMode.SCHEDULE
                    ? 'bg-slate-800 text-white shadow-lg ring-1 ring-white/10' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                <Calendar size={18} className={activeTab === TabMode.SCHEDULE ? 'text-purple-400' : ''} />
                排程任務
              </button>
            </div>

            {/* Dynamic Content Area */}
            <div className="flex-1 relative min-h-[500px]">
              {activeTab === TabMode.MANUAL ? <ManualView /> : <ScheduleView />}
            </div>
          </div>

          {/* Right Column: Help / Info (Span 4) */}
          <div className="lg:col-span-4 h-full">
            <HelpPanel />
          </div>

        </div>
      </div>
    </div>
  );
}

export default App;