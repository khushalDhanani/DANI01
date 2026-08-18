import React, { useState } from "react";
import {
  ActivityIndicator,
  Modal,
  ScrollView,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Download,
  Info,
  PhoneCall,
  Search,
  ShieldAlert,
  ShieldCheck,
  X,
} from "lucide-react-native";
import { downloadContactQualityIssuesExport } from "@/api/contact.api";
import { THEME_COLORS } from "@/constants/theme";
import { useContactQuality, useContactQualityIssues } from "@/hooks/useContact";
import type { ContactQualityRuleResult } from "@/types/contact.types";

export function ContactPhoneQualityTab() {
  const { data: quality, isLoading, isError } = useContactQuality();
  const [selectedSeverity, setSelectedSeverity] = useState<string>("ALL");
  const [activeDrilldownRule, setActiveDrilldownRule] = useState<ContactQualityRuleResult | null>(null);
  const [drilldownSearch, setDrilldownSearch] = useState("");
  const [isExporting, setIsExporting] = useState(false);

  // Issues drilldown query
  const { data: issuesData, isLoading: isIssuesLoading } = useContactQualityIssues(
    activeDrilldownRule?.rule_code || "",
    drilldownSearch || undefined,
    50,
    0
  );

  if (isLoading) {
    return (
      <View className="py-8 items-center justify-center">
        <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
        <Text className="text-sm text-slate-400 mt-3 font-medium">Auditing phone & address quality rules...</Text>
      </View>
    );
  }

  if (isError || !quality) {
    return (
      <View className="py-8 items-center justify-center">
        <AlertTriangle size={36} color={THEME_COLORS.dangerIcon} />
        <Text className="text-sm text-red-400 mt-3 font-medium">Failed to load phone quality audit results.</Text>
      </View>
    );
  }

  // Filter phone & address related rules
  const phoneRuleCodes = [
    "MISSING_ALL_PHONES",
    "DUPLICATE_PRIMARY_PHONE",
    "MISSING_PRIMARY_PHONE",
    "INVALID_PHONE_FORMAT",
    "UNVERIFIED_PRIMARY_PHONE",
    "MISSING_EMERGENCY_CONTACT",
    "MISSING_PERMANENT_PINCODE",
    "MISSING_CORRESPONDENCE_PINCODE",
  ];

  const phoneRules = quality.rules.filter((r) => phoneRuleCodes.includes(r.rule_code));
  const filteredRules =
    selectedSeverity === "ALL"
      ? phoneRules
      : phoneRules.filter((r) => r.severity === selectedSeverity);

  const phoneCritical = phoneRules.filter((r) => r.severity === "CRITICAL").reduce((acc, r) => acc + r.issue_count, 0);
  const phoneWarning = phoneRules.filter((r) => r.severity === "WARNING").reduce((acc, r) => acc + r.issue_count, 0);
  const phoneInfo = phoneRules.filter((r) => r.severity === "INFO").reduce((acc, r) => acc + r.issue_count, 0);

  const handleExport = async (ruleCode: string) => {
    try {
      setIsExporting(true);
      await downloadContactQualityIssuesExport(ruleCode, drilldownSearch || undefined, "csv");
    } catch (err) {
      console.error("Export error:", err);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <ScrollView className="flex-1" showsVerticalScrollIndicator={false}>
      {/* Health Score Summary Card */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-3 mb-4 flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <View className="flex-row items-center gap-4 flex-1">
          <View className="w-16 h-16 rounded-full bg-emerald-950/80 border-2 border-emerald-500 items-center justify-center">
            <Text className="text-lg font-black text-emerald-400">{quality.overall_health_score}%</Text>
            <Text className="text-[9px] font-bold text-emerald-500 tracking-wider">HEALTH</Text>
          </View>
          <View className="flex-1">
            <View className="flex-row items-center gap-2 mb-1">
              <PhoneCall size={18} color={THEME_COLORS.successIcon} />
              <Text className="text-base font-bold text-white">Phone, ICE & Address Quality Audit</Text>
            </View>
            <Text className="text-xs text-slate-400 leading-relaxed">
              Auditing 10-digit primary mobile numbers, shared/duplicate phones, unverified numbers, In Case of Emergency (ICE) contacts, and postal PIN codes.
            </Text>
          </View>
        </View>

        {/* Severity Counters */}
        <View className="flex-row gap-2.5 self-start md:self-auto">
          <View className="bg-red-950/40 border border-red-800/40 px-3.5 py-2 rounded-xl items-center min-w-[70px]">
            <Text className="text-lg font-black text-red-400">{phoneCritical}</Text>
            <Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Critical</Text>
          </View>
          <View className="bg-amber-950/40 border border-amber-800/40 px-3.5 py-2 rounded-xl items-center min-w-[70px]">
            <Text className="text-lg font-black text-amber-400">{phoneWarning}</Text>
            <Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Warnings</Text>
          </View>
          <View className="bg-indigo-950/40 border border-indigo-800/40 px-3.5 py-2 rounded-xl items-center min-w-[70px]">
            <Text className="text-lg font-black text-indigo-400">{phoneInfo}</Text>
            <Text className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Info</Text>
          </View>
        </View>
      </View>

      {/* Severity Filter Pills */}
      <View className="flex-row gap-2 mb-4">
        {(["ALL", "CRITICAL", "WARNING", "INFO"] as const).map((sev) => {
          const isActive = selectedSeverity === sev;
          return (
            <TouchableOpacity
              key={sev}
              onPress={() => setSelectedSeverity(sev)}
              className={`px-3.5 py-1.5 rounded-lg border transition-all ${
                isActive
                  ? "bg-blue-600 border-blue-400"
                  : "bg-dark-card border-dark-border"
              }`}
            >
              <Text className={`text-xs font-bold ${isActive ? "text-white" : "text-slate-400"}`}>
                {sev === "ALL" ? `All Rules (${phoneRules.length})` : sev}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Rules List Grid */}
      <View className="gap-3 mb-4">
        {filteredRules.map((rule) => {
          const isPassed = rule.issue_count === 0;
          const isCritical = rule.severity === "CRITICAL";
          const isWarning = rule.severity === "WARNING";

          return (
            <View
              key={rule.rule_code}
              className={`bg-dark-card rounded-xl p-4 border transition-all ${
                isPassed
                  ? "border-emerald-900/60 bg-emerald-950/10"
                  : isCritical
                  ? "border-red-900/60 bg-red-950/10"
                  : isWarning
                  ? "border-amber-900/60 bg-amber-950/10"
                  : "border-indigo-900/60 bg-indigo-950/10"
              }`}
            >
              <View className="flex-row items-center justify-between mb-2">
                <View className="flex-row items-center gap-2.5 flex-1">
                  {isPassed ? (
                    <ShieldCheck size={18} color={THEME_COLORS.successIcon} />
                  ) : isCritical ? (
                    <ShieldAlert size={18} color={THEME_COLORS.dangerIcon} />
                  ) : isWarning ? (
                    <AlertTriangle size={18} color={THEME_COLORS.warningIcon} />
                  ) : (
                    <Info size={18} color={THEME_COLORS.accentIcon} />
                  )}
                  <View className="flex-1">
                    <Text className="text-sm font-bold text-white">{rule.rule_name}</Text>
                    <Text className="text-[11px] font-mono text-slate-500">[{rule.rule_code}]</Text>
                  </View>
                </View>

                {/* Badge Count */}
                <View
                  className={`px-2.5 py-1 rounded-md ${
                    isPassed
                      ? "bg-emerald-950 border border-emerald-800"
                      : isCritical
                      ? "bg-red-950 border border-red-800"
                      : isWarning
                      ? "bg-amber-950 border border-amber-800"
                      : "bg-indigo-950 border border-indigo-800"
                  }`}
                >
                  <Text
                    className={`text-xs font-mono font-bold ${
                      isPassed
                        ? "text-emerald-400"
                        : isCritical
                        ? "text-red-400"
                        : isWarning
                        ? "text-amber-400"
                        : "text-indigo-400"
                    }`}
                  >
                    {isPassed ? "PASS" : `${rule.issue_count} issues`}
                  </Text>
                </View>
              </View>

              <Text className="text-xs text-slate-400 mb-3 leading-relaxed">{rule.description}</Text>

              <View className="bg-dark-bg/80 border border-dark-border rounded-lg p-2.5 mb-3">
                <Text className="text-[10px] uppercase font-bold text-slate-500 mb-0.5">Impact & Recommendation</Text>
                <Text className="text-xs text-slate-300">{rule.recommendation}</Text>
              </View>

              {!isPassed && (
                <TouchableOpacity
                  className="bg-blue-950/60 border border-blue-800/60 py-2 rounded-lg flex-row items-center justify-center gap-2 active:bg-blue-900/60"
                  onPress={() => {
                    setDrilldownSearch("");
                    setActiveDrilldownRule(rule);
                  }}
                >
                  <Text className="text-xs font-bold text-blue-400">Inspect Flagged Records</Text>
                  <ArrowRight size={13} color={THEME_COLORS.primaryIcon} />
                </TouchableOpacity>
              )}
            </View>
          );
        })}
      </View>

      {/* Drilldown Modal */}
      <Modal
        visible={Boolean(activeDrilldownRule)}
        animationType="fade"
        transparent
        onRequestClose={() => setActiveDrilldownRule(null)}
      >
        <View className="flex-1 bg-black/75 items-center justify-center p-4 md:p-4">
          <View className="w-full max-w-3xl max-h-[85%] bg-dark-card border border-dark-border rounded-xl p-3 shadow-2xl">
            {/* Modal Header */}
            <View className="flex-row items-center justify-between pb-4 border-b border-dark-border mb-4">
              <View className="flex-1 mr-4">
                <View className="flex-row items-center gap-2 mb-1">
                  <AlertCircle size={16} color={THEME_COLORS.primaryIcon} />
                  <Text className="text-base font-bold text-white">{activeDrilldownRule?.rule_name}</Text>
                </View>
                <Text className="text-xs text-slate-400">
                  [{activeDrilldownRule?.rule_code}] — {issuesData?.total ?? 0} affected records
                </Text>
              </View>

              <View className="flex-row items-center gap-2">
                <TouchableOpacity
                  className="bg-blue-600 hover:bg-blue-500 px-3 py-1.5 rounded-lg flex-row items-center gap-1.5"
                  disabled={isExporting}
                  onPress={() => activeDrilldownRule && handleExport(activeDrilldownRule.rule_code)}
                >
                  {isExporting ? (
                    <ActivityIndicator size="small" color="#ffffff" />
                  ) : (
                    <>
                      <Download size={13} color="#ffffff" />
                      <Text className="text-xs font-bold text-white">Export CSV</Text>
                    </>
                  )}
                </TouchableOpacity>
                <TouchableOpacity
                  className="bg-dark-bg border border-dark-border p-1.5 rounded-lg"
                  onPress={() => setActiveDrilldownRule(null)}
                >
                  <X size={16} color={THEME_COLORS.textMuted} />
                </TouchableOpacity>
              </View>
            </View>

            {/* Search Input */}
            <View className="flex-row items-center gap-2 bg-dark-bg border border-dark-border px-3 py-2 rounded-xl mb-4">
              <Search size={14} color={THEME_COLORS.textMuted} />
              <TextInput
                className="flex-1 text-xs text-white"
                placeholder="Search by name, employee code, phone..."
                placeholderTextColor={THEME_COLORS.textDisabled}
                value={drilldownSearch}
                onChangeText={setDrilldownSearch}
              />
            </View>

            {/* Table / List */}
            {isIssuesLoading ? (
              <View className="py-12 items-center justify-center">
                <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
                <Text className="text-xs text-slate-400 mt-2 font-medium">Fetching flagged records...</Text>
              </View>
            ) : issuesData?.items && issuesData.items.length > 0 ? (
              <ScrollView className="max-h-[380px]" showsVerticalScrollIndicator={false}>
                {issuesData.items.map((item) => (
                  <View
                    key={item.record_id}
                    className="flex-row items-center justify-between p-3 bg-dark-bg/60 border border-dark-border rounded-xl mb-2 gap-3"
                  >
                    <View className="flex-row items-center gap-3 flex-1">
                      <View className="px-2 py-1 rounded bg-blue-950/80 border border-blue-800/60">
                        <Text className="text-[11px] font-mono font-bold text-blue-400">
                          {item.emp_code || `ID ${item.record_id}`}
                        </Text>
                      </View>
                      <View className="flex-1">
                        <Text className="text-xs font-bold text-white">{item.entity_name}</Text>
                        <Text className="text-[11px] text-slate-400 mt-0.5">{item.issue_detail}</Text>
                      </View>
                    </View>
                    {item.contact_value && (
                      <View className="bg-dark-card border border-dark-border px-2.5 py-1 rounded-lg">
                        <Text className="text-xs font-mono text-slate-300">{item.contact_value}</Text>
                      </View>
                    )}
                  </View>
                ))}
              </ScrollView>
            ) : (
              <View className="py-12 items-center justify-center gap-2">
                <CheckCircle2 size={28} color={THEME_COLORS.successIcon} />
                <Text className="text-xs text-slate-400 font-medium">No records matching your search filter.</Text>
              </View>
            )}
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}
