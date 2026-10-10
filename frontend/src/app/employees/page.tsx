import { Users, Phone, Mail, DollarSign, Plus } from "lucide-react";
import { fetchEmployees } from "@/lib/api";

export default async function EmployeesPage() {
  const employees = await fetchEmployees();

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Users className="h-6 w-6 text-emerald-400" />
            Employees Directory
          </h2>
          <p className="text-sm text-muted-foreground mt-0.5">
            Single unified employee table with strict E.164 WhatsApp numbers (<code className="text-emerald-400 font-mono">^\+[1-9]\d&#123;1,14&#125;$</code>)
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {employees.map((emp) => (
          <div
            key={emp.id}
            className="glass-panel p-5 rounded-2xl border border-border/40 space-y-4 hover:border-emerald-500/40 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-secondary text-slate-300">
                  {emp.employee_code}
                </span>
                <h3 className="text-base font-bold text-white mt-2">
                  {emp.first_name} {emp.last_name}
                </h3>
                <p className="text-xs text-muted-foreground">{emp.department || "General Department"}</p>
              </div>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                  emp.is_active ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
                }`}
              >
                {emp.is_active ? "ACTIVE" : "INACTIVE"}
              </span>
            </div>

            <div className="space-y-2 text-xs pt-2 border-t border-border/30">
              <div className="flex items-center gap-2 text-emerald-400 font-mono">
                <Phone className="h-3.5 w-3.5" />
                <span>{emp.whatsapp_phone}</span>
              </div>
              {emp.email && (
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Mail className="h-3.5 w-3.5" />
                  <span>{emp.email}</span>
                </div>
              )}
              <div className="flex items-center gap-2 text-slate-300">
                <DollarSign className="h-3.5 w-3.5 text-emerald-400" />
                <span>${emp.hourly_rate} / hour</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
