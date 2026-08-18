import React, { useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import {
  Briefcase,
  GitBranch,
  RefreshCw,
  ShieldAlert,
  Users,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import {
  useEmployeeOverview,
  useEmployeeQuality,
  useEmployeeStructure,
} from "@/hooks/useEmployee";
import { EmployeeDetailModal } from "./EmployeeDetailModal";
import { EmployeeOverviewTab } from "./EmployeeOverviewTab";
import { EmployeeQualityTab } from "./EmployeeQualityTab";
import { EmployeeRosterTab } from "./EmployeeRosterTab";
import { EmployeeStructureTab } from "./EmployeeStructureTab";

export type EmployeeTabType = "overview" | "structure" | "quality" | "roster";

const COMPANY_OPTIONS = [
  { id: undefined, label: "All", code: "ALL" },
  { id: 1, label: "AIL", code: "AIL" },
  { id: 2, label: "ASCL", code: "ASCL" },
];

export const EmployeeModuleScreen: React.FC = () => {
  const [activeTab, setActiveTab] = useState<EmployeeTabType>("overview");
  const [selectedEmpId, setSelectedEmpId] = useState<number | null>(null);
  const [selectedCompId, setSelectedCompId] = useState<number | undefined>(undefined);

  const {
    data: overviewData,
    isLoading: loadingOverview,
    refetch: refetchOverview,
  } = useEmployeeOverview(selectedCompId);

  const {
    data: structureData,
    isLoading: loadingStructure,
    refetch: refetchStructure,
  } = useEmployeeStructure();

  const {
    data: qualityData,
    isLoading: loadingQuality,
    refetch: refetchQuality,
  } = useEmployeeQuality();

  const handleRefresh = () => {
    if (activeTab === "overview") refetchOverview();
    else if (activeTab === "structure") refetchStructure();
    else if (activeTab === "quality") refetchQuality();
  };

  return (
    <ScrollView className="flex-1 bg-dark-bg p-3 md:p-4" showsVerticalScrollIndicator={false}>
      {/* ── Compact Header Banner ──────────────────────────── */}
      <View className="flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
        <View className="flex-1 flex-row items-center gap-3">
          <View className="bg-blue-950/80 border border-blue-800/60 px-2 py-0.5 rounded">
            <Text className="text-[10px] font-mono font-bold text-blue-400">INTELLIGENCE DOMAIN</Text>
          </View>
          <View>
            <Text className="text-lg md:text-xl font-black text-white leading-tight">Employee & Workforce Intelligence</Text>
            <Text className="text-[11px] text-slate-400" numberOfLines={1}>
              Automated discovery, structural hierarchy, position history, authentication linkage, and multi-rule data quality audit.
            </Text>
          </View>
        </View>

        <View className="flex-row items-center gap-2 self-start md:self-auto">
            {/* Company Selector Pills */}
            <View className="flex-row items-center bg-dark-card border border-dark-border p-0.5 rounded-lg">
              {COMPANY_OPTIONS.map((c) => {
                const isSelected = selectedCompId === c.id;
                return (
                  <Pressable
                    key={c.code}
                    onPress={() => setSelectedCompId(c.id)}
                    className={`px-2 py-1 rounded-md transition-all ${
                      isSelected ? "bg-blue-600 border border-blue-400" : "border-transparent"
                    }`}
                  >
                    <Text
                      className={`text-[11px] font-bold font-mono ${
                        isSelected ? "text-white" : "text-slate-400"
                      }`}
                    >
                      {c.label}
                    </Text>
                  </Pressable>
                );
              })}
            </View>

            <Pressable
              onPress={handleRefresh}
              accessibilityRole="button"
              accessibilityLabel="Refresh workforce analytics"
              className="flex-row items-center gap-1.5 bg-dark-card border border-dark-border px-2.5 py-1.5 rounded-lg active:bg-slate-800 transition-all"
            >
              <RefreshCw size={12} color={THEME_COLORS.primaryIcon} />
              <Text className="text-[11px] font-bold text-slate-300">Sync</Text>
            </Pressable>
          </View>
        </View>


        {/* ── Navigation Tabs ────────────────────────────────── */}
        <View className="flex-row flex-wrap items-center gap-1.5 border-b border-dark-border pb-2 mb-3">
          {[
            {
              id: "overview",
              label: "Workforce Overview",
              icon: Users,
              badge: overviewData?.status_counts.active
                ? `${overviewData.status_counts.active.toLocaleString()} Active`
                : undefined,
            },
            {
              id: "structure",
              label: "Structure & Graph",
              icon: GitBranch,
              badge: structureData?.tables ? `${structureData.tables.length} Tables` : undefined,
            },
            {
              id: "quality",
              label: "Data Quality Audit",
              icon: ShieldAlert,
              badge: qualityData?.critical_issues_count
                ? `${qualityData.critical_issues_count} Critical`
                : undefined,
              badgeColor: qualityData?.critical_issues_count ? "rose" : "blue",
            },
            {
              id: "roster",
              label: "Employee Directory",
              icon: Briefcase,
            },
          ].map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <Pressable
                key={tab.id}
                onPress={() => setActiveTab(tab.id as EmployeeTabType)}
                className={`flex-row items-center gap-1.5 px-3 py-1.5 rounded-lg border transition-all ${
                  active
                    ? "bg-blue-600 border-blue-400 shadow-sm"
                    : "bg-dark-card border-dark-border hover:border-slate-600"
                }`}
              >
                <Icon size={12} color={active ? "#ffffff" : "#94a3b8"} />
                <Text className={`text-xs font-bold ${active ? "text-white" : "text-slate-400"}`}>
                  {tab.label}
                </Text>
                {tab.badge ? (
                  <View
                    className={`px-1.5 py-0.2 rounded text-[9px] ${
                      active
                        ? "bg-blue-800 text-white"
                        : tab.badgeColor === "rose"
                        ? "bg-rose-950/50 border border-rose-800 text-rose-300"
                        : "bg-dark-bg text-slate-400 border border-dark-border"
                    }`}
                  >
                    <Text
                      className={`text-[9px] font-mono font-bold ${
                        active
                          ? "text-white"
                          : tab.badgeColor === "rose"
                          ? "text-rose-300"
                          : "text-slate-300"
                      }`}
                    >
                      {tab.badge}
                    </Text>
                  </View>
                ) : null}
              </Pressable>
            );
          })}
        </View>

      {/* ── Tab Content Area ─────────────────────────────────── */}
      <View className="flex-1">
        {activeTab === "overview" && (
          <EmployeeOverviewTab
            overview={overviewData}
            isLoading={loadingOverview}
            onSelectStatusFilter={(_st) => setActiveTab("roster")}
          />
        )}

        {activeTab === "structure" && (
          <EmployeeStructureTab
            structure={structureData}
            isLoading={loadingStructure}
          />
        )}

        {activeTab === "quality" && (
          <EmployeeQualityTab
            quality={qualityData}
            isLoading={loadingQuality}
          />
        )}

        {activeTab === "roster" && (
          <EmployeeRosterTab
            onSelectEmployee={(empId) => setSelectedEmpId(empId)}
            compId={selectedCompId}
          />
        )}

      </View>

      {/* ── 360° Employee Detail Dossier Modal ───────────────── */}
      <EmployeeDetailModal
        empId={selectedEmpId}
        onClose={() => setSelectedEmpId(null)}
      />
    </ScrollView>
  );
};
