import React, { useState } from "react";
import { Pressable, Text, View } from "react-native";
import { Users, UserCheck, Eye } from "lucide-react-native";
import { PageContainer } from "@/components/layout/PageContainer";
import { PersonListView } from "@/features/modules/person/PersonListView";
import { usePersonMetrics } from "@/hooks/useModules";
import { THEME_COLORS } from "@/constants/theme";

type PersonTab = "all" | "visitors" | "contacts";

/**
 * Daylite Person Directory Route
 * Path: /daylite/person
 *
 * Renders three tabs backed by PersonIsVisitor_Contact:
 *   All Persons  → no visitor_contact filter
 *   Visitors     → PersonIsVisitor_Contact = 1
 *   Contacts     → PersonIsVisitor_Contact = 2
 *
 * Count badges come from the existing usePersonMetrics() hook
 * (visitor_count, contact_entity_count). No extra API call needed.
 */
export default function DaylitePersonDirectoryScreen() {
  const [activeTab, setActiveTab] = useState<PersonTab>("all");

  const { data: metricsRes } = usePersonMetrics();
  const metrics = metricsRes?.metrics;

  const visitorCount = metrics?.visitor_count;
  const contactCount = metrics?.contact_entity_count;
  const totalCount   = metrics?.total_persons;

  const tabs: {
    id: PersonTab;
    label: string;
    icon: React.ReactNode;
    count?: number | null;
    visitorContact?: 1 | 2;
    accentColor: string;
    badgeColor: string;
  }[] = [
    {
      id: "all",
      label: "All Persons",
      icon: <Users size={13} color={activeTab === "all" ? THEME_COLORS.primaryIcon : THEME_COLORS.textMuted} />,
      count: totalCount,
      visitorContact: undefined,
      accentColor: "border-blue-500",
      badgeColor: "bg-slate-800 border-slate-700 text-slate-300",
    },
    {
      id: "visitors",
      label: "Visitors",
      icon: <Eye size={13} color={activeTab === "visitors" ? THEME_COLORS.successIcon : THEME_COLORS.textMuted} />,
      count: visitorCount,
      visitorContact: 1,
      accentColor: "border-emerald-500",
      badgeColor: "bg-emerald-950/70 border-emerald-700/60 text-emerald-300",
    },
    {
      id: "contacts",
      label: "Contacts",
      icon: <UserCheck size={13} color={activeTab === "contacts" ? THEME_COLORS.accentIcon : THEME_COLORS.textMuted} />,
      count: contactCount,
      visitorContact: 2,
      accentColor: "border-violet-500",
      badgeColor: "bg-violet-950/70 border-violet-700/60 text-violet-300",
    },
  ];

  const currentTab = tabs.find((t) => t.id === activeTab)!;

  return (
    <PageContainer scrollable={false}>
      <View style={{ flex: 1, minHeight: 0 }} className="gap-0">
        {/* ── Segment Tab Bar ─────────────────────────────────── */}
        <View className="flex-row items-center border-b border-dark-border mb-3 gap-0.5">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <Pressable
                key={tab.id}
                onPress={() => setActiveTab(tab.id)}
                accessibilityRole="tab"
                accessibilityState={{ selected: isActive }}
                accessibilityLabel={tab.label}
                className={[
                  "flex-row items-center gap-1.5 px-3 py-2 border-b-2 transition-all",
                  isActive
                    ? `${tab.accentColor} bg-blue-500/5`
                    : "border-transparent hover:bg-slate-800/40",
                ].join(" ")}
              >
                {tab.icon}
                <Text
                  className={`text-xs font-bold ${
                    isActive ? "text-white" : "text-slate-400"
                  }`}
                >
                  {tab.label}
                </Text>

                {/* Live count badge */}
                {tab.count != null && (
                  <View
                    className={`px-1.5 py-0.5 rounded border ${tab.badgeColor}`}
                  >
                    <Text className="text-[9px] font-mono font-bold">
                      {tab.count.toLocaleString()}
                    </Text>
                  </View>
                )}
              </Pressable>
            );
          })}
        </View>

        {/* ── Person List (key forces re-mount on tab switch, resetting page/search) */}
        <View style={{ flex: 1, minHeight: 0 }}>
          <PersonListView
            key={activeTab}
            visitorContact={currentTab.visitorContact}
          />
        </View>
      </View>
    </PageContainer>
  );
}

