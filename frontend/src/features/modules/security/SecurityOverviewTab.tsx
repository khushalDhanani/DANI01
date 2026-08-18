import React from "react";
import {
  ActivityIndicator,
  Text,
  View,
} from "react-native";
import {
  AlertTriangle,
  CheckCircle2,
  KeyRound,
  Lock,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Smartphone,
  UserCheck,
  Users,
  UserX,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import { useSecurityOverview } from "@/hooks/useSecurity";

export function SecurityOverviewTab() {
  const { data: overview, isLoading, isError } = useSecurityOverview();

  if (isLoading) {
    return (
      <View className="py-8 items-center justify-center">
        <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
        <Text className="text-sm text-slate-400 mt-3 font-medium">Loading user & security intelligence...</Text>
      </View>
    );
  }

  if (isError || !overview) {
    return (
      <View className="py-8 items-center justify-center">
        <AlertTriangle size={36} color={THEME_COLORS.dangerIcon} />
        <Text className="text-sm text-red-400 mt-3 font-medium">Failed to load security overview metrics.</Text>
      </View>
    );
  }

  const { account_metrics: acc, employee_link_metrics: link, posture_metrics: posture, role_distribution: roles } = overview;

  return (
    <View className="gap-4">
      {/* Top Banner */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-3 mb-4 flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <View className="flex-row items-center gap-4 flex-1">
          <View className="w-12 h-12 rounded-xl bg-purple-950/80 border border-purple-800/60 items-center justify-center">
            <ShieldCheck size={24} color="#a855f7" />
          </View>
          <View className="flex-1">
            <Text className="text-base font-bold text-white mb-1">User & Security Access Intelligence</Text>
            <Text className="text-xs text-slate-400 leading-relaxed">
              RBAC access auditing for {acc.total_user_accounts.toLocaleString()} user accounts and {link.total_active_employees.toLocaleString()} active employees across Roles, Permissions, Multi-Factor Auth, and Registered Devices.
            </Text>
          </View>
        </View>
        <View className="bg-dark-bg border border-dark-border rounded-xl px-5 py-2.5 items-center self-start md:self-auto">
          <Text className="text-xl font-bold text-purple-400">{acc.active_users}</Text>
          <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Active Users</Text>
        </View>
      </View>

      {/* SECTION 1: ACCOUNT & AUTHENTICATION OVERVIEW */}
      <View className="mb-4">
        <View className="flex-row items-center gap-2 mb-3">
          <Lock size={16} color="#a855f7" />
          <Text className="text-sm font-bold text-white uppercase tracking-wider">Account & Authentication Posture</Text>
        </View>

        <View className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Active Users */}
          <View className="bg-dark-card border border-dark-border rounded-xl p-4">
            <View className="flex-row items-center justify-between mb-2">
              <Text className="text-xs font-semibold text-slate-400">Active Accounts</Text>
              <UserCheck size={16} color={THEME_COLORS.successIcon} />
            </View>
            <Text className="text-xl font-bold text-emerald-400">{acc.active_users.toLocaleString()}</Text>
            <Text className="text-[11px] text-slate-400 mt-1">
              {acc.active_users_pct}% of total {acc.total_user_accounts.toLocaleString()} accounts
            </Text>
          </View>

          {/* Inactive Accounts */}
          <View className="bg-dark-card border border-dark-border rounded-xl p-4">
            <View className="flex-row items-center justify-between mb-2">
              <Text className="text-xs font-semibold text-slate-400">Inactive Accounts</Text>
              <UserX size={16} color={THEME_COLORS.warningIcon} />
            </View>
            <Text className="text-xl font-bold text-amber-400">{acc.inactive_users.toLocaleString()}</Text>
            <Text className="text-[11px] text-slate-400 mt-1">
              {acc.inactive_users_pct}% disabled logins
            </Text>
          </View>

          {/* Deleted Accounts */}
          <View className="bg-dark-card border border-dark-border rounded-xl p-4">
            <View className="flex-row items-center justify-between mb-2">
              <Text className="text-xs font-semibold text-slate-400">Deleted Logins</Text>
              <ShieldAlert size={16} color={THEME_COLORS.dangerIcon} />
            </View>
            <Text className="text-xl font-bold text-red-400">{acc.deleted_users.toLocaleString()}</Text>
            <Text className="text-[11px] text-slate-400 mt-1">
              {acc.deleted_users_pct}% marked deleted in DB
            </Text>
          </View>

          {/* Master Admin Accounts */}
          <View className="bg-dark-card border border-dark-border rounded-xl p-4">
            <View className="flex-row items-center justify-between mb-2">
              <Text className="text-xs font-semibold text-slate-400">Privileged Super Admins</Text>
              <KeyRound size={16} color="#f59e0b" />
            </View>
            <Text className="text-xl font-bold text-amber-400">{posture.master_admins_count}</Text>
            <Text className="text-[11px] text-slate-400 mt-1">
              Elevated Master Admin privileges
            </Text>
          </View>
        </View>

        {/* Posture Bar (MFA, Mobile, Devices) */}
        <View className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
          <View className="bg-dark-card/60 border border-dark-border rounded-xl p-3.5 flex-row items-center justify-between">
            <View className="flex-row items-center gap-3">
              <ShieldCheck size={20} color={THEME_COLORS.primaryIcon} />
              <View>
                <Text className="text-xs font-bold text-white">MFA Protected Logins</Text>
                <Text className="text-[11px] text-slate-400">Multi-Factor Authentication enabled</Text>
              </View>
            </View>
            <Text className="text-base font-bold text-blue-400">{posture.mfa_enabled_count}</Text>
          </View>

          <View className="bg-dark-card/60 border border-dark-border rounded-xl p-3.5 flex-row items-center justify-between">
            <View className="flex-row items-center gap-3">
              <Smartphone size={20} color="#a855f7" />
              <View>
                <Text className="text-xs font-bold text-white">Mobile App Users</Text>
                <Text className="text-[11px] text-slate-400">iOS & Android self-service mobile</Text>
              </View>
            </View>
            <Text className="text-base font-bold text-purple-400">{posture.mobile_app_users_count.toLocaleString()}</Text>
          </View>

          <View className="bg-dark-card/60 border border-dark-border rounded-xl p-3.5 flex-row items-center justify-between">
            <View className="flex-row items-center gap-3">
              <Shield size={20} color="#10b981" />
              <View>
                <Text className="text-xs font-bold text-white">Registered User Devices</Text>
                <Text className="text-[11px] text-slate-400">Bound devices in SecurityUserDevice</Text>
              </View>
            </View>
            <Text className="text-base font-bold text-emerald-400">{posture.total_registered_devices.toLocaleString()}</Text>
          </View>
        </View>
      </View>

      {/* SECTION 2: EMPLOYEE LINKAGE & WORKFORCE ROSTER */}
      <View className="mb-4">
        <View className="flex-row items-center gap-2 mb-3">
          <Users size={16} color="#3b82f6" />
          <Text className="text-sm font-bold text-white uppercase tracking-wider">Employee ↔ User Account Linkage</Text>
        </View>

        <View className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Active Employees with Login */}
          <View className="bg-dark-card border border-dark-border rounded-xl p-4">
            <View className="flex-row items-center justify-between mb-2">
              <Text className="text-xs font-semibold text-slate-400">Staff with Login</Text>
              <CheckCircle2 size={16} color={THEME_COLORS.successIcon} />
            </View>
            <Text className="text-xl font-bold text-emerald-400">{link.active_emps_with_active_user.toLocaleString()}</Text>
            <Text className="text-[11px] text-slate-400 mt-1">
              {link.active_emps_with_active_user_pct}% of {link.total_active_employees.toLocaleString()} active staff
            </Text>
          </View>

          {/* Active Employees without Login */}
          <View className="bg-dark-card border border-dark-border rounded-xl p-4">
            <View className="flex-row items-center justify-between mb-2">
              <Text className="text-xs font-semibold text-slate-400">Staff Without Login</Text>
              <UserX size={16} color="#64748b" />
            </View>
            <Text className="text-xl font-bold text-slate-300">{link.active_emps_without_active_user}</Text>
            <Text className="text-[11px] text-slate-400 mt-1">
              {link.active_emps_without_active_user_pct}% non-portal manufacturing/field
            </Text>
          </View>

          {/* External / Unlinked User Accounts */}
          <View className="bg-dark-card border border-dark-border rounded-xl p-4">
            <View className="flex-row items-center justify-between mb-2">
              <Text className="text-xs font-semibold text-slate-400">External & Service Accounts</Text>
              <Users size={16} color="#38bdf8" />
            </View>
            <Text className="text-xl font-bold text-cyan-400">{acc.unlinked_users.toLocaleString()}</Text>
            <Text className="text-[11px] text-slate-400 mt-1">
              {acc.unlinked_users_pct}% Candidates, Consultancies & Vendors
            </Text>
          </View>
        </View>
      </View>

      {/* SECTION 3: ROLE DISTRIBUTION */}
      <View className="mb-4">
        <View className="flex-row items-center gap-2 mb-3">
          <KeyRound size={16} color="#f59e0b" />
          <Text className="text-sm font-bold text-white uppercase tracking-wider">Role & Access Level Distribution</Text>
        </View>

        <View className="bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="space-y-4">
            {roles.map((r) => (
              <View key={r.role_id} className="mb-3">
                <View className="flex-row items-center justify-between mb-1">
                  <View className="flex-row items-center gap-2">
                    <Text className="text-xs font-bold text-white">{r.role_desc}</Text>
                    <Text className="text-[10px] text-slate-500 font-mono">Role #{r.role_id}</Text>
                  </View>
                  <Text className="text-xs font-semibold text-purple-400">
                    {r.active_users.toLocaleString()} active ({r.percentage}%)
                  </Text>
                </View>
                {/* Progress bar */}
                <View className="h-2 w-full bg-dark-bg rounded-full overflow-hidden">
                  <View
                    className="h-full bg-purple-500 rounded-full"
                    style={{ width: `${Math.max(2, Math.min(100, r.percentage))}%` }}
                  />
                </View>
              </View>
            ))}
          </View>
        </View>
      </View>
    </View>
  );
}
