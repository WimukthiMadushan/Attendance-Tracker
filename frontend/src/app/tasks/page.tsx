import { ListTodo, CheckCircle2, Clock, Sparkles } from "lucide-react";
import { fetchTasks, fetchEmployees } from "@/lib/api";

export default async function TasksPage() {
  const tasks = await fetchTasks();
  const employees = await fetchEmployees();
  const employeeMap = new Map(employees.map((e) => [e.id, `${e.first_name} ${e.last_name}`]));

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <ListTodo className="h-6 w-6 text-emerald-400" />
            Daily Tasks Feed
          </h2>
          <p className="text-sm text-muted-foreground mt-0.5">
            Single unified tasks table linked by foreign keys to <code className="text-emerald-400 font-mono">employees</code> and <code className="text-emerald-400 font-mono">attendance_logs</code>
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {tasks.map((task) => (
          <div
            key={task.id}
            className="glass-panel p-5 rounded-2xl border border-border/40 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-emerald-500/30 transition-colors"
          >
            <div className="space-y-2 flex-1">
              <div className="flex items-center gap-3">
                <span className="text-xs font-semibold text-white">
                  {employeeMap.get(task.employee_id) || task.employee_id}
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-secondary text-muted-foreground">
                  {task.date}
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400">
                  {task.category || "General"}
                </span>
              </div>
              <p className="text-sm text-slate-200">{task.description}</p>
              {task.raw_message && (
                <p className="text-[11px] text-muted-foreground font-mono">
                  {task.raw_message}
                </p>
              )}
            </div>

            <div className="flex items-center gap-6 shrink-0 border-t md:border-t-0 md:border-l border-border/30 pt-3 md:pt-0 md:pl-6">
              <div className="text-right">
                <div className="flex items-center gap-1.5 text-xs text-slate-300">
                  <Clock className="h-3.5 w-3.5 text-emerald-400" />
                  <span>{task.duration_minutes || 60} mins</span>
                </div>
                {task.ai_confidence && (
                  <div className="flex items-center gap-1 text-[11px] text-emerald-400 mt-1">
                    <Sparkles className="h-3 w-3" />
                    <span>AI Conf: {(task.ai_confidence * 100).toFixed(0)}%</span>
                  </div>
                )}
              </div>
              <span className="text-[11px] font-bold uppercase px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400">
                {task.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
