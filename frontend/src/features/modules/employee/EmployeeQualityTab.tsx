import React, { useState } from "react";
import { ActivityIndicator, FlatList, Modal, Pressable, Text, TextInput, View } from "react-native";
import {
  AlertTriangle,
  CheckCircle2,
  Download,
  Info,
  Search,
  ShieldAlert,
  X,
} from "lucide-react-native";
import { employeeApi } from "@/api/employee.api";
import { THEME_COLORS } from "@/constants/theme";
import { useEmployeeQualityIssues } from "@/hooks/useEmployee";
import type { EmployeeDataQualityResponse, QualityRuleResult } from "@/types/employee.types";

interface EmployeeQualityTabProps {
  quality?: EmployeeDataQualityResponse;
  isLoading: boolean;
}

export const EmployeeQualityTab: React.FC<EmployeeQualityTabProps> = ({
  quality,
  isLoading,
}) => {
  const [selectedRule, setSelectedRule] = useState<QualityRuleResult | null>(null);
  const [issueSearch, setIssueSearch] = useState<string>("");
  const [activeSeverityFilter, setActiveSeverityFilter] = useState<string>("ALL");

  // Query issues when modal is opened for a specific rule
  const { data: issuesData, isLoading: loadingIssues } = useEmployeeQualityIssues(
    selectedRule?.rule_code || "",
    issueSearch,
    50,
    0
  );

  if (isLoading || !quality) {
    return (
      <View className="py-12 items-center justify-center">
        <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
        <Text className="text-sm text-slate-400 mt-3 font-medium">Auditing employee data quality...</Text>
      </View>
    );
  }

  const { overall_health_score, critical_issues_count, warning_issues_count, info_issues_count, rules } = quality;

  const filteredRules = rules.filter((r) => {
    if (activeSeverityFilter === "ALL") return true;
    return r.severity === activeSeverityFilter;
  });

  const handleExportCSV = async (ruleCode: string) => {
    await employeeApi.exportQualityIssues({
      issue: ruleCode,
      search: issueSearch || undefined,
      format: "csv",
    });
  };

  return (
    <View className="gap-4">
      {/* ── Health Score & Severity Cards ──────────────────── */}
      <View className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
        {/* Overall Score */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4 flex-row items-center justify-between">
          <View>
            <Text className="text-[10px] uppercase font-bold text-slate-400">Workforce Data Quality</Text>
            <Text className="text-xl font-black text-white font-mono mt-0.5">{overall_health_score}%</Text>
            <Text className="text-[10px] text-emerald-400 flex-row items-center gap-1 mt-1">
              ✓ Canonical validation rules active
            </Text>
          </View>
          <View className="w-12 h-12 rounded-xl bg-blue-600/10 border border-blue-500/20 items-center justify-center">
            <CheckCircle2 size={24} color={THEME_COLORS.primaryIcon} />
          </View>
        </View>

        {/* Critical Issues */}
        <Pressable
          onPress={() => setActiveSeverityFilter(activeSeverityFilter === "CRITICAL" ? "ALL" : "CRITICAL")}
          className={`bg-dark-card border rounded-xl p-4 flex-row items-center justify-between ${
            activeSeverityFilter === "CRITICAL" ? "border-rose-500 bg-rose-950/20" : "border-rose-500/30"
          }`}
        >
          <View>
            <Text className="text-[10px] uppercase font-bold text-rose-400">Critical Issues</Text>
            <Text className="text-xl font-black text-rose-400 font-mono mt-0.5">{critical_issues_count}</Text>
            <Text className="text-[10px] text-slate-400 mt-1">Immediate action required</Text>
          </View>
          <View className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/30 items-center justify-center">
            <ShieldAlert size={24} color={THEME_COLORS.dangerIcon} />
          </View>
        </Pressable>

        {/* Warnings */}
        <Pressable
          onPress={() => setActiveSeverityFilter(activeSeverityFilter === "WARNING" ? "ALL" : "WARNING")}
          className={`bg-dark-card border rounded-xl p-4 flex-row items-center justify-between ${
            activeSeverityFilter === "WARNING" ? "border-amber-500 bg-amber-950/20" : "border-amber-500/30"
          }`}
        >
          <View>
            <Text className="text-[10px] uppercase font-bold text-amber-400">Warnings</Text>
            <Text className="text-xl font-black text-amber-400 font-mono mt-0.5">{warning_issues_count}</Text>
            <Text className="text-[10px] text-slate-400 mt-1">Data hygiene gaps</Text>
          </View>
          <View className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/30 items-center justify-center">
            <AlertTriangle size={24} color={THEME_COLORS.warningIcon} />
          </View>
        </Pressable>

        {/* Info */}
        <Pressable
          onPress={() => setActiveSeverityFilter(activeSeverityFilter === "INFO" ? "ALL" : "INFO")}
          className={`bg-dark-card border rounded-xl p-4 flex-row items-center justify-between ${
            activeSeverityFilter === "INFO" ? "border-blue-500 bg-blue-950/20" : "border-blue-500/30"
          }`}
        >
          <View>
            <Text className="text-[10px] uppercase font-bold text-blue-400">Informational</Text>
            <Text className="text-xl font-black text-blue-400 font-mono mt-0.5">{info_issues_count}</Text>
            <Text className="text-[10px] text-slate-400 mt-1">Legacy / Audit traces</Text>
          </View>
          <View className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/30 items-center justify-center">
            <Info size={24} color={THEME_COLORS.primaryIcon} />
          </View>
        </Pressable>
      </View>

      {/* ── Rule Severity Filter Pills ─────────────────────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2">
        <View className="flex-row items-center gap-1.5">
          {["ALL", "CRITICAL", "WARNING", "INFO"].map((sev) => (
            <Pressable
              key={sev}
              onPress={() => setActiveSeverityFilter(sev)}
              className={`px-3 py-1.5 rounded-lg border text-xs font-bold transition-all ${
                activeSeverityFilter === sev
                  ? "bg-blue-600 border-blue-400 text-white"
                  : "bg-dark-card border-dark-border text-slate-400"
              }`}
            >
              <Text
                className={`text-xs font-bold ${
                  activeSeverityFilter === sev ? "text-white" : "text-slate-400"
                }`}
              >
                {sev} {sev === "ALL" ? `(${rules.length})` : ""}
              </Text>
            </Pressable>
          ))}
        </View>

        <Text className="text-[11px] text-slate-400">Click any card to inspect individual employee records &amp; export CSV</Text>
      </View>

      {/* ── Rules Catalog Grid ─────────────────────────────── */}
      <View className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {filteredRules.map((rule) => {
          const isCrit = rule.severity === "CRITICAL";
          const isWarn = rule.severity === "WARNING";

          return (
            <Pressable
              key={rule.rule_code}
              onPress={() => {
                setSelectedRule(rule);
                setIssueSearch("");
              }}
              accessibilityRole="button"
              accessibilityLabel={`Inspect ${rule.rule_name}`}
              className={`bg-dark-card border rounded-xl p-4 transition-all hover:border-slate-500 ${
                isCrit
                  ? "border-rose-500/30 hover:border-rose-400"
                  : isWarn
                  ? "border-amber-500/30 hover:border-amber-400"
                  : "border-dark-border hover:border-blue-400"
              }`}
            >
              <View className="flex-row items-start justify-between gap-2 mb-2">
                <View className="flex-1">
                  <View className="flex-row items-center gap-2 mb-1">
                    <View
                      className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase font-mono ${
                        isCrit
                          ? "bg-rose-950 border border-rose-800 text-rose-300"
                          : isWarn
                          ? "bg-amber-950 border border-amber-800 text-amber-300"
                          : "bg-blue-950 border border-blue-800 text-blue-300"
                      }`}
                    >
                      <Text
                        className={`text-[9px] font-bold uppercase font-mono ${
                          isCrit
                            ? "text-rose-300"
                            : isWarn
                            ? "text-amber-300"
                            : "text-blue-300"
                        }`}
                      >
                        {rule.severity}
                      </Text>
                    </View>
                    <Text className="text-xs font-mono text-slate-400">{rule.rule_code}</Text>
                  </View>
                  <Text className="text-sm font-bold text-white">{rule.rule_name}</Text>
                </View>

                <View className="items-end bg-dark-bg border border-dark-border px-3 py-1.5 rounded-lg">
                  <Text
                    className={`text-lg font-mono font-black ${
                      isCrit ? "text-rose-400" : isWarn ? "text-amber-400" : "text-blue-400"
                    }`}
                  >
                    {rule.issue_count.toLocaleString()}
                  </Text>
                  <Text className="text-[9px] text-slate-400">flagged</Text>
                </View>
              </View>

              <Text className="text-xs text-slate-300 mb-2">{rule.description}</Text>

              <View className="bg-dark-bg border border-dark-border/80 rounded-lg p-2.5 gap-1">
                <Text className="text-[11px] text-slate-400">
                  <Text className="font-bold text-slate-300">Impact: </Text>
                  {rule.impact}
                </Text>
                <Text className="text-[11px] text-slate-400">
                  <Text className="font-bold text-slate-300">Recommendation: </Text>
                  {rule.recommendation}
                </Text>
              </View>
            </Pressable>
          );
        })}
      </View>

      {/* ── Rule Drilldown & Record Inspector Modal ─────────── */}
      {selectedRule && (
        <Modal visible={true} transparent={true} animationType="fade">
          <View className="flex-1 bg-black/70 justify-center items-center p-4">
            <View className="w-full max-w-4xl max-h-[85vh] bg-dark-card border border-dark-border rounded-xl flex-col overflow-hidden shadow-2xl">
              {/* Modal Header */}
              <View className="p-4 border-b border-dark-border flex-row items-center justify-between bg-slate-900">
                <View className="flex-1 mr-2">
                  <View className="flex-row items-center gap-2 mb-1">
                    <View
                      className={`px-2 py-0.5 rounded text-[9px] font-bold font-mono ${
                        selectedRule.severity === "CRITICAL"
                          ? "bg-rose-950 border border-rose-800 text-rose-300"
                          : "bg-amber-950 border border-amber-800 text-amber-300"
                      }`}
                    >
                      <Text
                        className={`text-[9px] font-bold font-mono ${
                          selectedRule.severity === "CRITICAL"
                            ? "text-rose-300"
                            : "text-amber-300"
                        }`}
                      >
                        {selectedRule.severity}
                      </Text>
                    </View>
                    <Text className="text-xs font-mono text-slate-400">{selectedRule.rule_code}</Text>
                  </View>
                  <Text className="text-base font-bold text-white">{selectedRule.rule_name}</Text>
                </View>

                <View className="flex-row items-center gap-2">
                  <Pressable
                    onPress={() => handleExportCSV(selectedRule.rule_code)}
                    className="flex-row items-center gap-1.5 bg-blue-600 px-3 py-1.5 rounded-lg border border-blue-400"
                  >
                    <Download size={13} color="#ffffff" />
                    <Text className="text-xs font-bold text-white">Export CSV</Text>
                  </Pressable>

                  <Pressable
                    onPress={() => setSelectedRule(null)}
                    className="w-8 h-8 rounded-lg bg-slate-800 items-center justify-center"
                  >
                    <X size={16} color={THEME_COLORS.textMuted} />
                  </Pressable>
                </View>
              </View>

              {/* Filter / Search Bar in Modal */}
              <View className="p-3 border-b border-dark-border bg-dark-bg flex-row items-center justify-between gap-3">
                <View className="flex-1 flex-row items-center bg-dark-card border border-dark-border rounded-lg px-3 py-1.5">
                  <Search size={14} color={THEME_COLORS.textMuted} />
                  <TextInput
                    value={issueSearch}
                    onChangeText={setIssueSearch}
                    placeholder="Search by name, employee code, or email..."
                    placeholderTextColor={THEME_COLORS.textMuted}
                    className="flex-1 text-xs text-white ml-2 outline-none"
                  />
                  {issueSearch ? (
                    <Pressable onPress={() => setIssueSearch("")}>
                      <X size={13} color={THEME_COLORS.textMuted} />
                    </Pressable>
                  ) : null}
                </View>

                <Text className="text-xs font-mono text-slate-400">
                  {issuesData?.total ?? 0} matching records
                </Text>
              </View>

              {/* Records List in Modal */}
              <View className="flex-1 p-3">
                {loadingIssues ? (
                  <View className="py-12 items-center justify-center">
                    <ActivityIndicator size="small" color={THEME_COLORS.primaryIcon} />
                    <Text className="text-xs text-slate-400 mt-2">Loading flagged records...</Text>
                  </View>
                ) : !issuesData?.items.length ? (
                  <View className="py-12 items-center justify-center">
                    <CheckCircle2 size={32} color={THEME_COLORS.success} />
                    <Text className="text-sm font-bold text-white mt-2">No records found</Text>
                    <Text className="text-xs text-slate-400">No issues match the search criteria.</Text>
                  </View>
                ) : (
                  <FlatList
                    data={issuesData.items}
                    keyExtractor={(item, idx) => `${item.emp_id || idx}_${idx}`}
                    contentContainerStyle={{ gap: 8 }}
                    renderItem={({ item }) => (
                      <View className="bg-dark-bg border border-dark-border p-3 rounded-lg flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <View className="flex-1">
                          <View className="flex-row items-center gap-2 mb-0.5">
                            <Text className="text-xs font-bold text-white">
                              {item.full_name || "Unknown Name"}
                            </Text>
                            <View className="bg-slate-800 px-1.5 py-0.5 rounded">
                              <Text className="text-[10px] font-mono text-blue-300">
                                Code: {item.emp_code || `EmpID: ${item.emp_id}`}
                              </Text>
                            </View>
                            <View
                              className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                                item.emp_is_active
                                  ? "bg-emerald-950 border border-emerald-800 text-emerald-300"
                                  : "bg-slate-800 text-slate-400"
                              }`}
                            >
                              <Text
                                className={`text-[9px] font-bold ${
                                  item.emp_is_active ? "text-emerald-300" : "text-slate-400"
                                }`}
                              >
                                {item.emp_is_active ? "Active" : "Inactive"}
                              </Text>
                            </View>
                          </View>
                          <Text className="text-[11px] font-mono text-amber-300">
                            {item.issue_detail}
                          </Text>
                        </View>

                        <View className="items-end text-[10px] text-slate-400">
                          {item.company_email ? (
                            <Text className="text-[10px] text-slate-300">{item.company_email}</Text>
                          ) : null}
                          {item.phone ? (
                            <Text className="text-[10px] text-slate-400">{item.phone}</Text>
                          ) : null}
                        </View>
                      </View>
                    )}
                  />
                )}
              </View>
            </View>
          </View>
        </Modal>
      )}
    </View>
  );
};
