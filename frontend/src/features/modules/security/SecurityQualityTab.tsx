import React, { useState } from "react";
import {
  ActivityIndicator,
  Modal,
  Pressable,
  ScrollView,
  Text,
  TextInput,
  View,
} from "react-native";
import {
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Download,
  Info,
  Search,
  Shield,
  ShieldAlert,
  ShieldCheck,
  X,
} from "lucide-react-native";
import { downloadSecurityQualityIssuesExport } from "@/api/security.api";
import { THEME_COLORS } from "@/constants/theme";
import {
  useSecurityQuality,
  useSecurityQualityIssues,
} from "@/hooks/useSecurity";
import type { SecurityQualityRuleResult } from "@/types/security.types";

export function SecurityQualityTab() {
  const { data: qualityData, isLoading, isError } = useSecurityQuality();
  const [selectedSeverity, setSelectedSeverity] = useState<string>("ALL");
  const [drilldownRule, setDrilldownRule] = useState<SecurityQualityRuleResult | null>(null);

  // Drilldown state
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [page, setPage] = useState<number>(0);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const pageSize = 20;

  const {
    data: issuesData,
    isLoading: isLoadingIssues,
    isFetching: isFetchingIssues,
  } = useSecurityQualityIssues(
    drilldownRule ? drilldownRule.rule_code : "",
    searchTerm.trim() || undefined,
    pageSize,
    page * pageSize
  );

  const handleOpenDrilldown = (rule: SecurityQualityRuleResult) => {
    setDrilldownRule(rule);
    setSearchTerm("");
    setPage(0);
  };

  const handleCloseDrilldown = () => {
    setDrilldownRule(null);
    setSearchTerm("");
    setPage(0);
  };

  const handleExportIssues = async () => {
    if (!drilldownRule) return;
    try {
      setIsExporting(true);
      await downloadSecurityQualityIssuesExport(
        drilldownRule.rule_code,
        searchTerm.trim() || undefined
      );
    } catch (err) {
      console.error("Export error:", err);
    } finally {
      setIsExporting(false);
    }
  };

  if (isLoading) {
    return (
      <View className="py-8 items-center justify-center">
        <ActivityIndicator size="large" color="#a855f7" />
        <Text className="text-sm text-slate-400 mt-3 font-medium">Running security and access audit...</Text>
      </View>
    );
  }

  if (isError || !qualityData) {
    return (
      <View className="py-8 items-center justify-center">
        <AlertTriangle size={36} color={THEME_COLORS.dangerIcon} />
        <Text className="text-sm text-red-400 mt-3 font-medium">Failed to load security audit results.</Text>
      </View>
    );
  }

  const filteredRules = qualityData.rules.filter((r) => {
    if (selectedSeverity === "ALL") return true;
    return r.severity === selectedSeverity;
  });

  const totalPages = issuesData ? Math.ceil(issuesData.total / pageSize) : 0;

  return (
    <View className="gap-4">
      {/* Top Health Score Banner */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-3 mb-4 flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <View className="flex-row items-center gap-4 flex-1">
          <View className="w-14 h-14 rounded-xl bg-purple-950/80 border border-purple-800/60 items-center justify-center">
            <ShieldCheck size={28} color="#a855f7" />
          </View>
          <View className="flex-1">
            <Text className="text-base font-bold text-white mb-1">Security & Access Health Score</Text>
            <Text className="text-xs text-slate-400 leading-relaxed">
              Automated audit of 14 Single-Source-of-Truth RBAC integrity rules evaluating broken employee linkages, inactive employee exposure, duplicate accounts, and missing privileges.
            </Text>
          </View>
        </View>

        <View className="flex-row items-center gap-3 self-start md:self-auto">
          <View className="bg-dark-bg border border-dark-border rounded-xl px-5 py-2.5 items-center">
            <Text
              className={`text-xl font-bold ${
                qualityData.overall_security_score >= 90
                  ? "text-emerald-400"
                  : qualityData.overall_security_score >= 70
                  ? "text-amber-400"
                  : "text-rose-400"
              }`}
            >
              {qualityData.overall_security_score}%
            </Text>
            <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Health Index</Text>
          </View>
        </View>
      </View>

      {/* Severity Counters */}
      <View className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
        <Pressable
          onPress={() => setSelectedSeverity("ALL")}
          className={`p-3.5 rounded-xl border flex-row items-center justify-between ${
            selectedSeverity === "ALL"
              ? "bg-purple-950/40 border-purple-500"
              : "bg-dark-card border-dark-border hover:border-slate-700"
          }`}
        >
          <View className="flex-row items-center gap-2.5">
            <Shield size={18} color="#c084fc" />
            <Text className="text-xs font-bold text-slate-200">All Audited Rules</Text>
          </View>
          <Text className="text-sm font-bold text-purple-400">{qualityData.rules.length}</Text>
        </Pressable>

        <Pressable
          onPress={() => setSelectedSeverity("CRITICAL")}
          className={`p-3.5 rounded-xl border flex-row items-center justify-between ${
            selectedSeverity === "CRITICAL"
              ? "bg-rose-950/40 border-rose-500"
              : "bg-dark-card border-dark-border hover:border-slate-700"
          }`}
        >
          <View className="flex-row items-center gap-2.5">
            <ShieldAlert size={18} color="#f43f5e" />
            <Text className="text-xs font-bold text-slate-200">Critical Risks</Text>
          </View>
          <Text className="text-sm font-bold text-rose-400">{qualityData.critical_issues_count}</Text>
        </Pressable>

        <Pressable
          onPress={() => setSelectedSeverity("WARNING")}
          className={`p-3.5 rounded-xl border flex-row items-center justify-between ${
            selectedSeverity === "WARNING"
              ? "bg-amber-950/40 border-amber-500"
              : "bg-dark-card border-dark-border hover:border-slate-700"
          }`}
        >
          <View className="flex-row items-center gap-2.5">
            <AlertTriangle size={18} color="#f59e0b" />
            <Text className="text-xs font-bold text-slate-200">Warnings</Text>
          </View>
          <Text className="text-sm font-bold text-amber-400">{qualityData.warning_issues_count}</Text>
        </Pressable>

        <Pressable
          onPress={() => setSelectedSeverity("INFO")}
          className={`p-3.5 rounded-xl border flex-row items-center justify-between ${
            selectedSeverity === "INFO"
              ? "bg-blue-950/40 border-blue-500"
              : "bg-dark-card border-dark-border hover:border-slate-700"
          }`}
        >
          <View className="flex-row items-center gap-2.5">
            <Info size={18} color="#38bdf8" />
            <Text className="text-xs font-bold text-slate-200">Informational</Text>
          </View>
          <Text className="text-sm font-bold text-blue-400">{qualityData.info_issues_count}</Text>
        </Pressable>
      </View>

      {/* Rules Catalog List */}
      <View className="space-y-3 mb-4">
        {filteredRules.map((rule) => {
          const isCritical = rule.severity === "CRITICAL";
          const isWarning = rule.severity === "WARNING";
          const hasIssues = rule.issue_count > 0;

          return (
            <Pressable
              key={rule.rule_code}
              onPress={() => handleOpenDrilldown(rule)}
              className="bg-dark-card border border-dark-border hover:border-purple-500/50 rounded-xl p-4 transition-colors mb-3"
            >
              <View className="flex-col md:flex-row items-start md:items-center justify-between gap-2 mb-2">
                <View className="flex-row items-center gap-2.5 flex-1">
                  {isCritical ? (
                    <ShieldAlert size={18} color="#f43f5e" />
                  ) : isWarning ? (
                    <AlertTriangle size={18} color="#f59e0b" />
                  ) : (
                    <Info size={18} color="#38bdf8" />
                  )}
                  <Text className="text-sm font-bold text-white">{rule.rule_name}</Text>
                  <Text className="text-[10px] font-mono text-slate-500 bg-dark-bg px-2 py-0.5 rounded border border-dark-border">
                    {rule.rule_code}
                  </Text>
                </View>

                <View className="flex-row items-center gap-2 self-start md:self-auto">
                  <View
                    className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                      isCritical
                        ? "bg-rose-950/60 border-rose-800/60 text-rose-400"
                        : isWarning
                        ? "bg-amber-950/60 border-amber-800/60 text-amber-400"
                        : "bg-blue-950/60 border-blue-800/60 text-blue-400"
                    }`}
                  >
                    <Text
                      className={`text-[9px] font-bold ${
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

                  <View
                    className={`px-2.5 py-0.5 rounded-full border ${
                      hasIssues
                        ? isCritical
                          ? "bg-rose-950/80 border-rose-600 text-rose-300"
                          : "bg-amber-950/80 border-amber-600 text-amber-300"
                        : "bg-emerald-950/80 border-emerald-600 text-emerald-300"
                    }`}
                  >
                    <Text
                      className={`text-[10px] font-bold ${
                        hasIssues
                          ? isCritical
                            ? "text-rose-300"
                            : "text-amber-300"
                          : "text-emerald-300"
                      }`}
                    >
                      {rule.issue_count.toLocaleString()} {rule.issue_count === 1 ? "issue" : "issues"}
                    </Text>
                  </View>
                </View>
              </View>

              <Text className="text-xs text-slate-300 mb-2 leading-relaxed">{rule.description}</Text>

              <View className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2 pt-2 border-t border-dark-border/40">
                <View className="flex-row items-start gap-1.5">
                  <Text className="text-[10px] font-bold uppercase text-slate-500">Impact:</Text>
                  <Text className="text-[11px] text-slate-400 flex-1">{rule.impact}</Text>
                </View>
                <View className="flex-row items-start gap-1.5">
                  <Text className="text-[10px] font-bold uppercase text-slate-500">Action:</Text>
                  <Text className="text-[11px] text-purple-300 flex-1">{rule.recommendation}</Text>
                </View>
              </View>
            </Pressable>
          );
        })}
      </View>

      {/* Drilldown Modal */}
      {drilldownRule && (
        <Modal
          visible={Boolean(drilldownRule)}
          transparent
          animationType="fade"
          onRequestClose={handleCloseDrilldown}
        >
          <View className="flex-1 bg-black/80 items-center justify-center p-4">
            <View className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl max-h-[85vh] flex-col overflow-hidden shadow-2xl">
              {/* Modal Header */}
              <View className="flex-row items-center justify-between px-5 py-4 border-b border-dark-border bg-dark-bg/60">
                <View className="flex-row items-center gap-3 flex-1 pr-4">
                  {drilldownRule.severity === "CRITICAL" ? (
                    <ShieldAlert size={22} color="#f43f5e" />
                  ) : drilldownRule.severity === "WARNING" ? (
                    <AlertTriangle size={22} color="#f59e0b" />
                  ) : (
                    <Info size={22} color="#38bdf8" />
                  )}
                  <View className="flex-1">
                    <View className="flex-row items-center gap-2">
                      <Text className="text-base font-bold text-white" numberOfLines={1}>
                        {drilldownRule.rule_name}
                      </Text>
                      <View className="px-2 py-0.5 rounded bg-dark-card border border-dark-border">
                        <Text className="text-[10px] font-mono text-purple-400 font-bold">
                          {drilldownRule.rule_code}
                        </Text>
                      </View>
                    </View>
                    <Text className="text-xs text-slate-400 mt-0.5">
                      {issuesData?.total.toLocaleString() || drilldownRule.issue_count.toLocaleString()} violating records detected
                    </Text>
                  </View>
                </View>
                <Pressable
                  onPress={handleCloseDrilldown}
                  className="p-1 rounded-lg hover:bg-dark-border text-slate-400"
                >
                  <X size={20} color={THEME_COLORS.textMuted} />
                </Pressable>
              </View>

              {/* Search & Export Subbar */}
              <View className="flex-row items-center justify-between gap-3 px-5 py-3 border-b border-dark-border bg-dark-card">
                <View className="flex-1 flex-row items-center bg-dark-bg border border-dark-border rounded-xl px-3 py-1.5">
                  <Search size={14} color={THEME_COLORS.textMuted} />
                  <TextInput
                    className="flex-1 ml-2 text-xs text-white placeholder:text-slate-500 font-sans outline-none"
                    placeholder="Search violating records, usernames, or details..."
                    placeholderTextColor="#64748b"
                    value={searchTerm}
                    onChangeText={(t) => {
                      setSearchTerm(t);
                      setPage(0);
                    }}
                  />
                </View>

                <Pressable
                  onPress={handleExportIssues}
                  disabled={isExporting}
                  className="flex-row items-center gap-1.5 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/40 px-3 py-1.5 rounded-lg"
                >
                  {isExporting ? (
                    <ActivityIndicator size="small" color="#c084fc" />
                  ) : (
                    <Download size={14} color="#c084fc" />
                  )}
                  <Text className="text-xs font-bold text-purple-300">
                    {isExporting ? "Exporting..." : "Export CSV"}
                  </Text>
                </Pressable>
              </View>

              {/* Table / List */}
              {isLoadingIssues ? (
                <View className="py-8 items-center justify-center">
                  <ActivityIndicator size="large" color="#a855f7" />
                  <Text className="text-xs text-slate-400 mt-2">Loading issue records...</Text>
                </View>
              ) : !issuesData || issuesData.items.length === 0 ? (
                <View className="py-8 items-center justify-center">
                  <CheckCircle2 size={32} color={THEME_COLORS.successIcon} />
                  <Text className="text-sm font-semibold text-slate-300 mt-2">No violating records found.</Text>
                  <Text className="text-xs text-slate-500 mt-1">This security check is passing cleanly.</Text>
                </View>
              ) : (
                <ScrollView className="flex-1 w-full" showsVerticalScrollIndicator={false}>
                  <View className="w-full divide-y divide-dark-border">
                    {/* Table Header */}
                    <View className="flex-row items-center px-4 py-2.5 bg-dark-bg/60 border-b border-dark-border">
                      <Text className="w-16 text-[11px] font-bold uppercase tracking-wider text-slate-400">ID</Text>
                      <Text className="w-48 text-[11px] font-bold uppercase tracking-wider text-slate-400">Entity</Text>
                      <Text className="w-36 text-[11px] font-bold uppercase tracking-wider text-slate-400">Role / Context</Text>
                      <Text className="flex-1 min-w-[200px] text-[11px] font-bold uppercase tracking-wider text-slate-400">Violation Details</Text>
                      <Text className="w-32 text-[11px] font-bold uppercase tracking-wider text-slate-400 text-right">Status</Text>
                    </View>

                    {/* Table Rows */}
                    {issuesData.items.map((it, idx) => (
                      <View
                        key={`${it.record_id}-${idx}`}
                        className="flex-row items-center px-4 py-3 hover:bg-dark-bg/40"
                      >
                        <Text className="w-16 text-xs font-mono text-slate-400">#{it.record_id}</Text>
                        <View className="w-48 pr-2">
                          <Text className="text-xs font-bold text-white" numberOfLines={1}>
                            {it.entity_name}
                          </Text>
                          <Text className="text-[10px] text-slate-500 uppercase font-mono">{it.entity_type}</Text>
                        </View>
                        <View className="w-36 pr-2">
                          <Text className="text-xs text-purple-300 font-medium" numberOfLines={1}>
                            {it.account_role || "N/A"}
                          </Text>
                        </View>
                        <View className="flex-1 min-w-[200px] pr-2">
                          <Text className="text-xs text-slate-300 leading-tight">
                            {it.issue_detail}
                          </Text>
                        </View>
                        <View className="w-32 items-end">
                          <View className="px-2 py-0.5 rounded bg-dark-bg border border-dark-border">
                            <Text className="text-[10px] font-bold text-slate-400" numberOfLines={1}>
                              {it.status_detail || "VIOLATION"}
                            </Text>
                          </View>
                        </View>
                      </View>
                    ))}
                  </View>
                </ScrollView>
              )}


              {/* Modal Pagination Footer */}
              {issuesData && issuesData.total > 0 && (
                <View className="flex-row items-center justify-between px-5 py-3 border-t border-dark-border bg-dark-bg/60">
                  <Text className="text-xs text-slate-400 font-medium">
                    Showing {page * pageSize + 1}–
                    {Math.min((page + 1) * pageSize, issuesData.total)} of{" "}
                    {issuesData.total.toLocaleString()} issues
                    {isFetchingIssues && " (Updating...)"}
                  </Text>

                  <View className="flex-row items-center gap-2">
                    <Pressable
                      className={`p-1.5 rounded-lg border border-dark-border ${
                        page === 0 ? "opacity-30" : "bg-dark-card hover:border-slate-600"
                      }`}
                      onPress={() => setPage((p) => Math.max(0, p - 1))}
                      disabled={page === 0}
                    >
                      <ChevronLeft size={16} color={THEME_COLORS.primaryIcon} />
                    </Pressable>
                    <Text className="text-xs text-slate-300 font-mono px-1">
                      {page + 1} / {Math.max(1, totalPages)}
                    </Text>
                    <Pressable
                      className={`p-1.5 rounded-lg border border-dark-border ${
                        page + 1 >= totalPages ? "opacity-30" : "bg-dark-card hover:border-slate-600"
                      }`}
                      onPress={() => setPage((p) => p + 1)}
                      disabled={page + 1 >= totalPages}
                    >
                      <ChevronRight size={16} color={THEME_COLORS.primaryIcon} />
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
