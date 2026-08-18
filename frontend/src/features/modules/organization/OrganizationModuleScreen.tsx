import React, { useState } from "react";
import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import {
  Building2,
  GitBranch,
  Layers,
  Network,
  RefreshCw,
  ShieldAlert,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import {
  useOrgHierarchy,
  useOrgOverview,
  useOrgQuality,
  useOrgReportingTree,
} from "@/hooks/useOrganization";
import { OrgHierarchyTab } from "./OrgHierarchyTab";
import { OrgOverviewTab } from "./OrgOverviewTab";
import { OrgQualityTab } from "./OrgQualityTab";
import { OrgReportingTab } from "./OrgReportingTab";
import { OrgUnitsCatalogTab } from "./OrgUnitsCatalogTab";

type TabKey = "overview" | "hierarchy" | "reporting" | "quality" | "catalog";

export const OrganizationModuleScreen: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>("overview");

  const {
    data: overview,
    isLoading: isOverviewLoading,
    refetch: refetchOverview,
  } = useOrgOverview();

  const {
    data: hierarchy,
    isLoading: isHierarchyLoading,
    refetch: refetchHierarchy,
  } = useOrgHierarchy();

  const {
    data: reporting,
    isLoading: isReportingLoading,
    refetch: refetchReporting,
  } = useOrgReportingTree();

  const {
    data: quality,
    isLoading: isQualityLoading,
    refetch: refetchQuality,
  } = useOrgQuality();

  const handleRefreshAll = () => {
    refetchOverview();
    refetchHierarchy();
    refetchReporting();
    refetchQuality();
  };

  const tabs: { key: TabKey; label: string; icon: React.ReactNode; badge?: string | number }[] = [
    {
      key: "overview",
      label: "Overview",
      icon: <Building2 size={12} color={activeTab === "overview" ? "#ffffff" : "#94a3b8"} />,
    },
    {
      key: "hierarchy",
      label: "Relationship Map",
      icon: <GitBranch size={12} color={activeTab === "hierarchy" ? "#ffffff" : "#94a3b8"} />,
      badge: hierarchy ? `${hierarchy.total_active_employees} Staff` : undefined,
    },
    {
      key: "reporting",
      label: "Reporting Lines",
      icon: <Network size={12} color={activeTab === "reporting" ? "#ffffff" : "#94a3b8"} />,
      badge: reporting ? `${reporting.total_assigned_managers} Leads` : undefined,
    },
    {
      key: "quality",
      label: "Data Quality",
      icon: <ShieldAlert size={12} color={activeTab === "quality" ? "#ffffff" : "#94a3b8"} />,
      badge: quality?.critical_issues_count ? `${quality.critical_issues_count} Critical` : undefined,
    },
    {
      key: "catalog",
      label: "Master Units",
      icon: <Layers size={12} color={activeTab === "catalog" ? "#ffffff" : "#94a3b8"} />,
    },
  ];

  return (
    <ScrollView className="flex-1 bg-dark-bg p-3 md:p-4" showsVerticalScrollIndicator={false}>
      {/* ── Compact Header Banner ──────────────────────────── */}
      <View className="flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
        <View className="flex-1 flex-row items-center gap-3">
          <View className="bg-blue-950/80 border border-blue-800/60 px-2 py-0.5 rounded">
            <Text className="text-[10px] font-mono font-bold text-blue-400">ORGANIZATION</Text>
          </View>
          <View>
            <Text className="text-lg md:text-xl font-black text-white leading-tight">Organization Structure</Text>
            <Text className="text-[11px] text-slate-400" numberOfLines={1}>
              Corporate entities, manufacturing locations, main functional divisions, operations, and designations.
            </Text>
          </View>
        </View>

        <TouchableOpacity
          onPress={handleRefreshAll}
          className="bg-dark-card border border-dark-border px-2.5 py-1.5 rounded-lg flex-row items-center gap-1.5 self-start md:self-auto active:bg-slate-800"
        >
          <RefreshCw size={12} color={THEME_COLORS.primaryIcon} />
          <Text className="text-[11px] font-bold text-slate-300">Sync</Text>
        </TouchableOpacity>
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
                  ? "bg-blue-600 border-blue-400 shadow-sm"
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
                    isActive ? "bg-blue-800 text-white" : "bg-dark-bg text-slate-400 border border-dark-border"
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
      {activeTab === "overview" && (
        <OrgOverviewTab overview={overview} isLoading={isOverviewLoading} />
      )}

      {activeTab === "hierarchy" && (
        <OrgHierarchyTab hierarchy={hierarchy} isLoading={isHierarchyLoading} />
      )}

      {activeTab === "reporting" && (
        <OrgReportingTab reporting={reporting} isLoading={isReportingLoading} />
      )}

      {activeTab === "quality" && (
        <OrgQualityTab quality={quality} isLoading={isQualityLoading} />
      )}

      {activeTab === "catalog" && (
        <OrgUnitsCatalogTab />
      )}
    </ScrollView>
  );
};
