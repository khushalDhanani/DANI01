import React from "react";
import { ActivityIndicator, Text, View } from "react-native";
import {
  CheckCircle2,
  Coins,
  Database,
  GitBranch,
  Layers,
  Lock,
  Sparkles,
  Users,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import type { EmployeeStructureResponse } from "@/types/employee.types";

interface EmployeeStructureTabProps {
  structure?: EmployeeStructureResponse;
  isLoading: boolean;
}

export const EmployeeStructureTab: React.FC<EmployeeStructureTabProps> = ({
  structure,
  isLoading,
}) => {
  if (isLoading || !structure) {
    return (
      <View className="py-12 items-center justify-center">
        <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
        <Text className="text-sm text-slate-400 mt-3 font-medium">Mapping Employee data graph...</Text>
      </View>
    );
  }

  const { master_table, canonical_key, business_key, tables } = structure;

  return (
    <View className="gap-4">
      {/* ── Master Entity Header Card ──────────────────────── */}
      <View className="bg-gradient-to-r from-blue-950/40 via-dark-card to-dark-card border border-blue-500/30 rounded-xl p-4 shadow-sm">
        <View className="flex-col sm:flex-row sm:items-center justify-between gap-3">
          <View className="flex-1">
            <View className="flex-row items-center gap-2 mb-1">
              <Database size={15} color={THEME_COLORS.primaryIcon} />
              <Text className="text-xs uppercase font-bold text-blue-400 tracking-wider">Canonical Master Table</Text>
            </View>
            <Text className="text-xl md:text-xl font-black text-white font-mono">{master_table}</Text>
            <Text className="text-[11px] text-slate-400 mt-1">
              Primary workforce entity holding personal demographics, contacts, legal identifiers, and employment lifecycle dates.
            </Text>
          </View>

          <View className="flex-row gap-2">
            <View className="bg-dark-bg border border-blue-500/30 px-3 py-2 rounded-lg">
              <Text className="text-[9px] uppercase font-bold text-slate-400">Canonical PK</Text>
              <Text className="text-sm font-mono font-bold text-blue-400">{canonical_key}</Text>
              <Text className="text-[9px] text-slate-500">bigint identity</Text>
            </View>
            <View className="bg-dark-bg border border-slate-700 px-3 py-2 rounded-lg">
              <Text className="text-[9px] uppercase font-bold text-slate-400">Business Key</Text>
              <Text className="text-sm font-mono font-bold text-emerald-400">{business_key}</Text>
              <Text className="text-[9px] text-slate-500">Badge / Code</Text>
            </View>
          </View>
        </View>
      </View>

      {/* ── Interactive Architecture Graph Card ────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4">
        <View className="flex-row items-center justify-between mb-3">
          <View className="flex-row items-center gap-2">
            <GitBranch size={15} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-bold text-white">Employee Relationship Graph</Text>
          </View>
          <View className="flex-row gap-2">
            <View className="flex-row items-center gap-1 bg-emerald-950/40 border border-emerald-800/40 px-2 py-0.5 rounded text-[10px]">
              <CheckCircle2 size={10} color={THEME_COLORS.success} />
              <Text className="text-[10px] font-bold text-emerald-400">Confirmed (11)</Text>
            </View>
            <View className="flex-row items-center gap-1 bg-amber-950/40 border border-amber-800/40 px-2 py-0.5 rounded text-[10px]">
              <Sparkles size={10} color={THEME_COLORS.warning} />
              <Text className="text-[10px] font-bold text-amber-400">Likely (1)</Text>
            </View>
          </View>
        </View>

        {/* Visual Graph Hierarchy */}
        <View className="bg-dark-bg border border-dark-border/80 rounded-xl p-4 gap-3">
          {/* Root Level */}
          <View className="items-center">
            <View className="bg-blue-600 border border-blue-400 px-4 py-2 rounded-lg shadow-md flex-row items-center gap-2">
              <Users size={14} color="#ffffff" />
              <Text className="text-xs font-bold text-white font-mono">dbo.EmployeeMst (Root PK: EmpID)</Text>
            </View>
          </View>

          {/* Sub-branches */}
          <View className="grid grid-cols-1 md:grid-cols-4 gap-3 mt-2">
            {/* Position & Org */}
            <View className="bg-dark-card border border-dark-border p-3 rounded-lg gap-1.5">
              <View className="flex-row items-center gap-1.5 text-blue-400">
                <Layers size={13} color={THEME_COLORS.primaryIcon} />
                <Text className="text-xs font-bold text-white">Position History</Text>
              </View>
              <Text className="text-[11px] font-mono text-slate-300">dbo.EmployeeOfficialDet</Text>
              <View className="text-[10px] text-slate-400 gap-0.5 mt-1 border-t border-dark-border pt-1">
                <Text className="text-[10px] text-slate-400">├── DeptID → OrgDepartmentMst</Text>
                <Text className="text-[10px] text-slate-400">├── DesigID → OrgDesignationMst</Text>
                <Text className="text-[10px] text-slate-400">├── LocID → OrgLocationMst</Text>
                <Text className="text-[10px] text-slate-400">└── EmpGradeID → EmployeeGradeMst</Text>
              </View>
            </View>

            {/* Manager Hierarchy */}
            <View className="bg-dark-card border border-dark-border p-3 rounded-lg gap-1.5">
              <View className="flex-row items-center gap-1.5">
                <Users size={13} color={THEME_COLORS.primaryIcon} />
                <Text className="text-xs font-bold text-white">Reporting Lines</Text>
              </View>
              <Text className="text-[11px] font-mono text-slate-300">dbo.EmployeeReportingDet</Text>
              <View className="text-[10px] text-slate-400 gap-0.5 mt-1 border-t border-dark-border pt-1">
                <Text className="text-[10px] text-slate-400">├── ReportingEmpID → EmployeeMst</Text>
                <Text className="text-[10px] text-slate-400">├── Functional (HOD / Team Lead)</Text>
                <Text className="text-[10px] text-slate-400">└── Administrative (HR Head)</Text>
              </View>
            </View>

            {/* Authentication */}
            <View className="bg-dark-card border border-dark-border p-3 rounded-lg gap-1.5">
              <View className="flex-row items-center gap-1.5">
                <Lock size={13} color={THEME_COLORS.primaryIcon} />
                <Text className="text-xs font-bold text-white">Portal &amp; Security</Text>
              </View>
              <Text className="text-[11px] font-mono text-slate-300">dbo.SecurityUserMst</Text>
              <View className="text-[10px] text-slate-400 gap-0.5 mt-1 border-t border-dark-border pt-1">
                <Text className="text-[10px] text-slate-400">├── UserEmpID → EmployeeMst</Text>
                <Text className="text-[10px] text-slate-400">├── RoleID → SecurityRoleMst</Text>
                <Text className="text-[10px] text-slate-400">└── UserADID (Azure AD / SSO)</Text>
              </View>
            </View>

            {/* Time & Payroll */}
            <View className="bg-dark-card border border-dark-border p-3 rounded-lg gap-1.5">
              <View className="flex-row items-center gap-1.5">
                <Coins size={13} color={THEME_COLORS.primaryIcon} />
                <Text className="text-xs font-bold text-white">Operations &amp; Payroll</Text>
              </View>
              <Text className="text-[11px] font-mono text-slate-300">Attendance &amp; Salary</Text>
              <View className="text-[10px] text-slate-400 gap-0.5 mt-1 border-t border-dark-border pt-1">
                <Text className="text-[10px] text-slate-400">├── EmployeeAttendance (829k)</Text>
                <Text className="text-[10px] text-slate-400">├── PayLogEarnedSalary (3.2M)</Text>
                <Text className="text-[10px] text-slate-400">└── PayMonthlyLeaveBalance (86k)</Text>
              </View>
            </View>
          </View>
        </View>
      </View>

      {/* ── Table Nodes Catalog ─────────────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4">
        <View className="flex-row items-center gap-2 mb-3">
          <Layers size={15} color={THEME_COLORS.primaryIcon} />
          <Text className="text-xs font-bold text-white">Registered Tables in Employee Domain ({tables.length})</Text>
        </View>

        <View className="gap-2">
          {tables.map((t) => (
            <View
              key={t.table}
              className="bg-dark-bg border border-dark-border p-3 rounded-lg flex-col sm:flex-row sm:items-center justify-between gap-2"
            >
              <View className="flex-1">
                <View className="flex-row items-center gap-2 mb-0.5">
                  <Text className="text-xs font-bold text-white font-mono">{t.schema}.{t.table}</Text>
                  <View className="bg-slate-800 px-1.5 py-0.5 rounded text-[9px]">
                    <Text className="text-[9px] font-mono font-bold text-slate-300">{t.role}</Text>
                  </View>
                  <View className="bg-emerald-950 border border-emerald-800 px-1.5 py-0.5 rounded">
                    <Text className="text-[9px] font-bold text-emerald-400">{t.confidence}</Text>
                  </View>
                </View>
                <Text className="text-[11px] text-slate-400">{t.description}</Text>
              </View>

              <View className="flex-row items-center gap-3 self-end sm:self-center">
                <View className="items-end">
                  <Text className="text-xs font-mono font-bold text-white">{t.row_count.toLocaleString()}</Text>
                  <Text className="text-[9px] text-slate-400">rows</Text>
                </View>
                <View className="bg-slate-900 border border-slate-700 px-2 py-1 rounded">
                  <Text className="text-[10px] font-mono text-slate-300">Key: {t.key_column}</Text>
                </View>
              </View>
            </View>
          ))}
        </View>
      </View>
    </View>
  );
};
