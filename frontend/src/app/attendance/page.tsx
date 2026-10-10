import { CalendarCheck, ShieldCheck, Clock } from "lucide-react";
import { fetchAttendance, fetchEmployees } from "@/lib/api";

export default async function AttendancePage() {
  const attendance = await fetchAttendance();
  const employees = await fetchEmployees();

  const employeeMap = new Map(employees.map((e) => [e.id, `${e.first_name} ${e.last_name}`]));
  const phoneMap = new Map(employees.map((e) => [e.id, e.whatsapp_phone]));

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <CalendarCheck className="h-6 w-6 text-emerald-400" />
            Attendance Logs
          </h2>
          <p className="text-sm text-muted-foreground mt-0.5">
            Single unified attendance table with composite key constraint <code className="text-emerald-400 font-mono">@@unique([employee_id, date])</code>
          </p>
        </div>
      </div>

      <div className="glass-panel rounded-2xl overflow-hidden border border-border/40">
        <div className="p-4 border-b border-border/40 flex items-center justify-between bg-secondary/20">
          <span className="text-xs font-semibold text-white uppercase tracking-wider">
            Daily Attendance Records
          </span>
          <span className="text-xs text-muted-foreground">
            {attendance.length} record(s) recorded
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-secondary/40 text-muted-foreground font-semibold border-b border-border/40">
              <tr>
                <th className="p-4">Date</th>
                <th className="p-4">Employee</th>
                <th className="p-4">WhatsApp Phone</th>
                <th className="p-4">Check-in</th>
                <th className="p-4">Check-out</th>
                <th className="p-4">Total Hours</th>
                <th className="p-4">Status</th>
                <th className="p-4">Source</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/20 text-slate-300">
              {attendance.map((log) => (
                <tr key={log.id} className="hover:bg-secondary/20 transition-colors">
                  <td className="p-4 font-mono font-medium text-white">{log.date}</td>
                  <td className="p-4 font-medium text-white">
                    {employeeMap.get(log.employee_id) || log.employee_id}
                  </td>
                  <td className="p-4 font-mono text-emerald-400">
                    {phoneMap.get(log.employee_id) || "N/A"}
                  </td>
                  <td className="p-4 font-mono">
                    {log.check_in_time ? new Date(log.check_in_time).toLocaleTimeString() : "--:--"}
                  </td>
                  <td className="p-4 font-mono">
                    {log.check_out_time ? new Date(log.check_out_time).toLocaleTimeString() : "--:--"}
                  </td>
                  <td className="p-4 font-semibold text-white">
                    {log.total_hours ? `${log.total_hours} hrs` : "In Progress"}
                  </td>
                  <td className="p-4">
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/20 text-emerald-400">
                      {log.status}
                    </span>
                  </td>
                  <td className="p-4 text-muted-foreground">{log.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
