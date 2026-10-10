import { Bell, Sparkles } from "lucide-react";

export function Navbar() {
  return (
    <header className="h-16 border-b border-border/40 glass-panel px-8 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-3">
        <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium flex items-center gap-1.5">
          <Sparkles className="h-3 w-3" />
          Single Relational Schema Engine
        </span>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/50 px-3 py-1.5 rounded-lg border border-border/40">
          <span>API:</span>
          <span className="text-emerald-400 font-mono">FastAPI :8000</span>
        </div>

        <button className="h-8 w-8 rounded-lg border border-border/50 bg-secondary/40 flex items-center justify-center text-muted-foreground hover:text-white transition-colors">
          <Bell className="h-4 w-4" />
        </button>

        <div className="flex items-center gap-2 pl-2 border-l border-border/40">
          <div className="h-8 w-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 font-bold text-xs">
            HR
          </div>
          <div className="text-left text-xs leading-tight">
            <p className="font-semibold text-white">HR Admin</p>
            <p className="text-[10px] text-muted-foreground">Admin Portal</p>
          </div>
        </div>
      </div>
    </header>
  );
}
