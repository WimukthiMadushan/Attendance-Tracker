"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  CalendarCheck,
  ListTodo,
  Receipt,
  MessageSquare,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigationItems = [
  { name: "Overview", href: "/", icon: LayoutDashboard },
  { name: "Daily Tasks", href: "/tasks", icon: ListTodo },
  { name: "Employees Directory", href: "/employees", icon: Users },
  { name: "Payroll", href: "/payroll", icon: Receipt },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-border/40 glass-panel flex flex-col shrink-0 min-h-screen">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 gap-3 border-b border-border/40">
        <div className="h-9 w-9 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
          <MessageSquare className="h-5 w-5" />
        </div>
        <div>
          <h1 className="font-bold text-sm tracking-tight text-white flex items-center gap-1.5">
            AutoTracker
          </h1>
          <p className="text-[11px] text-muted-foreground font-mono">WhatsApp AI & HR</p>
        </div>
      </div>

      {/* Nav List */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navigationItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-200",
                isActive
                  ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm"
                  : "text-muted-foreground hover:text-white hover:bg-secondary/60"
              )}
            >
              <Icon className={cn("h-4 w-4", isActive ? "text-emerald-400" : "text-muted-foreground")} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* WhatsApp Status Box */}
      <div className="p-4 m-3 rounded-xl bg-card border border-border/50">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">
            Cloud Webhook
          </span>
          <span className="flex h-2 w-2 rounded-full bg-emerald-400 whatsapp-pulse" />
        </div>
        <div className="flex items-center gap-2 text-xs text-white">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span>Idempotency Active</span>
        </div>
        <p className="text-[10px] text-muted-foreground mt-1">E.164 phone verification enabled</p>
      </div>
    </aside>
  );
}
