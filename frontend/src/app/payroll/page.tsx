import { Receipt, DollarSign, Calendar, TrendingUp } from "lucide-react";
import { fetchEmployees, fetchAttendance } from "@/lib/api";

export default async function PayrollPage() {
  const employees = await fetchEmployees();
  const attendance = await fetchAttendance();

  // Aggregate hours by employee
  const hoursMap = new Map<string, number>();
  attendance.forEach((a) => {
    const current = hoursMap.get(a.employee_id) || 0;
    hoursMap.set(a.employee_id, current + (a.total_hours || 0));
  });

  const payrollSummary = employees.map((emp) => {
    const regularHours = Math.min(hoursMap.get(emp.id) || 40, 40);
    const overtimeHours = Math.max((hoursMap.get(emp.id) || 40) - 40, 0);
    const regularPay = regularHours * emp.hourly_rate;
    const overtimePay = overtimeHours * (emp.hourly_rate * 1.5);
    const grossPay = regularPay + overtimePay;
    const deductions = grossPay * 0.05; // 5% standard deductions
    const netPay = grossPay - deductions;

    return {
      emp,
      regularHours,
      overtimeHours,
      grossPay,
      deductions,
      netPay,
    };
  });

  const totalGrossPayout = payrollSummary.reduce((acc, p) => acc + p.grossPay, 0);
  const totalNetPayout = payrollSummary.reduce((acc, p) => acc + p.netPay, 0);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Receipt className="h-6 w-6 text-emerald-400" />
            Payroll Processing Portal
          </h2>
          <p className="text-sm text-muted-foreground mt-0.5">
            Automated payroll calculated directly from unified attendance tracking and hourly rates.
          </p>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-2xl">
          <span className="text-xs text-muted-foreground">Current Payroll Period</span>
          <p className="text-lg font-bold text-white mt-1">October 2026 (Bi-Weekly 1)</p>
          <p className="text-xs text-emerald-400 mt-1">Status: Open / Dynamic</p>
        </div>
        <div className="glass-panel p-5 rounded-2xl">
          <span className="text-xs text-muted-foreground">Total Gross Estimated</span>
          <p className="text-2xl font-bold text-white mt-1">${totalGrossPayout.toFixed(2)}</p>
          <p className="text-xs text-muted-foreground mt-1">Before tax and statutory deductions</p>
        </div>
        <div className="glass-panel p-5 rounded-2xl">
          <span className="text-xs text-muted-foreground">Total Net Payable</span>
          <p className="text-2xl font-bold text-emerald-400 mt-1">${totalNetPayout.toFixed(2)}</p>
          <p className="text-xs text-muted-foreground mt-1">Estimated direct disbursement</p>
        </div>
      </div>

      {/* Payroll Table */}
      <div className="glass-panel rounded-2xl overflow-hidden border border-border/40">
        <div className="p-4 border-b border-border/40 bg-secondary/20 flex items-center justify-between">
          <span className="text-xs font-semibold text-white uppercase tracking-wider">
            Employee Payroll Breakdown
          </span>
          <span className="text-xs text-muted-foreground">
            {payrollSummary.length} employee records
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-secondary/40 text-muted-foreground font-semibold border-b border-border/40">
              <tr>
                <th className="p-4">Employee</th>
                <th className="p-4">Code</th>
                <th className="p-4">Hourly Rate</th>
                <th className="p-4">Regular Hrs</th>
                <th className="p-4">OT Hrs</th>
                <th className="p-4">Gross Pay</th>
                <th className="p-4">Deductions</th>
                <th className="p-4">Net Pay</th>
                <th className="p-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/20 text-slate-300">
              {payrollSummary.map(({ emp, regularHours, overtimeHours, grossPay, deductions, netPay }) => (
                <tr key={emp.id} className="hover:bg-secondary/20 transition-colors">
                  <td className="p-4 font-semibold text-white">
                    {emp.first_name} {emp.last_name}
                  </td>
                  <td className="p-4 font-mono text-muted-foreground">{emp.employee_code}</td>
                  <td className="p-4 font-mono text-emerald-400">${emp.hourly_rate}/hr</td>
                  <td className="p-4 font-mono">{regularHours.toFixed(1)} hrs</td>
                  <td className="p-4 font-mono">{overtimeHours.toFixed(1)} hrs</td>
                  <td className="p-4 font-medium text-white">${grossPay.toFixed(2)}</td>
                  <td className="p-4 text-red-400">-${deductions.toFixed(2)}</td>
                  <td className="p-4 font-bold text-emerald-400">${netPay.toFixed(2)}</td>
                  <td className="p-4">
                    <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/20 text-emerald-400">
                      CALCULATED
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
