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
  Search,
  ShieldCheck,
  X,
} from "lucide-react-native";
import { downloadOrgQualityIssuesExport } from "@/api/organization.api";
import { THEME_COLORS } from "@/constants/theme";
import { useOrgQualityIssues } from "@/hooks/useOrganization";
import type {
  OrgDataQualityResponse,
  OrgQualityRuleResult,
} from "@/types/organization.types";

interface OrgQualityTabProps {
  quality?: OrgDataQualityResponse;
  isLoading: boolean;
}

export const OrgQualityTab: React.FC<OrgQualityTabProps> = ({
  quality,
  isLoading,
}) => {
  const [selectedSeverity, setSelectedSeverity] = useState<string>("ALL");
  const [activeDrilldownRule, setActiveDrilldownRule] = useState<OrgQualityRuleResult | null>(null);
  const [drilldownSearch, setDrilldownSearch] = useState("");
  const [isExporting, setIsExporting] = useState(false);

  // Issues drilldown query
  const { data: issuesData, isLoading: isIssuesLoading } = useOrgQualityIssues(
    activeDrilldownRule?.rule_code || "",
    drilldownSearch || undefined,
    50,
    0
  );

  if (isLoading || !quality) {
    return (
      <View className="py-12 items-center justify-center">
        <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
        <Text className="text-sm text-slate-400 mt-3 font-medium">Auditing organization structure data quality...</Text>
      </View>
    );
  }

  const {
    overall_health_score,
    critical_issues_count,
    warning_issues_count,
    info_issues_count,
    rules,
  } = quality;

  const filteredRules =
    selectedSeverity === "ALL"
      ? rules
      : rules.filter((r) => r.severity === selectedSeverity);

  const handleExport = async (ruleCode: string) => {
    try {
      setIsExporting(true);
      await downloadOrgQualityIssuesExport(ruleCode, drilldownSearch || undefined, "csv");
    } catch (err) {
      console.error("Export error:", err);
    } finally {
      setIsExporting(false);
    }
  };

  const renderSeverityBadge = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return (
          <View className="flex-row items-center gap-1 bg-rose-950/60 border border-rose-800/60 px-2 py-0.5 rounded">
            <AlertCircle size={10} color={THEME_COLORS.danger} />
            <Text className="text-[10px] font-bold text-rose-400">CRITICAL</Text>
          </View>
        );
      case "WARNING":
        return (
          <View className="flex-row items-center gap-1 bg-amber-950/60 border border-amber-800/60 px-2 py-0.5 rounded">
            <AlertTriangle size={10} color={THEME_COLORS.warning} />
            <Text className="text-[10px] font-bold text-amber-400">WARNING</Text>
          </View>
        );
      default:
        return (
          <View className="flex-row items-center gap-1 bg-blue-950/60 border border-blue-800/60 px-2 py-0.5 rounded">
            <Info size={10} color={THEME_COLORS.primaryIcon} />
            <Text className="text-[10px] font-bold text-blue-400">INFO</Text>
          </View>
        );
    }
  };

  return (
    <View className="gap-4">
      {/* ── Top Quality Health Header ───────────────────────── */}
      <View className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        {/* Health Score Card */}
        <View className="bg-dark-card border border-dark-border p-4 rounded-xl flex-row items-center justify-between">
          <View>
            <Text className="text-[10px] uppercase font-bold text-slate-400">Structure Health</Text>
            <Text className="text-xl font-black text-white font-mono mt-0.5">{overall_health_score}%</Text>
            <Text className="text-[10px] text-emerald-400 font-bold mt-1">14 Canonical Rules</Text>
          </View>
          <View className="p-3 bg-emerald-950/40 border border-emerald-800/30 rounded-xl">
            <ShieldCheck size={28} color={THEME_COLORS.success} />
          </View>
        </View>

        {/* Critical Card */}
        <TouchableOpacity
          onPress={() => setSelectedSeverity(selectedSeverity === "CRITICAL" ? "ALL" : "CRITICAL")}
          className={`bg-dark-card border p-4 rounded-xl flex-row items-center justify-between ${
            selectedSeverity === "CRITICAL" ? "border-rose-500 bg-rose-950/20" : "border-dark-border"
          }`}
        >
          <View>
            <Text className="text-[10px] uppercase font-bold text-slate-400">Critical Issues</Text>
            <Text className="text-xl font-black text-rose-400 font-mono mt-0.5">{critical_issues_count}</Text>
            <Text className="text-[10px] text-slate-400 mt-1">Immediate action</Text>
          </View>
          <View className="p-3 bg-rose-950/40 border border-rose-800/30 rounded-xl">
            <AlertCircle size={28} color={THEME_COLORS.danger} />
          </View>
        </TouchableOpacity>

        {/* Warning Card */}
        <TouchableOpacity
          onPress={() => setSelectedSeverity(selectedSeverity === "WARNING" ? "ALL" : "WARNING")}
          className={`bg-dark-card border p-4 rounded-xl flex-row items-center justify-between ${
            selectedSeverity === "WARNING" ? "border-amber-500 bg-amber-950/20" : "border-dark-border"
          }`}
        >
          <View>
            <Text className="text-[10px] uppercase font-bold text-slate-400">Warnings</Text>
            <Text className="text-xl font-black text-amber-400 font-mono mt-0.5">{warning_issues_count}</Text>
            <Text className="text-[10px] text-slate-400 mt-1">Data hygiene</Text>
          </View>
          <View className="p-3 bg-amber-950/40 border border-amber-800/30 rounded-xl">
            <AlertTriangle size={28} color={THEME_COLORS.warning} />
          </View>
        </TouchableOpacity>

        {/* Info Card */}
        <TouchableOpacity
          onPress={() => setSelectedSeverity(selectedSeverity === "INFO" ? "ALL" : "INFO")}
          className={`bg-dark-card border p-4 rounded-xl flex-row items-center justify-between ${
            selectedSeverity === "INFO" ? "border-blue-500 bg-blue-950/20" : "border-dark-border"
          }`}
        >
          <View>
            <Text className="text-[10px] uppercase font-bold text-slate-400">Informational</Text>
            <Text className="text-xl font-black text-blue-400 font-mono mt-0.5">{info_issues_count}</Text>
            <Text className="text-[10px] text-slate-400 mt-1">Master catalog</Text>
          </View>
          <View className="p-3 bg-blue-950/40 border border-blue-800/30 rounded-xl">
            <Info size={28} color={THEME_COLORS.primaryIcon} />
          </View>
        </TouchableOpacity>
      </View>

      {/* ── Filter Pills Bar ───────────────────────────────── */}
      <View className="flex-row items-center gap-2">
        {["ALL", "CRITICAL", "WARNING", "INFO"].map((sev) => (
          <TouchableOpacity
            key={sev}
            onPress={() => setSelectedSeverity(sev)}
            className={`px-3 py-1.5 rounded-lg border ${
              selectedSeverity === sev
                ? "bg-blue-600 border-blue-400"
                : "bg-dark-card border-dark-border"
            }`}
          >
            <Text
              className={`text-xs font-bold ${
                selectedSeverity === sev ? "text-white" : "text-slate-400"
              }`}
            >
              {sev}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* ── Rules Catalog Grid ──────────────────────────────── */}
      <View className="gap-3">
        {filteredRules.map((rule) => (
          <View
            key={rule.rule_code}
            className={`bg-dark-card border rounded-xl p-4 transition-all ${
              rule.issue_count > 0 ? "border-dark-border" : "border-dark-border/40 opacity-70"
            }`}
          >
            <View className="flex-col sm:flex-row sm:items-start justify-between gap-2 mb-2">
              <View className="flex-1">
                <View className="flex-row items-center gap-2 mb-1">
                  {renderSeverityBadge(rule.severity)}
                  <Text className="text-xs font-mono font-bold text-slate-400">[{rule.rule_code}]</Text>
                  {rule.issue_count === 0 && (
                    <View className="flex-row items-center gap-1 bg-emerald-950/50 border border-emerald-800/40 px-1.5 py-0.2 rounded">
                      <CheckCircle2 size={10} color={THEME_COLORS.success} />
                      <Text className="text-[9px] font-bold text-emerald-400">Clean</Text>
                    </View>
                  )}
                </View>
                <Text className="text-sm font-bold text-white">{rule.rule_name}</Text>
                <Text className="text-xs text-slate-400 mt-1">{rule.description}</Text>
              </View>

              <View className="flex-row items-center gap-3 self-end sm:self-start">
                <View className="items-end">
                  <Text
                    className={`text-xl font-black font-mono ${
                      rule.issue_count > 0
                        ? rule.severity === "CRITICAL"
                          ? "text-rose-400"
                          : rule.severity === "WARNING"
                          ? "text-amber-400"
                          : "text-blue-400"
                        : "text-emerald-400"
                    }`}
                  >
                    {rule.issue_count.toLocaleString()}
                  </Text>
                  <Text className="text-[9px] text-slate-400">issues</Text>
                </View>

                {rule.issue_count > 0 && (
                  <TouchableOpacity
                    onPress={() => setActiveDrilldownRule(rule)}
                    className="bg-blue-600 hover:bg-blue-500 p-2 rounded-lg flex-row items-center gap-1 active:bg-blue-700"
                  >
                    <Text className="text-[11px] font-bold text-white">Inspect</Text>
                    <ArrowRight size={12} color="#ffffff" />
                  </TouchableOpacity>
                )}
              </View>
            </View>

            {/* Impact & Recommendation */}
            <View className="bg-dark-bg border border-dark-border/80 rounded-lg p-2.5 mt-2 gap-1 text-[11px]">
              <View className="flex-row items-start gap-1.5">
                <Text className="text-[10px] font-bold text-slate-400 uppercase w-24">Impact:</Text>
                <Text className="text-[11px] text-slate-300 flex-1">{rule.impact}</Text>
              </View>
              <View className="flex-row items-start gap-1.5 border-t border-dark-border/60 pt-1">
                <Text className="text-[10px] font-bold text-slate-400 uppercase w-24">Remedy:</Text>
                <Text className="text-[11px] text-emerald-400/90 flex-1">{rule.recommendation}</Text>
              </View>
            </View>
          </View>
        ))}
      </View>

      {/* ── Rule Drilldown Inspector Modal ──────────────────── */}
      {activeDrilldownRule && (
        <Modal
          visible={Boolean(activeDrilldownRule)}
          transparent
          animationType="fade"
          onRequestClose={() => setActiveDrilldownRule(null)}
        >
          <View className="flex-1 bg-black/80 justify-center items-center p-4">
            <View className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl max-h-[85vh] overflow-hidden flex-col shadow-2xl">
              {/* Modal Header */}
              <View className="p-4 border-b border-dark-border flex-row items-center justify-between bg-dark-bg">
                <View className="flex-1 mr-3">
                  <View className="flex-row items-center gap-2 mb-1">
                    {renderSeverityBadge(activeDrilldownRule.severity)}
                    <Text className="text-xs font-mono font-bold text-blue-400">
                      {activeDrilldownRule.rule_code}
                    </Text>
                  </View>
                  <Text className="text-base font-bold text-white">{activeDrilldownRule.rule_name}</Text>
                  <Text className="text-xs text-slate-400 mt-0.5">{activeDrilldownRule.description}</Text>
                </View>

                <View className="flex-row items-center gap-2">
                  <TouchableOpacity
                    onPress={() => handleExport(activeDrilldownRule.rule_code)}
                    disabled={isExporting}
                    className="bg-dark-card border border-dark-border px-3 py-2 rounded-lg flex-row items-center gap-1.5"
                  >
                    <Download size={13} color="#94a3b8" />
                    <Text className="text-xs font-bold text-slate-300">Export</Text>
                  </TouchableOpacity>

                  <TouchableOpacity
                    onPress={() => setActiveDrilldownRule(null)}
                    className="bg-dark-card border border-dark-border p-2 rounded-lg"
                  >
                    <X size={16} color="#94a3b8" />
                  </TouchableOpacity>
                </View>
              </View>

              {/* Search filter in modal */}
              <View className="p-3 border-b border-dark-border bg-slate-900/50 flex-row items-center">
                <Search size={14} color="#64748b" />
                <TextInput
                  value={drilldownSearch}
                  onChangeText={setDrilldownSearch}
                  placeholder="Filter records..."
                  placeholderTextColor="#64748b"
                  className="flex-1 text-xs text-white ml-2"
                />
              </View>

              {/* Modal Body / Items List */}
              <ScrollView className="p-4 flex-1">
                {isIssuesLoading ? (
                  <View className="py-12 items-center justify-center">
                    <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
                    <Text className="text-xs text-slate-400 mt-2 font-medium">Fetching flagged records...</Text>
                  </View>
                ) : !issuesData || issuesData.items.length === 0 ? (
                  <View className="py-12 items-center justify-center">
                    <CheckCircle2 size={32} color={THEME_COLORS.success} />
                    <Text className="text-sm text-slate-300 font-bold mt-2">No issue records found</Text>
                  </View>
                ) : (
                  <View className="gap-2">
                    {issuesData.items.map((item, idx) => (
                      <View
                        key={`${item.record_id}-${idx}`}
                        className="bg-dark-bg border border-dark-border p-3 rounded-lg flex-col sm:flex-row sm:items-center justify-between gap-2"
                      >
                        <View className="flex-1">
                          <View className="flex-row items-center gap-2 mb-1">
                            <Text className="text-xs font-mono font-bold text-white">
                              ID: {item.record_id}
                            </Text>
                            <View className="bg-slate-800 px-1.5 py-0.2 rounded">
                              <Text className="text-[9px] uppercase font-bold text-slate-400">{item.entity_type}</Text>
                            </View>
                            <Text className="text-xs font-bold text-blue-400">{item.entity_name}</Text>
                          </View>
                          <Text className="text-xs text-slate-300">{item.issue_detail}</Text>
                        </View>
                      </View>
                    ))}
                  </View>
                )}
              </ScrollView>

              {/* Modal Footer */}
              <View className="p-3 border-t border-dark-border bg-dark-bg flex-row items-center justify-between">
                <Text className="text-[11px] text-slate-400">
                  Showing {issuesData?.items.length || 0} of {issuesData?.total || 0} total records
                </Text>
                <TouchableOpacity
                  onPress={() => setActiveDrilldownRule(null)}
                  className="bg-slate-800 px-4 py-1.5 rounded-lg"
                >
                  <Text className="text-xs font-bold text-white">Close</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>
      )}
    </View>
  );
};
