import React, { useState } from "react";
import { ActivityIndicator, Pressable, Text, View } from "react-native";
import {
  AlertTriangle,
  Building,
  Building2,
  CalendarCheck,
  Clock,
  Clock3,
  MapPin,
  UserCheck,
  UserX,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import { useAttendanceOrgHierarchy, useAttendanceOverview } from "@/hooks/useAttendance";

interface AttendanceOverviewTabProps {
  deptId?: number;
  compId?: number;
}

export function AttendanceOverviewTab({ deptId, compId }: AttendanceOverviewTabProps = {}) {
  const [selectedDeptId, setSelectedDeptId] = useState<number | undefined>(deptId);
  const [selectedCompId, setSelectedCompId] = useState<number | undefined>(compId);

  const { data: overview, isLoading: isOverviewLoading, error: overviewError } = useAttendanceOverview(
    selectedDeptId,
    selectedCompId
  );
  const { data: orgHierarchy, isLoading: isOrgLoading } = useAttendanceOrgHierarchy();

  if (isOverviewLoading || isOrgLoading) {
    return (
      <View className="py-20 items-center justify-center">
        <ActivityIndicator size="large" color="#a855f7" />
        <Text className="text-xs text-slate-400 mt-3 font-medium">
          Loading Attendance & Organizational Hierarchy metrics...
        </Text>
      </View>
    );
  }

  if (overviewError || !overview) {
    return (
      <View className="py-8 items-center justify-center bg-dark-card border border-dark-border rounded-xl p-4">
        <AlertTriangle size={32} color={THEME_COLORS.danger} />
        <Text className="text-sm font-semibold text-slate-300 mt-2">
          Failed to load Attendance Overview metrics.
        </Text>
        <Text className="text-xs text-slate-500 mt-1">
          Ensure MSSQL database connectivity and retry.
        </Text>
      </View>
    );
  }

  const { attendance_metrics: att, punch_metrics: pm, shift_distribution: shifts } = overview;

  return (
    <View className="gap-2.5 w-full">
      {/* ── Organizational Filter Banner ── */}
      <View className="bg-dark-card border border-dark-border p-3 rounded-xl flex-row flex-wrap items-center justify-between gap-3">
        <View className="flex-row items-center gap-3">
          <View className="p-2 rounded-xl bg-purple-950/80 border border-purple-800/60">
            <Building2 size={18} color="#c084fc" />
          </View>
          <View>
            <Text className="text-sm font-bold text-white">Organizational Hierarchy View</Text>
            <Text className="text-xs text-slate-400">
              {selectedDeptId
                ? `Filtered by Department #${selectedDeptId}`
                : selectedCompId
                ? `Filtered by Company #${selectedCompId}`
                : "Showing Enterprise-Wide Consolidated Metrics"}
            </Text>
          </View>
        </View>

        {(selectedDeptId !== undefined || selectedCompId !== undefined) && (
          <Pressable
            onPress={() => {
              setSelectedDeptId(undefined);
              setSelectedCompId(undefined);
            }}
            className="px-3 py-1.5 rounded-lg bg-dark-bg border border-purple-800/60 hover:bg-purple-950/50"
          >
            <Text className="text-xs font-semibold text-purple-300">Reset Filters</Text>
          </Pressable>
        )}
      </View>

      {/* ── Stat Cards Grid ── */}
      <View className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Attendance Logs */}
        <View className="bg-dark-card border border-dark-border p-3 rounded-xl">
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Total Attendance Records
            </Text>
            <View className="p-2 rounded-xl bg-purple-950/80 border border-purple-800/60">
              <CalendarCheck size={18} color="#c084fc" />
            </View>
          </View>
          <Text className="text-xl font-black text-white">
            {att.total_attendance_records.toLocaleString()}
          </Text>
          <Text className="text-xs text-slate-400 mt-1 font-mono">
            {att.employees_with_attendance.toLocaleString()} unique employees
          </Text>
        </View>

        {/* Present Days */}
        <View className="bg-dark-card border border-dark-border p-3 rounded-xl">
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Present Days
            </Text>
            <View className="p-2 rounded-xl bg-emerald-950/80 border border-emerald-800/60">
              <UserCheck size={18} color="#34d399" />
            </View>
          </View>
          <Text className="text-xl font-black text-emerald-400">
            {att.present_days.toLocaleString()}
          </Text>
          <Text className="text-xs text-emerald-400/80 mt-1 font-semibold">
            {att.present_pct}% present ratio
          </Text>
        </View>

        {/* Absent Days */}
        <View className="bg-dark-card border border-dark-border p-3 rounded-xl">
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Absent Days
            </Text>
            <View className="p-2 rounded-xl bg-rose-950/80 border border-rose-800/60">
              <UserX size={18} color="#f87171" />
            </View>
          </View>
          <Text className="text-xl font-black text-rose-400">
            {att.absent_days.toLocaleString()}
          </Text>
          <Text className="text-xs text-rose-400/80 mt-1 font-semibold">
            {att.absent_pct}% absence ratio
          </Text>
        </View>

        {/* Overtime Hours */}
        <View className="bg-dark-card border border-dark-border p-3 rounded-xl">
          <View className="flex-row items-center justify-between mb-3">
            <Text className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Overtime Hours
            </Text>
            <View className="p-2 rounded-xl bg-amber-950/80 border border-amber-800/60">
              <Clock size={18} color="#fbbf24" />
            </View>
          </View>
          <Text className="text-xl font-black text-amber-400">
            {pm.total_overtime_hours.toLocaleString()} hrs
          </Text>
          <Text className="text-xs text-slate-400 mt-1 font-mono">
            {pm.overtime_records_count.toLocaleString()} OT instances
          </Text>
        </View>
      </View>

      {/* ── Organizational Hierarchy Tree & Sites Breakdown ── */}
      {orgHierarchy && (
        <View className="gap-4 w-full">
          {/* Companies Breakdown Cards */}
          <View className="bg-dark-card border border-dark-border rounded-xl p-4">
            <View className="flex-row items-center justify-between mb-4">
              <View className="flex-row items-center gap-2">
                <Building size={18} color="#c084fc" />
                <Text className="text-base font-bold text-white">Company Level Breakdown</Text>
              </View>
              <Text className="text-xs text-slate-400 font-mono">
                {orgHierarchy.companies.length} Legal Entities
              </Text>
            </View>

            <View className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {orgHierarchy.companies.map((c, index) => {
                const isSelected = selectedCompId === c.id;
                return (
                  <Pressable
                    key={`comp-${c.id}-${index}`}
                    onPress={() => setSelectedCompId(isSelected ? undefined : c.id)}
                    className={`p-4 rounded-xl border transition-all ${
                      isSelected
                        ? "bg-purple-950/40 border-purple-500"
                        : "bg-dark-bg border-dark-border hover:border-slate-700"
                    }`}
                  >
                    <View className="flex-row items-center justify-between mb-2">
                      <Text className="text-sm font-bold text-white">{c.name}</Text>
                      <View className="px-2 py-0.5 rounded bg-purple-950 border border-purple-800">
                        <Text className="text-[10px] font-mono font-bold text-purple-300">
                          {c.code || "COMP"}
                        </Text>
                      </View>
                    </View>

                    <View className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-dark-border/60">
                      <View>
                        <Text className="text-[10px] text-slate-400">Records</Text>
                        <Text className="text-xs font-bold text-slate-200">
                          {c.total_attendance_records.toLocaleString()}
                        </Text>
                      </View>
                      <View>
                        <Text className="text-[10px] text-slate-400">Headcount</Text>
                        <Text className="text-xs font-bold text-purple-300">{c.headcount} Staff</Text>
                      </View>
                      <View>
                        <Text className="text-[10px] text-slate-400">OT Hours</Text>
                        <Text className="text-xs font-bold text-amber-400">
                          {c.total_ot_hours.toLocaleString()} hrs
                        </Text>
                      </View>
                    </View>
                  </Pressable>
                );
              })}
            </View>
          </View>

          {/* Plant / Site Locations Grid */}
          <View className="bg-dark-card border border-dark-border rounded-xl p-4">
            <View className="flex-row items-center justify-between mb-4">
              <View className="flex-row items-center gap-2">
                <MapPin size={18} color="#38bdf8" />
                <Text className="text-base font-bold text-white">Plant & Location Level Attendance</Text>
              </View>
              <Text className="text-xs text-slate-400 font-mono">
                {orgHierarchy.locations.length} Sites & Manufacturing Plants
              </Text>
            </View>

            <View className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {orgHierarchy.locations.slice(0, 9).map((loc, index) => (
                <View key={`loc-${loc.id}-${index}`} className="bg-dark-bg p-4 rounded-xl border border-dark-border">
                  <View className="flex-row items-center justify-between mb-2">
                    <Text className="text-sm font-bold text-white">{loc.name}</Text>
                    <View className="px-2 py-0.5 rounded bg-sky-950 border border-sky-800">
                      <Text className="text-[10px] font-mono font-bold text-sky-300">
                        {loc.code || "SITE"}
                      </Text>
                    </View>
                  </View>
                  <View className="flex-row items-center justify-between pt-2 mt-2 border-t border-dark-border/60">
                    <Text className="text-[11px] text-slate-400">Attendance Volume:</Text>
                    <Text className="text-xs font-bold text-slate-200">
                      {loc.total_attendance_records.toLocaleString()}
                    </Text>
                  </View>
                  <View className="flex-row items-center justify-between pt-1">
                    <Text className="text-[11px] text-slate-400">Late Arrival Ratio:</Text>
                    <Text className="text-xs font-bold text-amber-400">{loc.late_pct}%</Text>
                  </View>
                  <View className="flex-row items-center justify-between pt-1">
                    <Text className="text-[11px] text-slate-400">Active Staff:</Text>
                    <Text className="text-xs font-bold text-purple-300">{loc.headcount}</Text>
                  </View>
                </View>
              ))}
            </View>
          </View>
        </View>
      )}



      {/* ── Punch & Grace Statistics ── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4">
        <Text className="text-base font-bold text-white mb-4">
          Biometric Punch & Grace Minute Metrics
        </Text>
        <View className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <View className="bg-dark-bg p-4 rounded-xl border border-dark-border">
            <Text className="text-[11px] font-bold uppercase text-slate-400 tracking-wider">Valid Punch Pairs</Text>
            <Text className="text-xl font-extrabold text-white mt-1">{pm.valid_punch_pairs.toLocaleString()}</Text>
            <Text className="text-[10px] text-slate-500 mt-0.5 font-mono">Complete In/Out</Text>
          </View>

          <View className="bg-dark-bg p-4 rounded-xl border border-dark-border">
            <Text className="text-[11px] font-bold uppercase text-slate-400 tracking-wider">Late Arrivals</Text>
            <Text className="text-xl font-extrabold text-amber-400 mt-1">{pm.late_arrivals_count.toLocaleString()}</Text>
            <Text className="text-[10px] text-amber-400/80 mt-0.5 font-mono">Arrived after shift</Text>
          </View>

          <View className="bg-dark-bg p-4 rounded-xl border border-dark-border">
            <Text className="text-[11px] font-bold uppercase text-slate-400 tracking-wider">Early Departures</Text>
            <Text className="text-xl font-extrabold text-amber-400 mt-1">{pm.early_departures_count.toLocaleString()}</Text>
            <Text className="text-[10px] text-amber-400/80 mt-0.5 font-mono">Left before shift</Text>
          </View>

          <View className="bg-dark-bg p-4 rounded-xl border border-dark-border">
            <Text className="text-[11px] font-bold uppercase text-slate-400 tracking-wider">Unclosed Punch Logs</Text>
            <Text className="text-xl font-extrabold text-rose-400 mt-1">{pm.missing_punch_out_count.toLocaleString()}</Text>
            <Text className="text-[10px] text-rose-400/80 mt-0.5 font-mono">Missing Punch-Out</Text>
          </View>
        </View>
      </View>

      {/* ── Active Shift Roster Master ── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 w-full">
        <View className="flex-row items-center justify-between mb-4">
          <View>
            <Text className="text-base font-bold text-white">Active Shift Roster Master</Text>
            <Text className="text-xs text-slate-400">
              Shift timing configurations and workforce assignment distribution.
            </Text>
          </View>
          <View className="px-2.5 py-1 rounded-lg bg-purple-950/80 border border-purple-800/60">
            <Text className="text-xs font-mono font-bold text-purple-300">
              {shifts.length} Active Shifts
            </Text>
          </View>
        </View>

        <View className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {shifts.map((s, index) => (
            <View key={`shift-${s.shift_id}-${index}`} className="bg-dark-bg p-4 rounded-xl border border-dark-border">
              <View className="flex-row items-center justify-between mb-2">
                <Text className="text-sm font-bold text-white">{s.shift_description}</Text>
                <View className="px-2 py-0.5 rounded bg-dark-card border border-dark-border font-mono text-[10px] text-purple-400 font-bold">
                  <Text className="text-[10px] font-mono font-bold text-purple-400">{s.shift_code}</Text>
                </View>
              </View>
              <View className="flex-row items-center gap-2 mb-3">
                <Clock3 size={14} color="#94a3b8" />
                <Text className="text-xs text-slate-300 font-mono">
                  {s.from_time} – {s.to_time}
                </Text>
              </View>
              <View className="flex-row items-center justify-between pt-2 border-t border-dark-border/60">
                <Text className="text-[11px] text-slate-400">Assigned Records:</Text>
                <Text className="text-xs font-bold text-purple-300">
                  {s.assigned_attendance_count.toLocaleString()} ({s.percentage}%)
                </Text>
              </View>
            </View>
          ))}
        </View>
      </View>
    </View>
  );
}
