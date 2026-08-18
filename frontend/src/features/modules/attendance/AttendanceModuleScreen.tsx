import React, { useState } from "react";
import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import { useQueryClient } from "@tanstack/react-query";
import {
  Building2,
  CalendarCheck,
  Clock,
  FileText,
  RefreshCw,
  ShieldCheck,
} from "lucide-react-native";
import { AttendanceDirectoryTab } from "./AttendanceDirectoryTab";
import { AttendanceLeaveTab } from "./AttendanceLeaveTab";
import { AttendanceOverviewTab } from "./AttendanceOverviewTab";
import { AttendanceQualityTab } from "./AttendanceQualityTab";

type TabKey = "overview" | "directory" | "leave" | "quality";

const COMPANY_OPTIONS = [
  { id: undefined, label: "All Companies", code: "ALL" },
  { id: 1, label: "AIL", full: "Aether Industries Limited", code: "AIL" },
  { id: 2, label: "ASCL", full: "Aether Speciality Chemicals Limited", code: "ASCL" },
];

export function AttendanceModuleScreen() {
  const [activeTab, setActiveTab] = useState<TabKey>("overview");
  const [selectedCompId, setSelectedCompId] = useState<number | undefined>(undefined);
  const queryClient = useQueryClient();

  const handleRefreshAll = () => {
    queryClient.invalidateQueries({ queryKey: ["attendance"] });
  };

  const tabs: { key: TabKey; label: string; icon: React.ReactNode; badge?: string }[] = [
    {
      key: "overview",
      label: "Attendance Overview",
      icon: <CalendarCheck size={14} color={activeTab === "overview" ? "#ffffff" : "#94a3b8"} />,
    },
    {
      key: "directory",
      label: "Daily Punch Directory",
      icon: <Clock size={14} color={activeTab === "directory" ? "#ffffff" : "#94a3b8"} />,
    },
    {
      key: "leave",
      label: "Leave Applications & Balances",
      icon: <FileText size={14} color={activeTab === "leave" ? "#ffffff" : "#94a3b8"} />,
    },
    {
      key: "quality",
      label: "Attendance & Leave Audit",
      icon: <ShieldCheck size={14} color={activeTab === "quality" ? "#ffffff" : "#94a3b8"} />,
      badge: "14 Rules",
    },
  ];

  return (
    <ScrollView className="flex-1 bg-dark-bg p-3 md:p-4" showsVerticalScrollIndicator={false}>
      {/* ── Compact Header Banner ──────────────────────────── */}
      <View className="flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
        <View className="flex-1 flex-row items-center gap-3">
          <View className="bg-purple-950/80 border border-purple-800/60 px-2 py-0.5 rounded">
            <Text className="text-[10px] font-mono font-bold text-purple-400">ATTENDANCE</Text>
          </View>
          <View>
            <Text className="text-lg md:text-xl font-black text-white leading-tight">
              Attendance & Leave Analysis
            </Text>
            <Text className="text-[11px] text-slate-400" numberOfLines={1}>
              Punch timestamps, shift rosters, overtime, leave applications, and 14 audit rules.
            </Text>
          </View>
        </View>

        <View className="flex-row items-center gap-2 self-start md:self-auto">
          {/* Company Filter Selector */}
          <View className="flex-row items-center bg-dark-card border border-dark-border p-0.5 rounded-lg">
            <View className="px-1.5">
              <Building2 size={12} color="#94a3b8" />
            </View>
            {COMPANY_OPTIONS.map((c) => {
              const isSelected = selectedCompId === c.id;
              return (
                <TouchableOpacity
                  key={c.code}
                  onPress={() => setSelectedCompId(c.id)}
                  className={`px-2.5 py-1 rounded-md transition-all ${
                    isSelected
                      ? "bg-purple-600 border border-purple-400"
                      : "border-transparent"
                  }`}
                >
                  <Text
                    className={`text-[11px] font-bold font-mono ${
                      isSelected ? "text-white" : "text-slate-400"
                    }`}
                  >
                    {c.label}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>

          <TouchableOpacity
            onPress={handleRefreshAll}
            className="bg-dark-card border border-dark-border px-2.5 py-1.5 rounded-lg flex-row items-center gap-1.5 active:bg-slate-800"
          >
            <RefreshCw size={12} color="#a855f7" />
            <Text className="text-[11px] font-bold text-slate-300">Sync</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* ── Navigation Tab Bar ──────────────────────────────── */}
      <View className="flex-row flex-wrap items-center gap-1.5 border-b border-dark-border pb-2 mb-3">
        {tabs.map((t) => {
          const isActive = activeTab === t.key;
          return (
            <TouchableOpacity
              key={t.key}
              onPress={() => setActiveTab(t.key)}
              className={`flex-row items-center gap-1.5 px-3 py-1.5 rounded-lg border transition-all ${
                isActive
                  ? "bg-purple-600 border-purple-400 shadow-sm"
                  : "bg-dark-card border-dark-border hover:border-slate-600"
              }`}
            >
              {t.icon}
              <Text className={`text-xs font-bold ${isActive ? "text-white" : "text-slate-400"}`}>
                {t.label}
              </Text>
              {t.badge && (
                <View
                  className={`px-1.5 py-0.2 rounded text-[9px] ${
                    isActive ? "bg-purple-800 text-white" : "bg-dark-bg text-slate-400 border border-dark-border"
                  }`}
                >
                  <Text
                    className={`text-[9px] font-mono font-bold ${
                      isActive ? "text-white" : "text-slate-300"
                    }`}
                  >
                    {t.badge}
                  </Text>
                </View>
              )}
            </TouchableOpacity>
          );
        })}
      </View>

      {/* ── Tab Content Views ───────────────────────────────── */}
      {activeTab === "overview" && <AttendanceOverviewTab compId={selectedCompId} />}
      {activeTab === "directory" && <AttendanceDirectoryTab compId={selectedCompId} />}
      {activeTab === "leave" && <AttendanceLeaveTab compId={selectedCompId} />}
      {activeTab === "quality" && <AttendanceQualityTab />}
    </ScrollView>
  );
}
