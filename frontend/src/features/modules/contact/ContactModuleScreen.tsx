import React, { useState } from "react";
import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import {
  AtSign,
  Mail,
  PhoneCall,
  RefreshCw,
  Users,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import { useContactOverview, useContactQuality } from "@/hooks/useContact";
import { ContactDirectoryTab } from "./ContactDirectoryTab";
import { ContactEmailQualityTab } from "./ContactEmailQualityTab";
import { ContactOverviewTab } from "./ContactOverviewTab";
import { ContactPhoneQualityTab } from "./ContactPhoneQualityTab";

type TabKey = "overview" | "directory" | "email_quality" | "phone_quality";

export const ContactModuleScreen: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabKey>("overview");

  const {
    data: overview,
    refetch: refetchOverview,
  } = useContactOverview();

  const {
    data: quality,
    refetch: refetchQuality,
  } = useContactQuality();

  const handleRefreshAll = () => {
    refetchOverview();
    refetchQuality();
  };

  const tabs: { key: TabKey; label: string; icon: React.ReactNode; badge?: string | number }[] = [
    {
      key: "overview",
      label: "Overview",
      icon: <AtSign size={14} color={activeTab === "overview" ? "#ffffff" : "#94a3b8"} />,
      badge: overview ? `${overview.total_active_employees} Staff` : undefined,
    },
    {
      key: "directory",
      label: "Contact Directory",
      icon: <Users size={14} color={activeTab === "directory" ? "#ffffff" : "#94a3b8"} />,
    },
    {
      key: "email_quality",
      label: "Email Quality",
      icon: <Mail size={14} color={activeTab === "email_quality" ? "#ffffff" : "#94a3b8"} />,
      badge: quality ? `${quality.overall_health_score}%` : undefined,
    },
    {
      key: "phone_quality",
      label: "Phone & Address Quality",
      icon: <PhoneCall size={14} color={activeTab === "phone_quality" ? "#ffffff" : "#94a3b8"} />,
      badge: quality?.critical_issues_count ? `${quality.critical_issues_count} Critical` : undefined,
    },
  ];

  return (
    <ScrollView className="flex-1 bg-dark-bg p-3 md:p-4" showsVerticalScrollIndicator={false}>
      {/* ── Compact Header Banner ──────────────────────────── */}
      <View className="flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
        <View className="flex-1 flex-row items-center gap-3">
          <View className="bg-emerald-950/80 border border-emerald-800/60 px-2 py-0.5 rounded">
            <Text className="text-[10px] font-mono font-bold text-emerald-400">CONTACT</Text>
          </View>
          <View>
            <Text className="text-lg md:text-xl font-black text-white leading-tight">Contact & Email Analysis</Text>
            <Text className="text-[11px] text-slate-400" numberOfLines={1}>
              Corporate email provisioning, mobile phones, emergency contacts, and address verification.
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
      {activeTab === "overview" && <ContactOverviewTab />}
      {activeTab === "directory" && <ContactDirectoryTab />}
      {activeTab === "email_quality" && <ContactEmailQualityTab />}
      {activeTab === "phone_quality" && <ContactPhoneQualityTab />}
    </ScrollView>
  );
};
