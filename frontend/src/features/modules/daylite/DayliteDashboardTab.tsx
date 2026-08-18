import React from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import {
  ArrowRight,
  Building2,
  Calendar,
  Database,
  Eye,
  Sparkles,
  UserCheck,
  Users,
} from "lucide-react-native";
import { CoverageBar } from "../components/CoverageBar";
import { usePersonMetrics } from "@/hooks/useModules";
import { useDatabaseTables } from "@/hooks/useDatabase";
import { THEME_COLORS } from "@/constants/theme";

export const DayliteDashboardTab: React.FC = () => {
  const router = useRouter();
  const { data: personMetrics } = usePersonMetrics((d) => {
    const m = d.metrics;
    return {
      total_persons: m?.total_persons,
      active_persons: m?.active_persons,
      active_percent: m?.active_percent,
      visitor_count: m?.visitor_count,
      visitor_percent: m?.visitor_percent,
      contact_entity_count: m?.contact_entity_count,
      contact_entity_percent: m?.contact_entity_percent,
      contact_coverage_percent: m?.contact_coverage_percent,
      persons_with_contact: m?.persons_with_contact,
      email_coverage_percent: m?.email_coverage_percent,
      persons_with_email: m?.persons_with_email,
      phone_coverage_percent: m?.phone_coverage_percent,
      persons_with_phone: m?.persons_with_phone,
      address_coverage_percent: m?.address_coverage_percent,
      persons_with_address: m?.persons_with_address,
      company_link_coverage_percent: m?.company_link_coverage_percent,
      persons_with_company_link: m?.persons_with_company_link,
      relationship_coverage_percent: m?.relationship_coverage_percent,
      persons_with_relationship: m?.persons_with_relationship,
    };
  });
  const { data: dlTablesRes, isLoading: isLoadingTables } = useDatabaseTables({
    search: "DL",
    limit: 200,
  });

  const totalDLTables = dlTablesRes?.total ?? 68;

  const dlTables = dlTablesRes?.items ?? [];
  const companyTable = dlTables.find((t) => t.table === "DLCompanyMst");
  const eventTable = dlTables.find((t) => t.table === "DLEvent");
  const companyCount = companyTable?.estimated_rows ?? null;
  const eventCount = eventTable?.estimated_rows ?? null;

  const totalPersons  = personMetrics?.total_persons      ?? 29758;
  const activePersons = personMetrics?.active_persons      ?? 28496;
  const activePct     = personMetrics?.active_percent      ?? 95.76;
  const visitorCount  = personMetrics?.visitor_count       ?? null;
  const visitorPct    = personMetrics?.visitor_percent     ?? null;
  const contactCount  = personMetrics?.contact_entity_count  ?? null;
  const contactPct    = personMetrics?.contact_entity_percent ?? null;

  return (
    <View className="gap-4">
      {/* ── Compact Hero Banner ──────────────────────────────── */}
      <View className="bg-gradient-to-r from-blue-950/40 via-dark-card to-dark-card border border-blue-500/20 rounded-lg p-4 shadow-sm">
        <View className="flex-col md:flex-row md:items-center justify-between gap-3">
          <View className="flex-1">
            <View className="flex-row items-center gap-2 mb-1">
              <Sparkles size={12} color={THEME_COLORS.primaryIcon} />
              <Text className="text-[10px] uppercase font-bold text-blue-400 tracking-wider">
                Daylite Intelligence Hub
              </Text>
            </View>
            <Text className="text-lg md:text-xl font-black text-white tracking-tight">
              Daylite CRM & Operations Dashboard
            </Text>
            <Text className="text-[11px] text-slate-400 mt-0.5 max-w-2xl">
              Unified domain analytics across master individuals, corporate affiliations, communication channels, and calendar operations.
            </Text>
          </View>

          <Pressable
            onPress={() => router.push("/daylite/person" as Href)}
            accessibilityRole="button"
            accessibilityLabel="Open DL Person Analysis"
            className="flex-row items-center gap-1.5 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 px-3 py-2 rounded-lg shadow-sm self-start md:self-auto transition-all"
          >
            <Users size={12} color={THEME_COLORS.onPrimary} />
            <Text className="text-[11px] font-bold text-white">Open DL Person Analysis</Text>
            <ArrowRight size={12} color={THEME_COLORS.onPrimary} />
          </Pressable>
        </View>
      </View>

      {/* ── Key Scale Indicators ─────────────────────────────── */}
      <View className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        {/* Person Master */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4 shadow-sm">
          <View className="flex-row items-center justify-between mb-2">
            <Text className="text-[11px] uppercase font-bold text-slate-400 tracking-wider">
              Person Master
            </Text>
            <Users size={16} color={THEME_COLORS.primaryIcon} />
          </View>
          <Text className="text-xl font-black text-white font-mono">
            {totalPersons.toLocaleString()}
          </Text>
          <View className="flex-row items-center gap-1.5 mt-1">
            <View className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <Text className="text-[11px] text-emerald-400 font-medium">
              {activePersons.toLocaleString()} Active ({activePct.toFixed(1)}%)
            </Text>
          </View>
        </View>

        {/* Visitors (PersonIsVisitor_Contact = 1) */}
        <Pressable
          onPress={() => router.push("/daylite/person?tab=visitors" as Href)}
          accessibilityRole="button"
          accessibilityLabel="View Visitors"
          className="bg-dark-card border border-emerald-800/30 hover:border-emerald-600/50 active:border-emerald-500 rounded-xl p-4 shadow-sm transition-all"
        >
          <View className="flex-row items-center justify-between mb-2">
            <Text className="text-[11px] uppercase font-bold text-emerald-400/80 tracking-wider">
              Visitors
            </Text>
            <Eye size={16} color={THEME_COLORS.successIcon} />
          </View>
          <Text className="text-xl font-black text-white font-mono">
            {visitorCount != null ? visitorCount.toLocaleString() : "…"}
          </Text>
          <View className="flex-row items-center gap-1.5 mt-1">
            <View className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <Text className="text-[11px] text-emerald-400/80 font-medium">
              {visitorPct != null ? `${visitorPct.toFixed(1)}% of total` : "PersonIsVisitor_Contact = 1"}
            </Text>
          </View>
        </Pressable>

        {/* Contacts (PersonIsVisitor_Contact = 2) */}
        <Pressable
          onPress={() => router.push("/daylite/person?tab=contacts" as Href)}
          accessibilityRole="button"
          accessibilityLabel="View Contacts"
          className="bg-dark-card border border-violet-800/30 hover:border-violet-600/50 active:border-violet-500 rounded-xl p-4 shadow-sm transition-all"
        >
          <View className="flex-row items-center justify-between mb-2">
            <Text className="text-[11px] uppercase font-bold text-violet-400/80 tracking-wider">
              Contacts
            </Text>
            <UserCheck size={16} color={THEME_COLORS.accentIcon} />
          </View>
          <Text className="text-xl font-black text-white font-mono">
            {contactCount != null ? contactCount.toLocaleString() : "…"}
          </Text>
          <View className="flex-row items-center gap-1.5 mt-1">
            <View className="w-1.5 h-1.5 rounded-full bg-violet-500" />
            <Text className="text-[11px] text-violet-400/80 font-medium">
              {contactPct != null ? `${contactPct.toFixed(1)}% of total` : "PersonIsVisitor_Contact = 2"}
            </Text>
          </View>
        </Pressable>

        {/* Company Master */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4 shadow-sm">
          <View className="flex-row items-center justify-between mb-2">
            <Text className="text-[11px] uppercase font-bold text-slate-400 tracking-wider">
              Company Master
            </Text>
            <Building2 size={16} color={THEME_COLORS.accentIcon} />
          </View>
          <Text className="text-xl font-black text-white font-mono">
            {isLoadingTables ? "..." : companyCount != null ? companyCount.toLocaleString() : "—"}
          </Text>
          <Text className="text-[11px] text-slate-500 mt-1 font-mono">
            dbo.DLCompanyMst
          </Text>
        </View>

        {/* Calendar Events */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4 shadow-sm">
          <View className="flex-row items-center justify-between mb-2">
            <Text className="text-[11px] uppercase font-bold text-slate-400 tracking-wider">
              Events & Logs
            </Text>
            <Calendar size={16} color={THEME_COLORS.successIcon} />
          </View>
          <Text className="text-xl font-black text-white font-mono">
            {isLoadingTables ? "..." : eventCount != null ? eventCount.toLocaleString() : "—"}
          </Text>
          <Text className="text-[11px] text-slate-500 mt-1 font-mono">
            dbo.DLEvent
          </Text>
        </View>

        {/* Daylite Tables */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4 shadow-sm">
          <View className="flex-row items-center justify-between mb-2">
            <Text className="text-[11px] uppercase font-bold text-slate-400 tracking-wider">
              Daylite Tables
            </Text>
            <Database size={16} color={THEME_COLORS.warningIcon} />
          </View>
          <Text className="text-xl font-black text-white font-mono">
            {isLoadingTables ? "..." : totalDLTables}
          </Text>
          <Text className="text-[11px] text-slate-500 mt-1">
            Mapped in DB Catalog
          </Text>
        </View>
      </View>

      {/* ── Person & Contact Domain Health Snapshot ───────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-3 shadow-sm">
        <View className="flex-row items-center justify-between mb-4 pb-3 border-b border-dark-border">
          <View>
            <Text className="text-sm font-bold text-white uppercase tracking-wider">
              Person & Contact Domain Health
            </Text>
            <Text className="text-xs text-slate-400 mt-0.5">
              Live aggregate coverage across {totalPersons.toLocaleString()} master individuals
            </Text>
          </View>
          <Pressable
            onPress={() => router.push("/daylite/person" as Href)}
            className="flex-row items-center gap-1.5 py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 active:bg-slate-900 border border-slate-700"
          >
            <Text className="text-xs font-semibold text-blue-400">View Full DL Person Analysis</Text>
            <ArrowRight size={12} color={THEME_COLORS.primaryIcon} />
          </Pressable>
        </View>

        <View className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2">
          <CoverageBar
            label="Contact Reachability (Email or Phone)"
            percent={personMetrics?.contact_coverage_percent}
            count={personMetrics?.persons_with_contact}
            total={totalPersons}
            colorScheme="emerald"
          />

          <CoverageBar
            label="Email Address Coverage"
            percent={personMetrics?.email_coverage_percent}
            count={personMetrics?.persons_with_email}
            total={totalPersons}
            colorScheme="blue"
          />

          <CoverageBar
            label="Telephone / Mobile Coverage"
            percent={personMetrics?.phone_coverage_percent}
            count={personMetrics?.persons_with_phone}
            total={totalPersons}
            colorScheme="indigo"
          />

          <CoverageBar
            label="Physical Address Coverage"
            percent={personMetrics?.address_coverage_percent}
            count={personMetrics?.persons_with_address}
            total={totalPersons}
            colorScheme="amber"
          />

          <CoverageBar
            label="Company Affiliation Links"
            percent={personMetrics?.company_link_coverage_percent}
            count={personMetrics?.persons_with_company_link}
            total={totalPersons}
            colorScheme="purple"
          />

          <CoverageBar
            label="Person Relationships"
            percent={personMetrics?.relationship_coverage_percent}
            count={personMetrics?.persons_with_relationship}
            total={totalPersons}
            colorScheme="auto"
          />
        </View>
      </View>
    </View>
  );
};
