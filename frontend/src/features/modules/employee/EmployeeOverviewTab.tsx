import React from "react";
import { ActivityIndicator, Text, View } from "react-native";
import {
  Building2,
  CheckCircle2,
  Lock,
  MapPin,
  ShieldAlert,
  UserCheck,
  UserMinus,
  Users,
  UserX,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import type { EmployeeOverviewResponse } from "@/types/employee.types";

interface EmployeeOverviewTabProps {
  overview?: EmployeeOverviewResponse;
  isLoading: boolean;
  onSelectStatusFilter?: (status: string) => void;
}

export const EmployeeOverviewTab: React.FC<EmployeeOverviewTabProps> = ({
  overview,
  isLoading,
}) => {
  if (isLoading || !overview) {
    return (
      <View className="py-12 items-center justify-center">
        <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
        <Text className="text-sm text-slate-400 mt-3 font-medium">Loading workforce metrics...</Text>
      </View>
    );
  }

  const {
    status_counts: sc,
    gender_distribution,
    employment_type_distribution,
    department_distribution,
    top_locations,
    user_account_coverage,
    reporting_coverage,
  } = overview;

  return (
    <View className="gap-4">
      {/* ── Top Headcount Summary Cards ─────────────────────── */}
      <View className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {/* Total Employees */}
        <View className="col-span-2 md:col-span-1 bg-dark-card border border-blue-500/20 rounded-xl p-3.5 shadow-sm">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] uppercase font-bold text-blue-400 tracking-wider">Total Headcount</Text>
            <Users size={14} color={THEME_COLORS.primaryIcon} />
          </View>
          <Text className="text-xl font-black text-white font-mono">{sc.total.toLocaleString()}</Text>
          <Text className="text-[10px] text-slate-400 mt-1">Master table <Text className="font-mono text-slate-300">dbo.EmployeeMst</Text></Text>
        </View>

        {/* Active Valid */}
        <View className="bg-dark-card border border-emerald-500/30 rounded-xl p-3.5 shadow-sm bg-emerald-950/10">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] uppercase font-bold text-emerald-400 tracking-wider">Active Employees</Text>
            <UserCheck size={14} color={THEME_COLORS.success} />
          </View>
          <Text className="text-xl font-black text-emerald-400 font-mono">{sc.active.toLocaleString()}</Text>
          <Text className="text-[10px] text-emerald-400/80 mt-1">
            {((sc.active / (sc.total || 1)) * 100).toFixed(1)}% of master roster
          </Text>
        </View>

        {/* Inactive */}
        <View className="bg-dark-card border border-amber-500/20 rounded-xl p-3.5 shadow-sm">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] uppercase font-bold text-amber-400 tracking-wider">Inactive</Text>
            <UserX size={14} color={THEME_COLORS.warning} />
          </View>
          <Text className="text-xl font-black text-amber-400 font-mono">{sc.inactive.toLocaleString()}</Text>
          <Text className="text-[10px] text-slate-400 mt-1">Deactivated accounts</Text>
        </View>

        {/* Resigned */}
        <View className="bg-dark-card border border-slate-700 rounded-xl p-3.5 shadow-sm">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Resigned / Ex-Staff</Text>
            <UserMinus size={14} color={THEME_COLORS.textMuted} />
          </View>
          <Text className="text-xl font-black text-slate-300 font-mono">{sc.resigned.toLocaleString()}</Text>
          <Text className="text-[10px] text-slate-400 mt-1">Past resignation date</Text>
        </View>

        {/* Soft Deleted */}
        <View className="bg-dark-card border border-rose-500/20 rounded-xl p-3.5 shadow-sm">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] uppercase font-bold text-rose-400 tracking-wider">Soft Deleted</Text>
            <ShieldAlert size={14} color={THEME_COLORS.dangerIcon} />
          </View>
          <Text className="text-xl font-black text-rose-400 font-mono">{sc.deleted.toLocaleString()}</Text>
          <Text className="text-[10px] text-slate-400 mt-1">EmpIsDeleted = 1</Text>
        </View>
      </View>

      {/* ── Active Employee Business Rule Callout ───────────── */}
      <View className="bg-blue-950/20 border border-blue-500/30 rounded-xl p-3.5 flex-row items-center justify-between flex-wrap gap-2">
        <View className="flex-row items-center gap-2">
          <CheckCircle2 size={16} color={THEME_COLORS.primaryIcon} />
          <View>
            <Text className="text-xs font-bold text-white">Canonical Active Employee Rule</Text>
            <Text className="text-[11px] text-blue-200/80 font-mono">
              EmpIsActive = 1 AND EmpIsDeleted = 0 AND (EmpResignDate IS NULL OR EmpResignDate &gt; GETDATE())
            </Text>
          </View>
        </View>
        <View className="bg-blue-600/30 border border-blue-400/40 px-2.5 py-1 rounded-md">
          <Text className="text-xs font-mono font-bold text-blue-300">{sc.active} Active Records Verified</Text>
        </View>
      </View>

      {/* ── Coverage & Integration Metrics ──────────────────── */}
      <View className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* User Account Linkage */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center justify-between mb-2">
            <View className="flex-row items-center gap-2">
              <Lock size={15} color={THEME_COLORS.primaryIcon} />
              <Text className="text-xs font-bold text-white">Authentication &amp; User Account Coverage</Text>
            </View>
            <Text className="text-xs font-mono font-bold text-emerald-400">
              {user_account_coverage.login_coverage_pct}%
            </Text>
          </View>
          <Text className="text-[11px] text-slate-400 mb-3">
            Active employees linked to portal login accounts via <Text className="font-mono text-slate-300">SecurityUserMst.UserEmpID</Text>.
          </Text>
          <View className="h-2 bg-dark-bg rounded-full overflow-hidden mb-2">
            <View
              className="h-full bg-blue-500 rounded-full"
              style={{ width: `${Math.min(user_account_coverage.login_coverage_pct, 100)}%` }}
            />
          </View>
          <View className="flex-row justify-between text-[10px] text-slate-400">
            <Text className="text-[10px] text-slate-400">{user_account_coverage.active_employees_with_login} Employees Linked</Text>
            <Text className="text-[10px] text-slate-400">{user_account_coverage.total_active_logins} Total User Accounts</Text>
          </View>
        </View>

        {/* Manager Reporting Coverage */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center justify-between mb-2">
            <View className="flex-row items-center gap-2">
              <Users size={15} color={THEME_COLORS.primaryIcon} />
              <Text className="text-xs font-bold text-white">Manager Hierarchy Coverage</Text>
            </View>
            <Text className="text-xs font-mono font-bold text-emerald-400">
              {reporting_coverage.manager_coverage_pct}%
            </Text>
          </View>
          <Text className="text-[11px] text-slate-400 mb-3">
            Active employees with configured reporting lines in <Text className="font-mono text-slate-300">EmployeeReportingDet</Text>.
          </Text>
          <View className="h-2 bg-dark-bg rounded-full overflow-hidden mb-2">
            <View
              className="h-full bg-emerald-500 rounded-full"
              style={{ width: `${Math.min(reporting_coverage.manager_coverage_pct, 100)}%` }}
            />
          </View>
          <View className="flex-row justify-between text-[10px] text-slate-400">
            <Text className="text-[10px] text-slate-400">{reporting_coverage.active_employees_with_manager} Employees with Active Manager</Text>
            <Text className="text-[10px] text-slate-400">{sc.active - reporting_coverage.active_employees_with_manager} Unassigned</Text>
          </View>
        </View>
      </View>

      {/* ── Organizational Breakdowns ───────────────────────── */}
      <View className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Department Distribution */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center gap-2 mb-3">
            <Building2 size={15} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-bold text-white">Top Departments</Text>
          </View>
          <View className="gap-2">
            {department_distribution.slice(0, 5).map((dept) => (
              <View key={dept.label} className="gap-1">
                <View className="flex-row justify-between">
                  <Text className="text-[11px] text-slate-300 font-medium truncate max-w-[180px]">{dept.label}</Text>
                  <Text className="text-[11px] font-mono text-slate-400">{dept.count} ({dept.percentage}%)</Text>
                </View>
                <View className="h-1.5 bg-dark-bg rounded-full overflow-hidden">
                  <View className="h-full bg-blue-500 rounded-full" style={{ width: `${dept.percentage}%` }} />
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* Site Locations */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center gap-2 mb-3">
            <MapPin size={15} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-bold text-white">Work Locations / Sites</Text>
          </View>
          <View className="gap-2">
            {top_locations.map((loc) => (
              <View key={loc.label} className="gap-1">
                <View className="flex-row justify-between">
                  <Text className="text-[11px] text-slate-300 font-medium truncate max-w-[180px]">{loc.label}</Text>
                  <Text className="text-[11px] font-mono text-slate-400">{loc.count} ({loc.percentage}%)</Text>
                </View>
                <View className="h-1.5 bg-dark-bg rounded-full overflow-hidden">
                  <View className="h-full bg-indigo-500 rounded-full" style={{ width: `${loc.percentage}%` }} />
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* Gender & Type */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center gap-2 mb-3">
            <Users size={15} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-bold text-white">Employment &amp; Demographics</Text>
          </View>
          <View className="gap-3">
            <View>
              <Text className="text-[10px] uppercase font-bold text-slate-400 mb-1.5">Employment Type</Text>
              <View className="flex-row gap-2">
                {employment_type_distribution.map((type) => (
                  <View key={type.label} className="flex-1 bg-dark-bg border border-dark-border p-2 rounded-lg">
                    <Text className="text-[10px] text-slate-400">{type.label}</Text>
                    <Text className="text-sm font-bold text-white font-mono">{type.count}</Text>
                  </View>
                ))}
              </View>
            </View>

            <View>
              <Text className="text-[10px] uppercase font-bold text-slate-400 mb-1.5">Gender Ratio</Text>
              <View className="flex-row gap-2">
                {gender_distribution.map((gen) => (
                  <View key={gen.label} className="flex-1 bg-dark-bg border border-dark-border p-2 rounded-lg">
                    <Text className="text-[10px] text-slate-400">{gen.label}</Text>
                    <Text className="text-sm font-bold text-white font-mono">{gen.count}</Text>
                  </View>
                ))}
              </View>
            </View>
          </View>
        </View>
      </View>
    </View>
  );
};
