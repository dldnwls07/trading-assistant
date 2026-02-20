import { MousePointer2, TrendingUp, Minus, Magnet, Eraser } from 'lucide-react';

const DrawingToolbar = ({ activeTool, onSelectTool, magnetEnabled, onToggleMagnet, onClearAll }) => {
    const tools = [
        { id: 'cursor', icon: MousePointer2, label: 'Cursor' },
        { id: 'trendline', icon: TrendingUp, label: 'Trend Line' },
        { id: 'hline', icon: Minus, label: 'Horz Line' },
        // 향후 추가될 도구들 (현재는 비활성화 또는 플레이스홀더)
        // { id: 'rectangle', icon: Square, label: 'Rectangle' },
        // { id: 'text', icon: Type, label: 'Text' },
        // { id: 'fibure', icon: Scaling, label: 'Fibonacci' },
    ];

    return (
        <div className="absolute left-4 top-16 z-[1001] flex flex-col gap-2">
            <div className="bg-[#09090b]/90 backdrop-blur-md border border-white/10 rounded-2xl p-1.5 shadow-2xl flex flex-col gap-1.5 animate-in slide-in-from-left-2 fade-in duration-300">
                {tools.map((tool) => (
                    <button
                        key={tool.id}
                        onClick={() => onSelectTool(tool.id)}
                        className={`p-2.5 rounded-xl transition-all duration-200 group relative flex items-center justify-center ${activeTool === tool.id
                            ? 'bg-yellow-400 text-black shadow-lg shadow-yellow-400/30 scale-105'
                            : 'text-zinc-500 hover:bg-white/5 hover:text-zinc-100'
                            }`}
                        title={tool.label}
                    >
                        <tool.icon size={20} strokeWidth={activeTool === tool.id ? 2.5 : 2} />

                        {/* Tooltip */}
                        <span className="absolute left-full ml-3 px-2 py-1 bg-slate-900 border border-slate-700 text-slate-200 text-[10px] font-bold rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap shadow-xl z-50">
                            {tool.label}
                        </span>
                    </button>
                ))}

                <div className="w-8 h-px bg-white/10 mx-auto my-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />

                <button
                    onClick={onToggleMagnet}
                    className={`p-2.5 rounded-xl transition-all duration-200 group relative flex items-center justify-center ${magnetEnabled
                        ? 'bg-yellow-400/20 text-yellow-400 border border-yellow-400/30'
                        : 'text-zinc-500 hover:bg-white/5 hover:text-zinc-100'
                        }`}
                    title="Magnet Mode"
                >
                    <Magnet size={20} strokeWidth={magnetEnabled ? 2.5 : 2} />
                    <span className="absolute left-full ml-3 px-2 py-1 bg-[#09090b] border border-white/10 text-zinc-200 text-[10px] font-bold rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap shadow-xl z-50">
                        Magnet Mode {magnetEnabled ? 'ON' : 'OFF'}
                    </span>
                </button>

                <div className="w-8 h-px bg-white/10 mx-auto my-1 bg-gradient-to-r from-transparent via-white/10 to-transparent" />

                <button
                    onClick={onClearAll}
                    className="p-2.5 rounded-xl text-zinc-500 hover:bg-red-500/20 hover:text-red-500 transition-all duration-200 group relative flex items-center justify-center"
                    title="Clear All Drawings"
                >
                    <Eraser size={20} strokeWidth={2} />
                    <span className="absolute left-full ml-3 px-2 py-1 bg-[#09090b] border border-red-900/50 text-red-400 text-[10px] font-bold rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap shadow-xl z-50">
                        Clear All
                    </span>
                </button>
            </div>
        </div>
    );
};

export default DrawingToolbar;
