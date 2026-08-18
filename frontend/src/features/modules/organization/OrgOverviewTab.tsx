import React from "react";
import { ActivityIndicator, Text, View } from "react-native";
import {
  Award,
  Building2,
  CheckCircle2,
  Factory,
  Layers,
  MapPin,
  Users,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import type { OrgOverviewResponse } from "@/types/organization.types";

interface OrgOverviewTabProps {
  overview?: OrgOverviewResponse;
  isLoading: boolean;
}

export const OrgOverviewTab: React.FC<OrgOverviewTabProps> = ({
  overview,
  isLoading,
}) => {
  if (isLoading || !overview) {
    return (
      <View className="py-12 items-center justify-center">
        <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
        <Text className="text-sm text-slate-400 mt-3 font-medium">Loading organization structure metrics...</Text>
      </View>
    );
  }

  const {
    scale_counts,
    headcount_by_company,
    headcount_by_location,
    headcount_by_top_departments,
    headcount_by_grade,
    active_employee_total,
  } = overview;

  return (
    <View className="gap-4">
      {/* ── Top Scale KPI Cards ─────────────────────────────── */}
      <View className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* Companies */}
        <View className="bg-dark-card border border-blue-500/20 p-3.5 rounded-xl">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Companies</Text>
            <Building2 size={14} color="#60a5fa" />
          </View>
          <Text className="text-xl font-black text-white font-mono">{scale_counts.total_companies}</Text>
          <View className="flex-row items-center gap-1 mt-1">
            <CheckCircle2 size={10} color={THEME_COLORS.success} />
            <Text className="text-[10px] text-emerald-400 font-bold">{scale_counts.active_companies} Active</Text>
          </View>
        </View>

        {/* Locations */}
        <View className="bg-dark-card border border-emerald-500/20 p-3.5 rounded-xl">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Locations / Plants</Text>
            <MapPin size={14} color="#34d399" />
          </View>
          <Text className="text-xl font-black text-white font-mono">{scale_counts.total_locations}</Text>
          <View className="flex-row items-center gap-1 mt-1">
            <CheckCircle2 size={10} color={THEME_COLORS.success} />
            <Text className="text-[10px] text-emerald-400 font-bold">{scale_counts.active_locations} Active</Text>
          </View>
        </View>

        {/* Main Depts */}
        <View className="bg-dark-card border border-purple-500/20 p-3.5 rounded-xl">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Main Divisions</Text>
            <Layers size={14} color="#c084fc" />
          </View>
          <Text className="text-xl font-black text-white font-mono">{scale_counts.total_main_depts}</Text>
          <View className="flex-row items-center gap-1 mt-1">
            <CheckCircle2 size={10} color={THEME_COLORS.success} />
            <Text className="text-[10px] text-purple-400 font-bold">{scale_counts.active_main_depts} Active</Text>
          </View>
        </View>

        {/* Departments */}
        <View className="bg-dark-card border border-cyan-500/20 p-3.5 rounded-xl">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Departments</Text>
            <Factory size={14} color="#22d3ee" />
          </View>
          <Text className="text-xl font-black text-white font-mono">{scale_counts.total_departments}</Text>
          <View className="flex-row items-center gap-1 mt-1">
            <CheckCircle2 size={10} color={THEME_COLORS.success} />
            <Text className="text-[10px] text-cyan-400 font-bold">{scale_counts.active_departments} Active</Text>
          </View>
        </View>

        {/* Designations */}
        <View className="bg-dark-card border border-amber-500/20 p-3.5 rounded-xl">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Designations</Text>
            <Users size={14} color="#fbbf24" />
          </View>
          <Text className="text-xl font-black text-white font-mono">{scale_counts.total_designations}</Text>
          <View className="flex-row items-center gap-1 mt-1">
            <CheckCircle2 size={10} color={THEME_COLORS.success} />
            <Text className="text-[10px] text-amber-400 font-bold">{scale_counts.active_designations} Active</Text>
          </View>
        </View>

        {/* Grades */}
        <View className="bg-dark-card border border-rose-500/20 p-3.5 rounded-xl">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Grades / Levels</Text>
            <Award size={14} color="#f43f5e" />
          </View>
          <Text className="text-xl font-black text-white font-mono">{scale_counts.total_grades}</Text>
          <View className="flex-row items-center gap-1 mt-1">
            <CheckCircle2 size={10} color={THEME_COLORS.success} />
            <Text className="text-[10px] text-rose-400 font-bold">{scale_counts.active_grades} Active</Text>
          </View>
        </View>
      </View>

      {/* ── Active Staffing Summary Banner ─────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 flex-col md:flex-row md:items-center justify-between gap-3">
        <View className="flex-1">
          <View className="flex-row items-center gap-2 mb-1">
            <Building2 size={14} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-bold text-white uppercase tracking-wider">Active Corporate Entities</Text>
          </View>
          <Text className="text-[11px] text-slate-400">
            Total of <Text className="font-bold text-white font-mono">{active_employee_total.toLocaleString()}</Text> active employees mapped across {scale_counts.active_companies} legal companies, {scale_counts.active_locations} operating plants, and {scale_counts.active_departments} sub-teams.
          </Text>
        </View>

        <View className="flex-row gap-2">
          <View className="bg-dark-bg border border-emerald-500/30 px-3 py-2 rounded-lg">
            <Text className="text-[9px] uppercase font-bold text-slate-400">Active Units</Text>
            <Text className="text-sm font-mono font-bold text-emerald-400">{scale_counts.total_active_units}</Text>
          </View>
          <View className="bg-dark-bg border border-slate-700 px-3 py-2 rounded-lg">
            <Text className="text-[9px] uppercase font-bold text-slate-400">Inactive Units</Text>
            <Text className="text-sm font-mono font-bold text-slate-400">{scale_counts.total_inactive_units}</Text>
          </View>
        </View>
      </View>

      {/* ── Grid: Company Headcount & Location Breakdown ───── */}
      <View className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Company Distribution */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center gap-2 mb-3">
            <Building2 size={15} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-bold text-white">Headcount by Legal Entity (Company)</Text>
          </View>

          <View className="gap-2.5">
            {headcount_by_company.map((comp) => (
              <View key={comp.id} className="bg-dark-bg border border-dark-border p-3 rounded-lg gap-2">
                <View className="flex-row items-center justify-between">
                  <View className="flex-row items-center gap-2 flex-1">
                    {comp.code && (
                      <View className="bg-blue-950 border border-blue-800 px-1.5 py-0.5 rounded">
                        <Text className="text-[9px] font-mono font-bold text-blue-400">{comp.code}</Text>
                      </View>
                    )}
                    <Text className="text-xs font-bold text-white truncate flex-1">{comp.name}</Text>
                  </View>
                  <Text className="text-xs font-mono font-bold text-blue-400">
                    {comp.count.toLocaleString()} ({comp.percentage}%)
                  </Text>
                </View>

                <View className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <View className="h-full bg-blue-500 rounded-full" style={{ width: `${comp.percentage}%` }} />
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* Location Distribution */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center gap-2 mb-3">
            <MapPin size={15} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-bold text-white">Operating Sites &amp; Plants Headcount</Text>
          </View>

          <View className="gap-2">
            {headcount_by_location.slice(0, 7).map((loc) => (
              <View key={loc.id} className="gap-1">
                <View className="flex-row justify-between">
                  <View className="flex-row items-center gap-1.5">
                    {loc.code && (
                      <Text className="text-[10px] font-mono text-slate-500">[{loc.code}]</Text>
                    )}
                    <Text className="text-[11px] text-slate-300 font-medium truncate max-w-[200px]">{loc.name}</Text>
                  </View>
                  <Text className="text-[11px] font-mono text-slate-400">{loc.count} ({loc.percentage}%)</Text>
                </View>
                <View className="h-1.5 bg-dark-bg rounded-full overflow-hidden">
                  <View className="h-full bg-emerald-500 rounded-full" style={{ width: `${loc.percentage}%` }} />
                </View>
              </View>
            ))}
          </View>
        </View>
      </View>

      {/* ── Grid: Top Departments & Grade Hierarchy ─────────── */}
      <View className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Top Departments */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center gap-2 mb-3">
            <Factory size={15} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-bold text-white">Top Operational Departments by Staffing</Text>
          </View>

          <View className="gap-2">
            {headcount_by_top_departments.slice(0, 8).map((dept) => (
              <View key={dept.id} className="gap-1">
                <View className="flex-row justify-between">
                  <Text className="text-[11px] text-slate-300 font-medium truncate max-w-[240px]">{dept.name}</Text>
                  <Text className="text-[11px] font-mono text-slate-400">{dept.count} ({dept.percentage}%)</Text>
                </View>
                <View className="h-1.5 bg-dark-bg rounded-full overflow-hidden">
                  <View className="h-full bg-cyan-500 rounded-full" style={{ width: `${dept.percentage * 3}%` }} />
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* Grade Distribution */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4">
          <View className="flex-row items-center gap-2 mb-3">
            <Award size={15} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-bold text-white">Executive &amp; Staff Grade Bands</Text>
          </View>

          <View className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {headcount_by_grade.map((g) => (
              <View key={g.id} className="bg-dark-bg border border-dark-border p-2.5 rounded-lg">
                <Text className="text-[10px] text-slate-400 font-bold truncate">{g.name}</Text>
                <Text className="text-base font-bold text-white font-mono mt-0.5">{g.count.toLocaleString()}</Text>
                <Text className="text-[9px] text-slate-500">{g.percentage}% of workforce</Text>
              </View>
            ))}
          </View>
        </View>
      </View>
    </View>
  );
};
