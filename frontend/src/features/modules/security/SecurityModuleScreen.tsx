import React, { useState } from "react";
import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import {
  KeyRound,
  Lock,
  RefreshCw,
  ShieldCheck,
  Users,
} from "lucide-react-native";
import {
  useSecurityOverview,
  useSecurityQuality,
  useSecurityRoles,
} from "@/hooks/useSecurity";
import { SecurityOverviewTab } from "./SecurityOverviewTab";
import { SecurityQualityTab } from "./SecurityQualityTab";
import { SecurityRolesTab } from "./SecurityRolesTab";
import { SecurityUsersTab } from "./SecurityUsersTab";

type TabKey = "overview" | "users" | "roles" | "quality";

export const SecurityModuleScreen: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>("overview");

  const {
    data: overview,
    refetch: refetchOverview,
  } = useSecurityOverview();

  const {
    data: rolesData,
    refetch: refetchRoles,
  } = useSecurityRoles();

  const {
    data: quality,
    refetch: refetchQuality,
  } = useSecurityQuality();

  const handleRefreshAll = () => {
    refetchOverview();
    refetchRoles();
    refetchQuality();
  };

  const tabs: { key: TabKey; label: string; icon: React.ReactNode; badge?: string | number }[] = [
    {
      key: "overview",
      label: "Overview",
      icon: <Lock size={12} color={activeTab === "overview" ? "#ffffff" : "#94a3b8"} />,
      badge: overview?.account_metrics ? `${overview.account_metrics.active_users} Active` : undefined,
    },
    {
      key: "users",
      label: "User Accounts",
      icon: <Users size={12} color={activeTab === "users" ? "#ffffff" : "#94a3b8"} />,
    },
    {
      key: "roles",
      label: "Roles & Rights",
      icon: <KeyRound size={12} color={activeTab === "roles" ? "#ffffff" : "#94a3b8"} />,
      badge: rolesData ? `${rolesData.active_roles} Roles` : undefined,
    },
    {
      key: "quality",
      label: "Security Audit",
      icon: <ShieldCheck size={12} color={activeTab === "quality" ? "#ffffff" : "#94a3b8"} />,
      badge: quality ? `${quality.overall_security_score}%` : undefined,
    },
  ];

  return (
    <ScrollView className="flex-1 bg-dark-bg p-3 md:p-4" showsVerticalScrollIndicator={false}>
      {/* ── Compact Header Banner ──────────────────────────── */}
      <View className="flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
        <View className="flex-1 flex-row items-center gap-3">
          <View className="bg-purple-950/80 border border-purple-800/60 px-2 py-0.5 rounded">
            <Text className="text-[10px] font-mono font-bold text-purple-400">SECURITY</Text>
          </View>
          <View>
            <Text className="text-lg md:text-xl font-black text-white leading-tight">User, Login & Security Analysis</Text>
            <Text className="text-[11px] text-slate-400" numberOfLines={1}>
              Authentication accounts, employee-to-user links, RBAC, menu permissions, and data integrity.
            </Text>
          </View>
        </View>

        <TouchableOpacity
          onPress={handleRefreshAll}
          className="bg-dark-card border border-dark-border px-2.5 py-1.5 rounded-lg flex-row items-center gap-1.5 self-start md:self-auto active:bg-slate-800"
        >
          <RefreshCw size={12} color="#a855f7" />
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
      {activeTab === "overview" && <SecurityOverviewTab />}
      {activeTab === "users" && <SecurityUsersTab />}
      {activeTab === "roles" && <SecurityRolesTab />}
      {activeTab === "quality" && <SecurityQualityTab />}
    </ScrollView>
  );
};
