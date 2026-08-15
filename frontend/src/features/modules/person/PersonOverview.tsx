import React from "react";
import { Text, View } from "react-native";
import { Building2, CheckCircle2, Mail, MapPin, Phone, Users, UserX } from "lucide-react-native";
import type { PersonModuleMetricsResponse } from "@/types/modules.types";
import { THEME_COLORS } from "@/constants/theme";

interface PersonOverviewProps {
  metricsResponse?: PersonModuleMetricsResponse;
  isLoading?: boolean;
}

export const PersonOverview: React.FC<PersonOverviewProps> = ({
  metricsResponse,
  isLoading = false,
}) => {
  const metrics = metricsResponse?.metrics;

  if (isLoading || !metrics) {
    return (
      <View className="gap-3">
        <View className="h-20 bg-dark-card border border-dark-border rounded-lg animate-pulse" />
        <View className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <View className="h-16 bg-dark-card border border-dark-border rounded-lg animate-pulse" />
          <View className="h-16 bg-dark-card border border-dark-border rounded-lg animate-pulse" />
          <View className="h-16 bg-dark-card border border-dark-border rounded-lg animate-pulse" />
        </View>
      </View>
    );
  }

  const total = metrics.total_persons ?? 0;
  const active = metrics.active_persons ?? 0;
  const inactive = metrics.inactive_persons ?? 0;
  const activePct = metrics.active_percent ?? 0;

  return (
    <View className="gap-3.5">
      {/* ── Compact Master Record Banner ──────────────────────── */}
      <View className="bg-gradient-to-r from-blue-950/40 via-dark-card to-dark-card border border-blue-500/20 rounded-xl p-4 shadow-sm">
        <View className="flex-col sm:flex-row sm:items-center justify-between gap-3">
          <View className="flex-1">
            <View className="flex-row items-center gap-1.5 mb-0.5">
              <Users size={14} color={THEME_COLORS.primaryIcon} />
              <Text className="text-[10px] uppercase font-bold text-blue-400 tracking-wider">
                Master Person Directory
              </Text>
            </View>
            <Text className="text-2xl md:text-3xl font-black text-white tracking-tight font-mono">
              {total.toLocaleString()}
            </Text>
            <Text className="text-[11px] text-slate-400 mt-0.5">
              Master entities registered in <Text className="font-mono text-slate-300">dbo.DLPersonMst</Text>
            </Text>
          </View>

          {/* Active vs Inactive Pill Stack */}
          <View className="flex-row items-center gap-2">
            <View className="bg-emerald-950/40 border border-emerald-800/50 px-3 py-1.5 rounded-lg">
              <View className="flex-row items-center gap-1 mb-0.5">
                <CheckCircle2 size={11} color={THEME_COLORS.success} />
                <Text className="text-[9px] uppercase font-bold text-emerald-400 tracking-wider">
                  Active
                </Text>
              </View>
              <Text className="text-sm font-mono font-bold text-emerald-300">
                {active.toLocaleString()}
              </Text>
              <Text className="text-[9px] text-emerald-400/80">
                {activePct.toFixed(1)}%
              </Text>
            </View>

            <View className="bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg">
              <View className="flex-row items-center gap-1 mb-0.5">
                <UserX size={11} color={THEME_COLORS.textMuted} />
                <Text className="text-[9px] uppercase font-bold text-slate-400 tracking-wider">
                  Inactive
                </Text>
              </View>
              <Text className="text-sm font-mono font-bold text-slate-300">
                {inactive.toLocaleString()}
              </Text>
              <Text className="text-[9px] text-slate-500">
                {(100 - activePct).toFixed(1)}%
              </Text>
            </View>
          </View>
        </View>
      </View>

      {/* ── Key Domain Snapshot Cards ───────────────────────── */}
      <View className="flex-col md:flex-row gap-3">
        {/* Contact Snapshot */}
        <View className="flex-1 bg-dark-card border border-dark-border rounded-lg p-3">
          <View className="flex-row items-center justify-between mb-2">
            <View className="flex-row items-center gap-1.5">
              <View className="w-6 h-6 rounded bg-blue-600/10 items-center justify-center border border-blue-500/20">
                <Phone size={12} color={THEME_COLORS.primaryIcon} />
              </View>
              <View>
                <Text className="text-xs font-bold text-slate-200">Communication</Text>
                <Text className="text-[9px] text-slate-500">Channels</Text>
              </View>
            </View>
            <Text className="text-xs font-mono font-black text-emerald-400">
              {metrics.contact_coverage_percent?.toFixed(1) ?? "0.0"}%
            </Text>
          </View>

          <View className="gap-1 pt-1.5 border-t border-dark-border/60">
            <View className="flex-row items-center justify-between">
              <View className="flex-row items-center gap-1">
                <Mail size={10} color={THEME_COLORS.textMuted} />
                <Text className="text-[11px] text-slate-400">Emails</Text>
              </View>
              <Text className="text-[11px] font-mono font-bold text-slate-300">
                {metrics.email_coverage_percent?.toFixed(1) ?? "0.0"}%
              </Text>
            </View>

            <View className="flex-row items-center justify-between">
              <View className="flex-row items-center gap-1">
                <Phone size={10} color={THEME_COLORS.textMuted} />
                <Text className="text-[11px] text-slate-400">Phones</Text>
              </View>
              <Text className="text-[11px] font-mono font-bold text-slate-300">
                {metrics.phone_coverage_percent?.toFixed(1) ?? "0.0"}%
              </Text>
            </View>
          </View>
        </View>

        {/* Address Snapshot */}
        <View className="flex-1 bg-dark-card border border-dark-border rounded-lg p-3">
          <View className="flex-row items-center justify-between mb-2">
            <View className="flex-row items-center gap-1.5">
              <View className="w-6 h-6 rounded bg-emerald-600/10 items-center justify-center border border-emerald-500/20">
                <MapPin size={12} color={THEME_COLORS.success} />
              </View>
              <View>
                <Text className="text-xs font-bold text-slate-200">Physical Address</Text>
                <Text className="text-[9px] text-slate-500">Location Details</Text>
              </View>
            </View>
            <Text className="text-xs font-mono font-black text-amber-400">
              {metrics.address_coverage_percent?.toFixed(1) ?? "0.0"}%
            </Text>
          </View>

          <View className="gap-1 pt-1.5 border-t border-dark-border/60">
            <View className="flex-row items-center justify-between">
              <Text className="text-[11px] text-slate-400">With Address</Text>
              <Text className="text-[11px] font-mono font-bold text-slate-300">
                {metrics.persons_with_address?.toLocaleString() ?? "0"}
              </Text>
            </View>
            <View className="flex-row items-center justify-between">
              <Text className="text-[11px] text-slate-400">Address Records</Text>
              <Text className="text-[11px] font-mono font-bold text-slate-300">
                {metrics.total_addresses?.toLocaleString() ?? "0"}
              </Text>
            </View>
          </View>
        </View>

        {/* Organization Linkage Snapshot */}
        <View className="flex-1 bg-dark-card border border-dark-border rounded-lg p-3">
          <View className="flex-row items-center justify-between mb-2">
            <View className="flex-row items-center gap-1.5">
              <View className="w-6 h-6 rounded bg-purple-600/10 items-center justify-center border border-purple-500/20">
                <Building2 size={12} color={THEME_COLORS.accentIcon} />
              </View>
              <View>
                <Text className="text-xs font-bold text-slate-200">Affiliations</Text>
                <Text className="text-[9px] text-slate-500">Company Links</Text>
              </View>
            </View>
            <Text className="text-xs font-mono font-black text-blue-400">
              {metrics.company_link_coverage_percent?.toFixed(1) ?? "0.0"}%
            </Text>
          </View>

          <View className="gap-1 pt-1.5 border-t border-dark-border/60">
            <View className="flex-row items-center justify-between">
              <Text className="text-[11px] text-slate-400">Company Linked</Text>
              <Text className="text-[11px] font-mono font-bold text-slate-300">
                {metrics.persons_with_company_link?.toLocaleString() ?? "0"}
              </Text>
            </View>
            <View className="flex-row items-center justify-between">
              <Text className="text-[11px] text-slate-400">Total Link Records</Text>
              <Text className="text-[11px] font-mono font-bold text-slate-300">
                {metrics.total_company_links?.toLocaleString() ?? "0"}
              </Text>
            </View>
          </View>
        </View>
      </View>
    </View>
  );
};
