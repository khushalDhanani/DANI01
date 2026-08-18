import React, { useState } from "react";
import { ActivityIndicator, Pressable, ScrollView, Text, View } from "react-native";
import { useRouter } from "expo-router";
import {
  AlertTriangle,
  ArrowLeft,
  CalendarCheck,
  Clock,
  FileText,
  UserCheck,
  UserX,
  Users,
} from "lucide-react-native";

import { THEME_COLORS } from "@/constants/theme";
import { useDepartmentDetail } from "@/hooks/useAttendance";
import { AttendanceDirectoryTab } from "./AttendanceDirectoryTab";
import { AttendanceLeaveTab } from "./AttendanceLeaveTab";

interface DepartmentDetailViewProps {
  deptId: number;
}

type SubTabKey = "punches" | "leaves";

export function DepartmentDetailView({ deptId }: DepartmentDetailViewProps) {
  const router = useRouter();
  const [activeSubTab, setActiveSubTab] = useState<SubTabKey>("punches");

  const { data: deptDetail, isLoading, error } = useDepartmentDetail(deptId);

  return (
    <ScrollView className="flex-1 bg-dark-bg p-4 md:p-4" showsVerticalScrollIndicator={false}>
      {/* ── Page Navigation Header & Breadcrumb ── */}
      <View className="flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
        <View className="flex-1">
          <Pressable
            onPress={() => (router.canGoBack() ? router.back() : router.push("/modules/attendance"))}
            className="flex-row items-center gap-2 mb-3 self-start px-3 py-1.5 rounded-xl bg-dark-card border border-dark-border hover:bg-slate-800"
          >

            <ArrowLeft size={16} color="#a855f7" />
            <Text className="text-xs font-bold text-purple-300">Back to Attendance Master</Text>
          </Pressable>

          <View className="flex-row items-center gap-2 mb-1 flex-wrap">
            <View className="bg-purple-950/80 border border-purple-800/60 px-2 py-0.5 rounded">
              <Text className="text-[10px] font-mono font-bold text-purple-400">
                {deptDetail?.dept_code || `DEP-${deptId}`}
              </Text>
            </View>
            <Text className="text-xs uppercase font-bold text-slate-400 tracking-wider">
              Department Attendance & Leave Analysis
            </Text>
          </View>

          <Text className="text-xl md:text-xl font-black text-white">
            {deptDetail?.dept_name || `Department #${deptId}`}
          </Text>
          <Text className="text-xs text-slate-400 mt-1">
            Department-level active workforce headcount, daily biometric punches, overtime minutes, and employee leave applications.
          </Text>
        </View>
      </View>

      {/* ── Content View ── */}
      {isLoading ? (
        <View className="py-20 items-center justify-center">
          <ActivityIndicator size="large" color="#a855f7" />
          <Text className="text-xs text-slate-400 mt-3 font-medium">
            Loading Department #{deptId} analytics...
          </Text>
        </View>
      ) : error || !deptDetail ? (
        <View className="py-8 items-center justify-center bg-dark-card border border-dark-border rounded-xl p-4">
          <AlertTriangle size={32} color={THEME_COLORS.danger} />
          <Text className="text-sm font-semibold text-slate-300 mt-2">
            Failed to load Department #{deptId} details.
          </Text>
          <Text className="text-xs text-slate-500 mt-1">
            Ensure database connectivity and retry.
          </Text>
        </View>
      ) : (
        <View className="gap-4 w-full">
          {/* ── Summary KPI Cards Grid ── */}
          <View className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Active Headcount
                </Text>
                <View className="p-1.5 rounded-lg bg-purple-950/80 border border-purple-800/60">
                  <Users size={14} color="#c084fc" />
                </View>
              </View>
              <Text className="text-xl font-black text-white">{deptDetail.headcount}</Text>
              <Text className="text-[10px] text-purple-300 mt-1 font-mono">Active Staff</Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Present Rate
                </Text>
                <View className="p-1.5 rounded-lg bg-emerald-950/80 border border-emerald-800/60">
                  <UserCheck size={14} color="#34d399" />
                </View>
              </View>
              <Text className="text-xl font-black text-emerald-400">{deptDetail.present_pct}%</Text>
              <Text className="text-[10px] text-emerald-400/80 mt-1 font-mono">
                {deptDetail.present_count.toLocaleString()} present
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Absence Rate
                </Text>
                <View className="p-1.5 rounded-lg bg-rose-950/80 border border-rose-800/60">
                  <UserX size={14} color="#f87171" />
                </View>
              </View>
              <Text className="text-xl font-black text-rose-400">{deptDetail.absent_pct}%</Text>
              <Text className="text-[10px] text-rose-400/80 mt-1 font-mono">
                {deptDetail.absent_count.toLocaleString()} absent
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Late Ratio
                </Text>
                <View className="p-1.5 rounded-lg bg-amber-950/80 border border-amber-800/60">
                  <Clock size={14} color="#fbbf24" />
                </View>
              </View>
              <Text className="text-xl font-black text-amber-400">{deptDetail.late_pct}%</Text>
              <Text className="text-[10px] text-amber-400/80 mt-1 font-mono">
                {deptDetail.late_count.toLocaleString()} late coming
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  OT Hours
                </Text>
                <View className="p-1.5 rounded-lg bg-sky-950/80 border border-sky-800/60">
                  <Clock size={14} color="#38bdf8" />
                </View>
              </View>
              <Text className="text-xl font-black text-sky-400 font-mono">
                {deptDetail.total_ot_hours.toLocaleString()} h
              </Text>
              <Text className="text-[10px] text-sky-400/80 mt-1 font-mono">
                {deptDetail.avg_ot_hours_per_emp} h/emp avg
              </Text>
            </View>

            <View className="bg-dark-card border border-dark-border p-4 rounded-xl">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Active Leaves
                </Text>
                <View className="p-1.5 rounded-lg bg-purple-950/80 border border-purple-800/60">
                  <FileText size={14} color="#c084fc" />
                </View>
              </View>
              <Text className="text-xl font-black text-purple-300">
                {deptDetail.active_leaves_count}
              </Text>
              <Text className="text-[10px] text-slate-400 mt-1 font-mono">
                {deptDetail.pending_leaves_count} pending
              </Text>
            </View>
          </View>

          {/* ── Interactive Sub-Tab Bar ── */}
          <View className="flex-row items-center gap-2 border-b border-dark-border pb-3">
            <Pressable
              onPress={() => setActiveSubTab("punches")}
              className={`flex-row items-center gap-2 px-4 py-2.5 rounded-xl border transition-all ${
                activeSubTab === "punches"
                  ? "bg-purple-600 border-purple-400 shadow-md"
                  : "bg-dark-card border-dark-border hover:border-slate-600"
              }`}
            >
              <CalendarCheck size={16} color={activeSubTab === "punches" ? "#fff" : "#94a3b8"} />
              <Text className={`text-xs font-bold ${activeSubTab === "punches" ? "text-white" : "text-slate-400"}`}>
                Department Daily Punches Directory
              </Text>
            </Pressable>

            <Pressable
              onPress={() => setActiveSubTab("leaves")}
              className={`flex-row items-center gap-2 px-4 py-2.5 rounded-xl border transition-all ${
                activeSubTab === "leaves"
                  ? "bg-purple-600 border-purple-400 shadow-md"
                  : "bg-dark-card border-dark-border hover:border-slate-600"
              }`}
            >
              <FileText size={16} color={activeSubTab === "leaves" ? "#fff" : "#94a3b8"} />
              <Text className={`text-xs font-bold ${activeSubTab === "leaves" ? "text-white" : "text-slate-400"}`}>
                Department Employee Leaves & Balances
              </Text>
            </Pressable>
          </View>

          {/* ── Sub-Tab Views ── */}
          {activeSubTab === "punches" && <AttendanceDirectoryTab deptId={deptId} />}
          {activeSubTab === "leaves" && <AttendanceLeaveTab deptId={deptId} />}
        </View>
      )}
    </ScrollView>
  );
}
