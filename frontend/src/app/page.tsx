import {
  Users,
  Clock,
  CheckCircle2,
  MessageSquare,
  ShieldCheck,
  Cpu,
  Database,
  ArrowUpRight,
} from "lucide-react";
import Link from "next/link";
import { fetchEmployees, fetchAttendance, fetchTasks } from "@/lib/api";

export default async function DashboardPage() {
  const employees = await fetchEmployees();
  const attendance = await fetchAttendance();
  const tasks = await fetchTasks();

  const activeCount = employees.filter((e) => e.is_active).length;
  const presentCount = attendance.filter((a) => a.status === "PRESENT").length;
  const totalHours = attendance.reduce((acc, curr) => acc + (curr.total_hours || 0), 0);
  const completedTasks = tasks.filter((t) => t.status === "COMPLETED").length;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Page Title & Status */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">HR Executive Dashboard</h2>
          <p className="text-sm text-muted-foreground mt-0.5">
            Real-time telemetry of WhatsApp check-ins, AI parsed task logs, and payroll hours.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/attendance"
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-500 hover:bg-emerald-600 text-slate-950 transition-colors flex items-center gap-1.5 shadow-lg shadow-emerald-500/20"
          >
            <span>View Attendance Matrix</span>
            <ArrowUpRight className="h-4 w-4" />
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Active Employees</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Users className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold text-white">{activeCount}</span>
            <span className="text-xs text-muted-foreground ml-2">Registered</span>
          </div>
          <div className="mt-2 text-[11px] text-emerald-400 flex items-center gap-1">
            <span>Strict E.164 phone verified</span>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Present Today</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <CheckCircle2 className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold text-white">{presentCount}</span>
            <span className="text-xs text-muted-foreground ml-2">checked in</span>
          </div>
          <div className="mt-2 text-[11px] text-emerald-400 flex items-center gap-1">
            <span>Unified [employee_id, date] log</span>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Tracked Hours Today</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Clock className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold text-white">{totalHours.toFixed(1)}h</span>
            <span className="text-xs text-muted-foreground ml-2">accumulated</span>
          </div>
          <div className="mt-2 text-[11px] text-muted-foreground">
            Auto-calculated on clock out
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Tasks Logged</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <MessageSquare className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <span className="text-2xl font-bold text-white">{completedTasks}</span>
            <span className="text-xs text-muted-foreground ml-2">completed</span>
          </div>
          <div className="mt-2 text-[11px] text-emerald-400 flex items-center gap-1">
            <span>Structured JSON Schema parsed</span>
          </div>
        </div>
      </div>

      {/* Architectural Guarantee Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-xl border border-border/60">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Database className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Unified Schema</h3>
              <p className="text-xs text-muted-foreground">Single Relational PostgreSQL</p>
            </div>
          </div>
          <p className="text-xs text-slate-300 mt-3 leading-relaxed">
            Zero per-employee tables. All attendance logs and tasks are joined by foreign keys with composite unique constraints (<code className="text-purple-300 font-mono">@@unique([employeeId, date])</code>).
          </p>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-border/60">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Idempotent Webhook</h3>
              <p className="text-xs text-muted-foreground">Meta Cloud API Guard</p>
            </div>
          </div>
          <p className="text-xs text-slate-300 mt-3 leading-relaxed">
            Guaranteed at-most-once processing using Meta unique <code className="text-emerald-300 font-mono">message_id</code> table deduplication. Webhook network retries will not duplicate entries.
          </p>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-border/60">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <Cpu className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">LLM Structured Parser</h3>
              <p className="text-xs text-muted-foreground">Gemini & OpenAI Schema</p>
            </div>
          </div>
          <p className="text-xs text-slate-300 mt-3 leading-relaxed">
            Natural language messages in WhatsApp are transformed via JSON Schema into explicit clock times, duration estimates, categories, and automated polite reply messages.
          </p>
        </div>
      </div>

      {/* Live Data Grid: Recent Tasks & Employee Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Tasks */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-border/40 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-emerald-400" />
              Live Task Stream (Extracted from WhatsApp)
            </h3>
            <Link href="/tasks" className="text-xs text-emerald-400 hover:underline">
              View All
            </Link>
          </div>
          <div className="space-y-3">
            {tasks.slice(0, 4).map((task) => (
              <div
                key={task.id}
                className="p-3.5 rounded-xl bg-secondary/30 border border-border/40 flex items-start justify-between gap-3"
              >
                <div className="space-y-1">
                  <p className="text-xs font-medium text-white">{task.description}</p>
                  <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                    <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-mono">
                      {task.category || "General"}
                    </span>
                    <span>• {task.duration_minutes || 60} mins</span>
                    {task.ai_confidence && (
                      <span>• AI Confidence: {(task.ai_confidence * 100).toFixed(0)}%</span>
                    )}
                  </div>
                </div>
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 shrink-0">
                  {task.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Registered Employees */}
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-border/40 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Users className="h-4 w-4 text-emerald-400" />
              Unified Employee Registry (E.164 Standards)
            </h3>
            <Link href="/employees" className="text-xs text-emerald-400 hover:underline">
              Manage
            </Link>
          </div>
          <div className="space-y-3">
            {employees.map((emp) => (
              <div
                key={emp.id}
                className="p-3.5 rounded-xl bg-secondary/30 border border-border/40 flex items-center justify-between"
              >
                <div>
                  <p className="text-xs font-semibold text-white">
                    {emp.first_name} {emp.last_name}
                  </p>
                  <p className="text-[11px] font-mono text-emerald-400 mt-0.5">
                    {emp.whatsapp_phone}
                  </p>
                  <p className="text-[10px] text-muted-foreground">{emp.department || "General"}</p>
                </div>
                <div className="text-right">
                  <span className="text-[10px] font-mono px-2 py-1 rounded bg-secondary text-slate-300">
                    {emp.employee_code}
                  </span>
                  <p className="text-[11px] text-muted-foreground mt-1">${emp.hourly_rate}/hr</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
