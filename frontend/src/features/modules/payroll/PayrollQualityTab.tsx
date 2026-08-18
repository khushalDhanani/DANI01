import React, { useState } from "react";
import { ActivityIndicator, Modal, Pressable, ScrollView, Text, View } from "react-native";
import {
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Download,
  ShieldCheck,
  X,
} from "lucide-react-native";
import { downloadPayrollQualityExport } from "@/api/payroll.api";
import { THEME_COLORS } from "@/constants/theme";
import { usePayrollQuality, usePayrollQualityIssues } from "@/hooks/usePayroll";
import type { PayrollQualityRuleInfo } from "@/types/payroll.types";

export function PayrollQualityTab() {
  const { data: dq, isLoading, error } = usePayrollQuality();

  const [selectedRule, setSelectedRule] = useState<PayrollQualityRuleInfo | null>(null);
  const [modalPage, setModalPage] = useState<number>(0);
  const [isExportingModal, setIsExportingModal] = useState<boolean>(false);
  const pageSize = 20;

  const { data: issuesData, isLoading: isLoadingIssues } = usePayrollQualityIssues(
    selectedRule?.rule_code,
    "",
    pageSize,
    modalPage * pageSize,
  );

  const handleExportIssues = async (ruleCode: string) => {
    try {
      setIsExportingModal(true);
      await downloadPayrollQualityExport(ruleCode);
    } catch (err) {
      console.error("Failed to export quality issues:", err);
    } finally {
      setIsExportingModal(false);
    }
  };

  if (isLoading) {
    return (
      <View className="py-12 items-center justify-center">
        <ActivityIndicator size="small" color="#a855f7" />
        <Text className="text-[11px] text-slate-400 mt-2 font-medium">
          Evaluating 6 Payroll & Salary SSoT data reconciliation rules...
        </Text>
      </View>
    );
  }

  if (error || !dq) {
    return (
      <View className="py-12 items-center justify-center bg-dark-card border border-dark-border rounded-lg p-4">
        <AlertTriangle size={28} color={THEME_COLORS.danger} />
        <Text className="text-xs font-semibold text-slate-300 mt-2">
          Failed to load Payroll Data Quality analysis.
        </Text>
      </View>
    );
  }

  const {
    overall_health_score,
    critical_issues_count,
    warning_issues_count,
    info_issues_count,
    rules,
  } = dq;

  return (
    <View className="gap-3">
      {/* ── Compact Top Health Score Banner ────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-3 flex-col md:flex-row items-start md:items-center justify-between gap-3">
        <View className="flex-row items-center gap-3 flex-1">
          <View className="relative items-center justify-center">
            <View className="w-12 h-12 rounded-full bg-purple-950/40 border-2 border-purple-500/40 items-center justify-center">
              <Text className="text-base font-black text-purple-400">
                {overall_health_score}%
              </Text>
            </View>
          </View>
          <View className="flex-1">
            <View className="flex-row items-center gap-1.5">
              <ShieldCheck size={16} color="#c084fc" />
              <Text className="text-sm font-bold text-white">
                Payroll Quality Index
              </Text>
            </View>
            <Text className="text-[11px] text-slate-400 leading-tight">
              Automated financial reconciliation across monthly salary headers, itemized earnings, deductions, and registers.
            </Text>
          </View>
        </View>

        {/* Compact Severity Summary Chips */}
        <View className="flex-row items-center gap-1.5 self-stretch md:self-auto justify-between md:justify-end">
          <View className="bg-rose-950/60 border border-rose-800/60 px-2.5 py-1 rounded-lg items-center min-w-[64px]">
            <Text className="text-[9px] font-bold text-rose-400 uppercase tracking-wider">Critical</Text>
            <Text className="text-base font-black text-rose-300">{critical_issues_count}</Text>
          </View>
          <View className="bg-amber-950/60 border border-amber-800/60 px-2.5 py-1 rounded-lg items-center min-w-[64px]">
            <Text className="text-[9px] font-bold text-amber-400 uppercase tracking-wider">Warning</Text>
            <Text className="text-base font-black text-amber-300">{warning_issues_count}</Text>
          </View>
          <View className="bg-blue-950/60 border border-blue-800/60 px-2.5 py-1 rounded-lg items-center min-w-[64px]">
            <Text className="text-[9px] font-bold text-blue-400 uppercase tracking-wider">Info</Text>
            <Text className="text-base font-black text-blue-300">{info_issues_count}</Text>
          </View>
        </View>
      </View>

      {/* ── Compact 6 Rule Cards Grid ─────────────────────── */}
      <View className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {rules.map((rule) => {
          const isCritical = rule.severity === "CRITICAL";
          const isWarning = rule.severity === "WARNING";
          const hasIssues = rule.issue_count > 0;

          return (
            <View
              key={rule.rule_code}
              className={`bg-dark-card border rounded-lg p-3 flex-col justify-between transition-all ${
                hasIssues
                  ? isCritical
                    ? "border-rose-800/60 bg-rose-950/10"
                    : isWarning
                    ? "border-amber-800/60 bg-amber-950/10"
                    : "border-blue-800/60 bg-blue-950/10"
                  : "border-dark-border"
              }`}
            >
              <View>
                <View className="flex-row items-start justify-between gap-2 mb-1.5">
                  <View className="flex-1">
                    <View className="flex-row items-center gap-1.5 mb-0.5">
                      <View
                        className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${
                          isCritical
                            ? "bg-rose-950 text-rose-400 border border-rose-800"
                            : isWarning
                            ? "bg-amber-950 text-amber-400 border border-amber-800"
                            : "bg-blue-950 text-blue-400 border border-blue-800"
                        }`}
                      >
                        <Text
                          className={`text-[9px] font-mono font-bold ${
                            isCritical
                              ? "text-rose-400"
                              : isWarning
                              ? "text-amber-400"
                              : "text-blue-400"
                          }`}
                        >
                          {rule.severity}
                        </Text>
                      </View>

                      <Text className="text-[9px] font-mono font-semibold text-slate-500">
                        {rule.rule_code}
                      </Text>
                    </View>

                    <Text className="text-xs font-bold text-white leading-tight">
                      {rule.rule_name}
                    </Text>
                  </View>

                  <View className="items-end">
                    <Text
                      className={`text-lg font-black ${
                        hasIssues
                          ? isCritical
                            ? "text-rose-400"
                            : isWarning
                            ? "text-amber-400"
                            : "text-blue-400"
                          : "text-emerald-400"
                      }`}
                    >
                      {rule.issue_count}
                    </Text>
                  </View>
                </View>

                <Text className="text-[11px] text-slate-400 leading-tight">
                  {rule.description}
                </Text>
              </View>

              {hasIssues ? (
                <View className="flex-row items-center justify-between pt-2 border-t border-dark-border mt-2">
                  <Text className="text-[9px] text-slate-500 font-mono flex-1 mr-2" numberOfLines={1}>
                    Impact: {rule.impact}
                  </Text>
                  <Pressable
                    onPress={() => {
                      setSelectedRule(rule);
                      setModalPage(0);
                    }}
                    className="px-2.5 py-1 rounded-md bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/40"
                  >
                    <Text className="text-[11px] font-bold text-purple-300">View Details</Text>
                  </Pressable>
                </View>
              ) : (
                <View className="flex-row items-center gap-1 pt-2 border-t border-dark-border mt-2">
                  <CheckCircle2 size={12} color="#34d399" />
                  <Text className="text-[10px] font-semibold text-emerald-400">Passing (0 issues)</Text>
                </View>
              )}
            </View>
          );
        })}
      </View>

      {/* ── Compact Drilldown Modal ───────────────────────── */}
      {selectedRule && (
        <Modal visible transparent animationType="fade">
          <View className="flex-1 bg-black/80 justify-center items-center p-3">
            <View className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl max-h-[85vh] overflow-hidden flex-col">
              {/* Modal Header */}
              <View className="px-4 py-3 border-b border-dark-border flex-row items-center justify-between bg-slate-900/60">
                <View>
                  <View className="flex-row items-center gap-2">
                    <Text className="text-[11px] font-mono font-bold text-purple-400">
                      {selectedRule.rule_code}
                    </Text>
                    <Text className="text-sm font-bold text-white">{selectedRule.rule_name}</Text>
                  </View>
                  <Text className="text-[11px] text-slate-400 mt-0.5">{selectedRule.description}</Text>
                </View>

                <View className="flex-row items-center gap-2">
                  <Pressable
                    className="p-1.5 rounded-lg bg-purple-600/20 hover:bg-purple-600/40 border border-purple-500/40 flex-row items-center gap-1"
                    onPress={() => handleExportIssues(selectedRule.rule_code)}
                    disabled={isExportingModal}
                  >
                    {isExportingModal ? (
                      <ActivityIndicator size="small" color="#c084fc" />
                    ) : (
                      <Download size={13} color="#c084fc" />
                    )}
                    <Text className="text-[11px] font-bold text-purple-300">Export CSV</Text>
                  </Pressable>

                  <Pressable
                    onPress={() => setSelectedRule(null)}
                    className="p-1.5 rounded-lg hover:bg-slate-800"
                  >
                    <X size={16} color="#94a3b8" />
                  </Pressable>
                </View>
              </View>

              {/* Modal Body Table */}
              <View className="flex-1 p-3">
                {isLoadingIssues ? (
                  <View className="py-12 items-center justify-center">
                    <ActivityIndicator size="small" color="#a855f7" />
                    <Text className="text-[11px] text-slate-400 mt-2">Loading issue records...</Text>
                  </View>
                ) : !issuesData || issuesData.items.length === 0 ? (
                  <View className="py-12 items-center justify-center">
                    <CheckCircle2 size={28} color="#34d399" />
                    <Text className="text-xs font-semibold text-slate-300 mt-2">
                      No violations found for this rule.
                    </Text>
                  </View>
                ) : (
                  <ScrollView className="flex-1">
                    <View className="w-full divide-y divide-dark-border border border-dark-border rounded-lg overflow-hidden">
                      <View className="flex-row items-center px-3 py-2 bg-slate-900/60">
                        <Text className="w-16 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                          Rec ID
                        </Text>
                        <Text className="w-44 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                          Employee
                        </Text>
                        <Text className="w-24 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                          Sal Month
                        </Text>
                        <Text className="flex-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                          Violation Detail
                        </Text>
                      </View>

                      {issuesData.items.map((issue, idx) => (
                        <View
                          key={idx}
                          className="flex-row items-center px-3 py-2 hover:bg-dark-bg/40 transition-colors"
                        >
                          <Text className="w-16 text-[11px] font-mono text-slate-400">
                            #{issue.record_id}
                          </Text>
                          <View className="w-44 pr-2">
                            <Text className="text-[11px] font-bold text-white" numberOfLines={1}>
                              {issue.emp_name || "N/A"}
                            </Text>
                            <Text className="text-[9px] text-slate-500 font-mono">
                              Code: {issue.emp_code || "N/A"}
                            </Text>
                          </View>
                          <Text className="w-24 text-[11px] font-mono text-purple-300 font-semibold">
                            {issue.sal_month}
                          </Text>
                          <Text className="flex-1 text-[11px] text-rose-300 font-mono">
                            {issue.issue_detail}
                          </Text>
                        </View>
                      ))}
                    </View>
                  </ScrollView>
                )}
              </View>

              {/* Modal Pagination Footer */}
              {issuesData && issuesData.total > pageSize && (
                <View className="px-4 py-2 bg-slate-900/60 border-t border-dark-border flex-row items-center justify-between">
                  <Text className="text-[11px] text-slate-400 font-mono">
                    Page {modalPage + 1} of {Math.ceil(issuesData.total / pageSize)}
                  </Text>
                  <View className="flex-row items-center gap-1.5">
                    <Pressable
                      disabled={modalPage === 0}
                      onPress={() => setModalPage((p) => Math.max(0, p - 1))}
                      className="p-1 rounded-md border border-dark-border bg-dark-card"
                    >
                      <ChevronLeft size={14} color="#94a3b8" />
                    </Pressable>
                    <Pressable
                      disabled={modalPage >= Math.ceil(issuesData.total / pageSize) - 1}
                      onPress={() => setModalPage((p) => p + 1)}
                      className="p-1 rounded-md border border-dark-border bg-dark-card"
                    >
                      <ChevronRight size={14} color="#94a3b8" />
                    </Pressable>
                  </View>
                </View>
              )}
            </View>
          </View>
        </Modal>
      )}
    </View>
  );
}
