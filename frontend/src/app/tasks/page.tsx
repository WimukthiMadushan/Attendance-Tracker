import { ListTodo, CheckCircle2, Clock, Sparkles } from "lucide-react";
import { fetchTasks, fetchEmployees } from "@/lib/api";

export default async function TasksPage() {
  const tasks = await fetchTasks();
  const employees = await fetchEmployees();
  const employeeMap = new Map(employees.map((e) => [e.id, e.full_name || e.employee_code]));

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <ListTodo className="h-6 w-6 text-emerald-400" />
            Daily Tasks Feed
          </h2>
          <p className="text-sm text-muted-foreground mt-0.5">
            Single unified task items table linked by foreign key to <code className="text-emerald-400 font-mono">employees</code>
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {tasks.map((task: any) => (
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
                  {task.created_at ? new Date(task.created_at).toLocaleDateString() : "Today"}
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400">
                  Task Item
                </span>
              </div>
              <p className="text-sm text-slate-200">
                {task.task_description || task.description}
              </p>
            </div>

            <div className="flex items-center gap-6 shrink-0 border-t md:border-t-0 md:border-l border-border/30 pt-3 md:pt-0 md:pl-6">
              <span className="text-[11px] font-bold uppercase px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400">
                LOGGED
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
