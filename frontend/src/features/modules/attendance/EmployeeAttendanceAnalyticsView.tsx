import React from "react";
import { ActivityIndicator, Pressable, ScrollView, Text, View } from "react-native";
import { useRouter } from "expo-router";
import {
  AlertTriangle,
  ArrowLeft,
  Briefcase,
  Calendar,
  Clock,
  FileText,
  MapPin,
  ShieldAlert,
  UserCheck,
  UserX,
  Users,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import { useEmployeeLifetimeAnalytics } from "@/hooks/useAttendance";
import { AttendanceDirectoryTab } from "./AttendanceDirectoryTab";

interface EmployeeAttendanceAnalyticsViewProps {
  empId: number;
}

export function EmployeeAttendanceAnalyticsView({ empId }: EmployeeAttendanceAnalyticsViewProps) {
  const router = useRouter();
  const { data: analytics, isLoading, error } = useEmployeeLifetimeAnalytics(empId);

  return (
    <ScrollView className="flex-1 bg-dark-bg p-4 md:p-4" showsVerticalScrollIndicator={false}>
      {/* ── Header Navigation & Breadcrumb ── */}
      <View className="flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
        <View className="flex-1">
          <Pressable
            onPress={() => (router.canGoBack() ? router.back() : router.push("/modules/attendance"))}
            className="flex-row items-center gap-2 mb-3 self-start px-3 py-1.5 rounded-xl bg-dark-card border border-dark-border hover:bg-slate-800"
          >

            <ArrowLeft size={16} color="#a855f7" />
            <Text className="text-xs font-bold text-purple-300">Back</Text>
          </Pressable>

          <View className="flex-row items-center gap-2 mb-1 flex-wrap">
            <View className="bg-purple-950/80 border border-purple-800/60 px-2 py-0.5 rounded">
              <Text className="text-[10px] font-mono font-bold text-purple-400">
                {analytics?.emp_code || `EMP-${empId}`}
              </Text>
            </View>
            <Text className="text-xs uppercase font-bold text-slate-400 tracking-wider">
              Employee 360 Lifetime Attendance & Leave Intelligence
            </Text>
          </View>

          <Text className="text-xl md:text-xl font-black text-white">
            {analytics?.emp_name || `Employee #${empId}`}
          </Text>

          <View className="flex-row items-center gap-4 mt-2 flex-wrap text-xs text-slate-400">
            <View className="flex-row items-center gap-1">
              <Briefcase size={13} color="#a855f7" />
              <Text className="text-xs text-slate-300">{analytics?.dept_name || "Unassigned Dept"}</Text>
            </View>
            <View className="flex-row items-center gap-1">
              <MapPin size={13} color="#a855f7" />
              <Text className="text-xs text-slate-300">{analytics?.loc_name || "Corporate Location"}</Text>
            </View>
            <View className="flex-row items-center gap-1">
              <Calendar size={13} color="#a855f7" />
              <Text className="text-xs text-slate-300">
                Joined: {analytics?.join_date || "N/A"} ({analytics?.tenure_label || "N/A"})
              </Text>
            </View>
            <View
              className={`px-2 py-0.5 rounded border ${
                analytics?.is_active
                  ? "bg-emerald-950/80 border-emerald-800/60"
                  : "bg-rose-950/80 border-rose-800/60"
              }`}
            >
              <Text
                className={`text-[10px] font-bold ${
                  analytics?.is_active ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {analytics?.is_active ? "ACTIVE EMPLOYEE" : "INACTIVE / LEFT"}
              </Text>
            </View>
          </View>
        </View>
      </View>

      {/* ── Content View ── */}
      {isLoading ? (
        <View className="py-20 items-center justify-center">
          <ActivityIndicator size="large" color="#a855f7" />
          <Text className="text-xs text-slate-400 mt-3 font-medium">
            Loading Employee #{empId} lifetime analytics...
          </Text>
        </View>
      ) : error || !analytics ? (
        <View className="py-8 items-center justify-center bg-dark-card border border-dark-border rounded-xl p-4">
          <AlertTriangle size={32} color={THEME_COLORS.danger} />
          <Text className="text-sm font-semibold text-slate-300 mt-2">
            Failed to load Employee #{empId} analytics.
          </Text>
        </View>
      ) : (
        <View className="gap-4 w-full">
          {/* ── Data Quality & HR Risk Signals Banner ── */}
          {analytics.risk_signals.length > 0 && (
            <View className="bg-amber-950/30 border border-amber-800/60 rounded-xl p-4 flex-col gap-2">
              <View className="flex-row items-center gap-2">
                <ShieldAlert size={18} color="#fbbf24" />
                <Text className="text-xs font-bold text-amber-300 uppercase tracking-wider">
                  HR Data Quality & Risk Exception Signals ({analytics.risk_signals.length})
                </Text>
              </View>
              <View className="flex-row items-center gap-2 flex-wrap">
                {analytics.risk_signals.map((sig, idx) => (
                  <View key={idx} className="bg-amber-900/60 border border-amber-700/60 px-2.5 py-1 rounded-lg">
                    <Text className="text-xs font-semibold text-amber-200">⚠️ {sig}</Text>
                  </View>
                ))}
              </View>
            </View>
          )}

          {/* ── Lifetime Summary KPI Cards Grid ── */}
          <View className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Total Attendance Logs
                </Text>
                <View className="p-1.5 rounded-lg bg-purple-950/80 border border-purple-800/60">
                  <Users size={14} color="#c084fc" />
                </View>
              </View>
              <Text className="text-xl font-black text-white">
                {analytics.total_attendance_records.toLocaleString()}
              </Text>
              <Text className="text-[10px] text-purple-300 mt-1 font-mono">
                {analytics.tenure_days} days tenure
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Present Days
                </Text>
                <View className="p-1.5 rounded-lg bg-emerald-950/80 border border-emerald-800/60">
                  <UserCheck size={14} color="#34d399" />
                </View>
              </View>
              <Text className="text-xl font-black text-emerald-400">{analytics.present_pct}%</Text>
              <Text className="text-[10px] text-emerald-400/80 mt-1 font-mono">
                {analytics.present_days.toLocaleString()} present
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Absence Days
                </Text>
                <View className="p-1.5 rounded-lg bg-rose-950/80 border border-rose-800/60">
                  <UserX size={14} color="#f87171" />
                </View>
              </View>
              <Text className="text-xl font-black text-rose-400">{analytics.absent_pct}%</Text>
              <Text className="text-[10px] text-rose-400/80 mt-1 font-mono">
                {analytics.absent_days.toLocaleString()} absent
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Late Arrivals
                </Text>
                <View className="p-1.5 rounded-lg bg-amber-950/80 border border-amber-800/60">
                  <Clock size={14} color="#fbbf24" />
                </View>
              </View>
              <Text className="text-xl font-black text-amber-400">
                {analytics.late_arrivals_count}
              </Text>
              <Text className="text-[10px] text-amber-400/80 mt-1 font-mono">
                {analytics.total_late_mins.toLocaleString()} mins total late
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Overtime Hours
                </Text>
                <View className="p-1.5 rounded-lg bg-sky-950/80 border border-sky-800/60">
                  <Clock size={14} color="#38bdf8" />
                </View>
              </View>
              <Text className="text-xl font-black text-sky-400 font-mono">
                {analytics.total_ot_hours.toLocaleString()} h
              </Text>
              <Text className="text-[10px] text-sky-400/80 mt-1 font-mono">
                {analytics.overtime_records_count} OT shifts
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Manual SAL Credits
                </Text>
                <View className="p-1.5 rounded-lg bg-purple-950/80 border border-purple-800/60">
                  <FileText size={14} color="#c084fc" />
                </View>
              </View>
              <Text className="text-xl font-black text-purple-300">
                {analytics.unpunched_salary_days}
              </Text>
              <Text className="text-[10px] text-slate-400 mt-1 font-mono">
                Unpunched salary days
              </Text>
            </View>

            <View className="bg-dark-card border border-red-900/60 p-4 rounded-xl bg-red-950/20">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-[10px] font-bold uppercase tracking-wider text-red-300">
                  Unexcused Absence
                </Text>
                <View className="p-1.5 rounded-lg bg-red-950/90 border border-red-700/60">
                  <AlertTriangle size={14} color="#ef4444" />
                </View>
              </View>
              <Text className="text-xl font-black text-red-400">
                {analytics.unauthorized_absence_days}
              </Text>
              <Text className="text-[10px] text-red-300/80 mt-1 font-mono">
                {analytics.leave_covered_absence_days} covered by leave request
              </Text>
            </View>
          </View>


          {/* ── Lifetime Leaves Breakdown Table ── */}
          <View className="bg-dark-card border border-dark-border rounded-xl p-3">
            <Text className="text-base font-bold text-white mb-3">
              Lifetime Approved Leaves Breakdown ({analytics.leaves_breakdown.reduce((acc, l) => acc + l.total_days_taken, 0)} Total Days)
            </Text>
            {analytics.leaves_breakdown.length === 0 ? (
              <Text className="text-xs text-slate-500 py-3 italic">
                No recorded leave applications for this employee.
              </Text>
            ) : (
              <View className="border border-dark-border rounded-xl overflow-hidden">
                <View className="flex-row items-center bg-dark-bg/80 px-4 py-2.5 border-b border-dark-border">
                  <Text className="flex-1 text-xs font-bold text-slate-400 uppercase">Leave Category / Scheme</Text>
                  <Text className="w-32 text-xs font-bold text-slate-400 uppercase text-right">Approved Requests</Text>
                  <Text className="w-32 text-xs font-bold text-slate-400 uppercase text-right">Total Days Taken</Text>
                </View>

                {analytics.leaves_breakdown.map((l, idx) => (
                  <View key={idx} className="flex-row items-center px-4 py-3 border-b border-dark-border/60">
                    <Text className="flex-1 text-xs font-bold text-white">{l.leave_type}</Text>
                    <Text className="w-32 text-xs font-mono text-purple-300 text-right">{l.request_count}</Text>
                    <Text className="w-32 text-xs font-mono text-emerald-400 font-bold text-right">
                      {l.total_days_taken} days
                    </Text>
                  </View>
                ))}
              </View>
            )}
          </View>

          {/* ── Employee Punch Log History ── */}
          <View className="gap-3">
            <Text className="text-base font-bold text-white">
              Employee Daily Biometric Punch History Logs ({analytics.emp_name})
            </Text>
            <AttendanceDirectoryTab empId={empId} />
          </View>

        </View>
      )}
    </ScrollView>
  );
}
