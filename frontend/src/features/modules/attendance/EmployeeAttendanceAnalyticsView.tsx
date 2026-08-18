import React from "react";
import { ActivityIndicator, Pressable, ScrollView, Text, View } from "react-native";
import { useRouter } from "expo-router";
import {
  AlertTriangle,
  ArrowLeft,
  Briefcase,
  Calendar,
  CalendarCheck,
  Clock,
  FileText,
  HelpCircle,
  Info,
  MapPin,
  PieChart,
  TrendingUp,
  UserCheck,
  UserX,
  Users,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import { useEmployeeLifetimeAnalytics } from "@/hooks/useAttendance";
import { AttendanceDirectoryTab } from "./AttendanceDirectoryTab";
import { formatDate } from "@/utils/formatters";

interface EmployeeAttendanceAnalyticsViewProps {
  empId: number;
}

export function EmployeeAttendanceAnalyticsView({ empId }: EmployeeAttendanceAnalyticsViewProps) {
  const router = useRouter();
  const { data: analytics, isLoading, error } = useEmployeeLifetimeAnalytics(empId);

  return (
    <ScrollView className="flex-1 bg-dark-bg p-3 md:p-3" showsVerticalScrollIndicator={false}>
      {/* ── Compact Header Navigation & Profile Banner ── */}
      <View className="bg-dark-card border border-dark-border p-3 rounded-xl mb-3 flex-col md:flex-row md:items-center justify-between gap-3 shadow-sm">
        <View className="flex-1">
          <View className="flex-row items-center gap-2 mb-1 flex-wrap">
            <Pressable
              onPress={() => (router.canGoBack() ? router.back() : router.push("/modules/attendance"))}
              className="flex-row items-center gap-1.5 px-2.5 py-1 rounded-lg bg-dark-bg border border-dark-border hover:bg-slate-800"
            >
              <ArrowLeft size={13} color="#a855f7" />
              <Text className="text-[11px] font-bold text-purple-300">Back</Text>
            </Pressable>

            <View className="bg-purple-950/80 border border-purple-800/60 px-2 py-0.5 rounded">
              <Text className="text-[10px] font-mono font-bold text-purple-400">
                {analytics?.emp_code || `EMP-${empId}`}
              </Text>
            </View>
            <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
              360 Attendance Intelligence
            </Text>
          </View>

          <Text className="text-lg md:text-xl font-extrabold text-white">
            {analytics?.emp_name || `Employee #${empId}`}
          </Text>

          <View className="flex-row items-center gap-3 mt-1.5 flex-wrap text-xs text-slate-400">
            <View className="flex-row items-center gap-1">
              <Briefcase size={12} color="#a855f7" />
              <Text className="text-xs text-slate-300">{analytics?.dept_name || "Unassigned Dept"}</Text>
            </View>
            <View className="flex-row items-center gap-1">
              <MapPin size={12} color="#a855f7" />
              <Text className="text-xs text-slate-300">{analytics?.loc_name || "Corporate Location"}</Text>
            </View>
            <View className="flex-row items-center gap-1">
              <Calendar size={12} color="#a855f7" />
              <Text className="text-xs text-slate-300">
                Joined: {analytics?.join_date ? formatDate(analytics.join_date) : "N/A"} ({analytics?.tenure_label || "N/A"})
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
                className={`text-[9px] font-bold ${
                  analytics?.is_active ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {analytics?.is_active ? "ACTIVE" : "INACTIVE"}
              </Text>
            </View>
          </View>
        </View>
      </View>

      {/* ── Content View ── */}
      {isLoading ? (
        <View className="py-16 items-center justify-center">
          <ActivityIndicator size="large" color="#a855f7" />
          <Text className="text-xs text-slate-400 mt-2 font-medium">
            Loading Employee #{empId} analytics...
          </Text>
        </View>
      ) : error || !analytics ? (
        <View className="py-6 items-center justify-center bg-dark-card border border-dark-border rounded-xl p-3">
          <AlertTriangle size={24} color={THEME_COLORS.danger} />
          <Text className="text-xs font-semibold text-slate-300 mt-1.5">
            Failed to load Employee #{empId} analytics.
          </Text>
        </View>
      ) : (
        <View className="gap-3 w-full">
          {/* ── Lifetime Summary KPI Cards Grid ── */}
          <View className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2.5">
            <View className="bg-dark-card border border-dark-border p-2.5 rounded-xl">
              <View className="flex-row items-center justify-between mb-1">
                <Text className="text-[9px] font-bold uppercase tracking-wider text-slate-400">
                  Total Logs
                </Text>
                <View className="p-1 rounded bg-purple-950/80 border border-purple-800/60">
                  <Users size={12} color="#c084fc" />
                </View>
              </View>
              <Text className="text-base font-extrabold text-white">
                {analytics.total_attendance_records.toLocaleString()}
              </Text>
              <Text className="text-[9px] text-purple-300 mt-0.5 font-mono">
                {analytics.tenure_days} days tenure
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-2.5 rounded-xl">
              <View className="flex-row items-center justify-between mb-1">
                <Text className="text-[9px] font-bold uppercase tracking-wider text-slate-400">
                  Present Days
                </Text>
                <View className="p-1 rounded bg-emerald-950/80 border border-emerald-800/60">
                  <UserCheck size={12} color="#34d399" />
                </View>
              </View>
              <Text className="text-base font-extrabold text-emerald-400">{analytics.present_pct}%</Text>
              <Text className="text-[9px] text-emerald-400/80 mt-0.5 font-mono">
                {analytics.present_days.toLocaleString()} present
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-2.5 rounded-xl">
              <View className="flex-row items-center justify-between mb-1">
                <Text className="text-[9px] font-bold uppercase tracking-wider text-slate-400">
                  Absence Days
                </Text>
                <View className="p-1 rounded bg-rose-950/80 border border-rose-800/60">
                  <UserX size={12} color="#f87171" />
                </View>
              </View>
              <Text className="text-base font-extrabold text-rose-400">{analytics.absent_pct}%</Text>
              <Text className="text-[9px] text-rose-400/80 mt-0.5 font-mono">
                {analytics.absent_days.toLocaleString()} absent
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-2.5 rounded-xl">
              <View className="flex-row items-center justify-between mb-1">
                <Text className="text-[9px] font-bold uppercase tracking-wider text-slate-400">
                  Late Arrivals
                </Text>
                <View className="p-1 rounded bg-amber-950/80 border border-amber-800/60">
                  <Clock size={12} color="#fbbf24" />
                </View>
              </View>
              <Text className="text-base font-extrabold text-amber-400">
                {analytics.late_arrivals_count}
              </Text>
              <Text className="text-[9px] text-amber-400/80 mt-0.5 font-mono">
                {analytics.total_late_mins.toLocaleString()} mins late
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-2.5 rounded-xl">
              <View className="flex-row items-center justify-between mb-1">
                <Text className="text-[9px] font-bold uppercase tracking-wider text-slate-400">
                  Overtime
                </Text>
                <View className="p-1 rounded bg-sky-950/80 border border-sky-800/60">
                  <Clock size={12} color="#38bdf8" />
                </View>
              </View>
              <Text className="text-base font-extrabold text-sky-400 font-mono">
                {analytics.total_ot_hours.toLocaleString()} h
              </Text>
              <Text className="text-[9px] text-sky-400/80 mt-0.5 font-mono">
                {analytics.overtime_records_count} OT shifts
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-2.5 rounded-xl">
              <View className="flex-row items-center justify-between mb-1">
                <Text className="text-[9px] font-bold uppercase tracking-wider text-slate-400">
                  Manual Credits
                </Text>
                <View className="p-1 rounded bg-purple-950/80 border border-purple-800/60">
                  <FileText size={12} color="#c084fc" />
                </View>
              </View>
              <Text className="text-base font-extrabold text-purple-300">
                {analytics.unpunched_salary_days}
              </Text>
              <Text className="text-[9px] text-slate-400 mt-0.5 font-mono">
                Unpunched salary
              </Text>
            </View>

            <View className="bg-dark-card border border-red-900/60 p-2.5 rounded-xl bg-red-950/20">
              <View className="flex-row items-center justify-between mb-1">
                <Text className="text-[9px] font-bold uppercase tracking-wider text-red-300">
                  Unexcused Abs
                </Text>
                <View className="p-1 rounded bg-red-950/90 border border-red-700/60">
                  <AlertTriangle size={12} color="#ef4444" />
                </View>
              </View>
              <Text className="text-base font-extrabold text-red-400">
                {analytics.unauthorized_absence_days}
              </Text>
              <Text className="text-[9px] text-red-300/80 mt-0.5 font-mono">
                {analytics.leave_covered_absence_days} in leave
              </Text>
            </View>
          </View>

          {/* ── Lifetime Leaves Breakdown Table ── */}
          {(() => {
            const totalLeaveDaysTaken = analytics.leaves_breakdown.reduce((acc, l) => acc + l.total_days_taken, 0);

            return (
              <View className="bg-dark-card border border-dark-border rounded-xl p-3 shadow-sm gap-3">
                {/* Header Title & Summary Banner */}
                <View className="flex-row items-center justify-between pb-2.5 border-b border-dark-border/80 flex-wrap gap-2">
                  <View className="flex-row items-center gap-2">
                    <View className="p-1.5 rounded-lg bg-emerald-950/80 border border-emerald-800/60">
                      <CalendarCheck size={16} color="#34d399" />
                    </View>
                    <View>
                      <Text className="text-xs font-bold text-white">
                        Lifetime Approved Leaves Breakdown (Category-Wise)
                      </Text>
                      <Text className="text-[10px] text-slate-400">
                        HR-approved leave history since {analytics.join_date ? formatDate(analytics.join_date) : "Join Date"} • Period Covered: {analytics.tenure_label}
                      </Text>
                    </View>
                  </View>

                  <View className="flex-row items-center gap-2 flex-wrap">
                    <View className="px-2.5 py-1 rounded-md bg-purple-950/80 border border-purple-800/60 flex-row items-center gap-1.5">
                      <PieChart size={11} color="#c084fc" />
                      <Text className="text-[10px] font-mono font-bold text-purple-300">
                        {analytics.leaves_breakdown.reduce((acc, l) => acc + l.request_count, 0)} Applications
                      </Text>
                    </View>
                    <View className="px-2.5 py-1 rounded-md bg-emerald-950/80 border border-emerald-800/60 flex-row items-center gap-1.5">
                      <TrendingUp size={11} color="#34d399" />
                      <Text className="text-[10px] font-mono font-bold text-emerald-300">
                        {totalLeaveDaysTaken} Total Leave Days
                      </Text>
                    </View>
                  </View>
                </View>

                {/* Leave Type Category Legend Box */}
                <View className="bg-slate-900/80 border border-slate-800 rounded-lg p-2.5 flex-row items-center justify-between flex-wrap gap-2 shadow-xs">
                  <View className="flex-row items-center gap-1.5">
                    <HelpCircle size={13} color="#a855f7" />
                    <Text className="text-[11px] font-bold text-white uppercase tracking-wider">
                      Leave Type Key & Legend:
                    </Text>
                  </View>
                  <View className="flex-row items-center gap-3 flex-wrap">
                    <View className="flex-row items-center gap-1.5">
                      <View className="px-2 py-0.5 rounded bg-purple-950 border border-purple-700/60">
                        <Text className="text-[10px] font-mono font-extrabold text-purple-300">PL</Text>
                      </View>
                      <Text className="text-xs font-semibold text-slate-200">PL = Privilege/Paid Leave</Text>
                    </View>

                    <View className="flex-row items-center gap-1.5">
                      <View className="px-2 py-0.5 rounded bg-sky-950 border border-sky-700/60">
                        <Text className="text-[10px] font-mono font-extrabold text-sky-300">CL</Text>
                      </View>
                      <Text className="text-xs font-semibold text-slate-200">CL = Casual Leave</Text>
                    </View>

                    <View className="flex-row items-center gap-1.5">
                      <View className="px-2 py-0.5 rounded bg-amber-950 border border-amber-700/60">
                        <Text className="text-[10px] font-mono font-extrabold text-amber-300">SL</Text>
                      </View>
                      <Text className="text-xs font-semibold text-slate-200">SL = Sick/Medical Leave</Text>
                    </View>

                    <View className="flex-row items-center gap-1.5">
                      <View className="px-2 py-0.5 rounded bg-rose-950 border border-rose-700/60">
                        <Text className="text-[10px] font-mono font-extrabold text-rose-300">CO/ML</Text>
                      </View>
                      <Text className="text-xs font-semibold text-slate-200">CO/ML = Comp Off/Special</Text>
                    </View>
                  </View>
                </View>

                {/* Category-Wise Breakdown Table */}
                <ScrollView
                  horizontal
                  showsHorizontalScrollIndicator={true}
                  className="w-full"
                  contentContainerStyle={{ minWidth: "100%", flexGrow: 1 }}
                >
                  <View className="min-w-[980px] w-full border border-dark-border rounded-lg overflow-hidden">
                    {/* Header */}
                    <View className="flex-row items-center bg-slate-900/90 px-3 py-2 border-b border-dark-border">
                      <Text className="w-60 pr-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                        Leave Type / Category
                      </Text>
                      <Text className="flex-1 min-w-[160px] pr-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                        Share of Total Leaves (% & Bar)
                      </Text>
                      <Text className="w-32 pr-2 text-[10px] font-bold uppercase tracking-wider text-slate-400 text-right">
                        Approved Apps
                      </Text>
                      <Text className="w-32 pr-2 text-[10px] font-bold uppercase tracking-wider text-slate-400 text-right">
                        Avg Duration / App
                      </Text>
                      <Text className="w-32 pr-2 text-[10px] font-bold uppercase tracking-wider text-slate-400 text-right">
                        Last Availed Date
                      </Text>
                      <Text className="w-32 text-[10px] font-bold uppercase tracking-wider text-slate-400 text-right">
                        Total Days Taken
                      </Text>
                    </View>

                    {/* Category Rows */}
                    {analytics.leaves_breakdown.map((l, idx) => {
                      const share = l.share_pct ?? 0;
                      const rawCode = (l.leave_code || "PL").trim().toUpperCase();
                      const code =
                        rawCode === "PL" || rawCode === "CL" || rawCode === "SL"
                          ? rawCode
                          : "CO/ML";

                      const fullLabel =
                        code === "PL"
                          ? "Privilege/Paid Leave"
                          : code === "CL"
                          ? "Casual Leave"
                          : code === "SL"
                          ? "Sick/Medical Leave"
                          : "Comp Off/Special";

                      const badgeColor =
                        code === "PL"
                          ? "bg-purple-950/90 border-purple-700/60 text-purple-300"
                          : code === "CL"
                          ? "bg-sky-950/90 border-sky-700/60 text-sky-300"
                          : code === "SL"
                          ? "bg-amber-950/90 border-amber-700/60 text-amber-300"
                          : "bg-rose-950/90 border-rose-700/60 text-rose-300";

                      return (
                        <View
                          key={idx}
                          className="flex-row items-center px-3 py-2.5 border-b border-dark-border/60 hover:bg-dark-bg/40 transition-colors"
                        >
                          {/* Category */}
                          <View className="w-60 pr-2 flex-row items-center gap-2">
                            <View className={`px-2 py-0.5 rounded border shrink-0 ${badgeColor}`}>
                              <Text className="text-[9px] font-mono font-extrabold">{code}</Text>
                            </View>
                            <Text className="flex-1 text-xs font-bold text-white" numberOfLines={1}>
                              {fullLabel}
                            </Text>
                          </View>

                          {/* Utilization Share Bar */}
                          <View className="flex-1 min-w-[160px] pr-2 flex-row items-center gap-2">
                            <View className="flex-1 h-2 rounded-full bg-slate-800 overflow-hidden">
                              <View
                                className="h-full rounded-full bg-emerald-500"
                                style={{ width: `${Math.min(share, 100)}%` }}
                              />
                            </View>
                            <Text className="w-12 text-[10px] font-mono text-slate-300 font-bold text-right">
                              {share}%
                            </Text>
                          </View>

                          {/* Requests */}
                          <View className="w-32 pr-2 items-end">
                            <Text className="text-xs font-mono text-purple-300 font-bold">
                              {l.request_count} app{l.request_count !== 1 ? "s" : ""}
                            </Text>
                          </View>

                          {/* Avg Duration / App */}
                          <View className="w-32 pr-2 items-end">
                            <Text className="text-xs font-mono text-slate-300">
                              {l.avg_days_per_request} d / app
                            </Text>
                          </View>

                          {/* Last Availed */}
                          <View className="w-32 pr-2 items-end">
                            <Text className="text-xs font-mono text-slate-400">
                              {l.last_availed_date ? formatDate(l.last_availed_date) : "N/A"}
                            </Text>
                          </View>

                          {/* Total Days */}
                          <View className="w-32 items-end">
                            <Text className="text-xs font-mono text-emerald-400 font-bold">
                              {l.total_days_taken} days
                            </Text>
                          </View>
                        </View>
                      );
                    })}
                  </View>
                </ScrollView>

                {/* Explanatory Footer Callout */}
                <View className="flex-row items-center gap-2 bg-slate-900/40 border border-slate-800/60 rounded-lg p-2">
                  <Info size={13} color="#94a3b8" />
                  <Text className="text-[10px] text-slate-400 flex-1">
                    Data Scope: Includes only officially approved leave applications (<Text className="font-bold text-slate-300">Status: Approved</Text>). Unapproved absences are profiled separately in the Daily Biometric Punch History below.
                  </Text>
                </View>
              </View>
            );
          })()}

          {/* ── Employee Punch Log History ── */}
          <View className="gap-2">
            <Text className="text-xs font-bold text-white">
              Employee Daily Biometric Punch History Logs ({analytics.emp_name})
            </Text>
            <AttendanceDirectoryTab empId={empId} />
          </View>
        </View>
      )}
    </ScrollView>
  );
}
