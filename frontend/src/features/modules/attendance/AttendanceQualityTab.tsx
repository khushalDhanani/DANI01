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
  Search,
  ShieldCheck,
  X,
} from "lucide-react-native";
import { downloadAttendanceQualityIssuesExport } from "@/api/attendance.api";
import { THEME_COLORS } from "@/constants/theme";
import {
  useAttendanceQuality,
  useAttendanceQualityIssues,
} from "@/hooks/useAttendance";

export function AttendanceQualityTab() {
  const { data: qualityData, isLoading, error } = useAttendanceQuality();

  const [selectedIssueCode, setSelectedIssueCode] = useState<string | null>(null);
  const [selectedRuleName, setSelectedRuleName] = useState<string>("");
  const [issueSearch, setIssueSearch] = useState<string>("");
  const [page, setPage] = useState<number>(0);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const pageSize = 20;

  const { data: issuesData, isLoading: isLoadingIssues, isFetching: isFetchingIssues } =
    useAttendanceQualityIssues(
      selectedIssueCode || undefined,
      issueSearch.trim() || undefined,
      pageSize,
      page * pageSize
    );

  const handleOpenDrilldown = (ruleCode: string, ruleName: string) => {
    setSelectedIssueCode(ruleCode);
    setSelectedRuleName(ruleName);
    setIssueSearch("");
    setPage(0);
  };

  const handleExportIssues = async () => {
    if (!selectedIssueCode) return;
    try {
      setIsExporting(true);
      await downloadAttendanceQualityIssuesExport(
        selectedIssueCode,
        issueSearch.trim() || undefined
      );
    } catch (err) {
      console.error("Export issues failed:", err);
    } finally {
      setIsExporting(false);
    }
  };

  if (isLoading) {
    return (
      <View className="py-20 items-center justify-center">
        <ActivityIndicator size="large" color="#a855f7" />
        <Text className="text-xs text-slate-400 mt-3 font-medium">
          Evaluating 14 Attendance & Leave SSoT quality rules...
        </Text>
      </View>
    );
  }

  if (error || !qualityData) {
    return (
      <View className="py-8 items-center justify-center bg-dark-card border border-dark-border rounded-xl p-4">
        <AlertTriangle size={32} color={THEME_COLORS.danger} />
        <Text className="text-sm font-semibold text-slate-300 mt-2">
          Failed to load Attendance Data Quality analysis.
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
  } = qualityData;

  const totalPages = issuesData ? Math.ceil(issuesData.total / pageSize) : 0;

  return (
    <View className="gap-4">
      {/* Top Health Score Banner */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-3 mb-4 flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <View className="flex-row items-center gap-4 flex-1">
          <View className="relative items-center justify-center">
            <View className="w-16 h-16 rounded-full bg-purple-950/40 border-2 border-purple-500/40 items-center justify-center">
              <Text className="text-xl font-black text-purple-400">
                {overall_health_score}%
              </Text>
            </View>
          </View>
          <View className="flex-1">
            <View className="flex-row items-center gap-2">
              <ShieldCheck size={18} color="#c084fc" />
              <Text className="text-base font-bold text-white">
                Attendance & Leave Quality Index
              </Text>
            </View>
            <Text className="text-xs text-slate-400 mt-1 leading-relaxed">
              Evaluating 14 SSoT data integrity rules covering attendance punch logs, shift rosters, overtime minutes, leave applications, and monthly leave balances.
            </Text>
          </View>
        </View>

        {/* Severity Summary Chips */}
        <View className="flex-row items-center gap-2 self-stretch md:self-auto justify-between md:justify-end">
          <View className="bg-rose-950/60 border border-rose-800/60 px-3 py-2 rounded-xl items-center min-w-[80px]">
            <Text className="text-xs font-bold text-rose-400 uppercase tracking-wider">Critical</Text>
            <Text className="text-lg font-black text-rose-300 mt-0.5">{critical_issues_count}</Text>
          </View>
          <View className="bg-amber-950/60 border border-amber-800/60 px-3 py-2 rounded-xl items-center min-w-[80px]">
            <Text className="text-xs font-bold text-amber-400 uppercase tracking-wider">Warning</Text>
            <Text className="text-lg font-black text-amber-300 mt-0.5">{warning_issues_count}</Text>
          </View>
          <View className="bg-blue-950/60 border border-blue-800/60 px-3 py-2 rounded-xl items-center min-w-[80px]">
            <Text className="text-xs font-bold text-blue-400 uppercase tracking-wider">Info</Text>
            <Text className="text-lg font-black text-blue-300 mt-0.5">{info_issues_count}</Text>
          </View>
        </View>
      </View>

      {/* 14 Rule Cards Grid */}
      <View className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {rules.map((rule) => {
          const isCritical = rule.severity === "CRITICAL";
          const isWarning = rule.severity === "WARNING";
          const hasIssues = rule.issue_count > 0;

          return (
            <View
              key={rule.rule_code}
              className={`bg-dark-card border rounded-xl p-4 flex-col justify-between transition-all ${
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
                <View className="flex-row items-start justify-between gap-3 mb-2">
                  <View className="flex-1">
                    <View className="flex-row items-center gap-2 mb-1">
                      <View
                        className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${
                          isCritical
                            ? "bg-rose-950 text-rose-400 border border-rose-800"
                            : isWarning
                            ? "bg-amber-950 text-amber-400 border border-amber-800"
                            : "bg-blue-950 text-blue-400 border border-blue-800"
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
                      <Text className="text-xs font-mono text-slate-500 font-bold">
                        {rule.rule_code}
                      </Text>
                    </View>
                    <Text className="text-sm font-bold text-white leading-snug">
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
                      {rule.issue_count.toLocaleString()}
                    </Text>
                    <Text className="text-[10px] text-slate-500 font-medium">
                      {hasIssues ? "issues" : "clean"}
                    </Text>
                  </View>
                </View>

                <Text className="text-xs text-slate-400 leading-relaxed mb-3">
                  {rule.description}
                </Text>
              </View>

              {/* Action Footer */}
              {hasIssues ? (
                <Pressable
                  onPress={() => handleOpenDrilldown(rule.rule_code, rule.rule_name)}
                  className={`mt-2 py-2 px-3 rounded-lg border flex-row items-center justify-between active:opacity-80 ${
                    isCritical
                      ? "bg-rose-900/30 border-rose-700/50 text-rose-300"
                      : isWarning
                      ? "bg-amber-900/30 border-amber-700/50 text-amber-300"
                      : "bg-blue-900/30 border-blue-700/50 text-blue-300"
                  }`}
                >
                  <Text
                    className={`text-xs font-bold ${
                      isCritical
                        ? "text-rose-300"
                        : isWarning
                        ? "text-amber-300"
                        : "text-blue-300"
                    }`}
                  >
                    Drilldown {rule.issue_count.toLocaleString()} Violating Records
                  </Text>
                  <ChevronRight
                    size={14}
                    color={
                      isCritical
                        ? "#fca5a5"
                        : isWarning
                        ? "#fde047"
                        : "#93c5fd"
                    }
                  />
                </Pressable>
              ) : (
                <View className="mt-2 py-1.5 flex-row items-center gap-1.5">
                  <CheckCircle2 size={14} color={THEME_COLORS.successIcon} />
                  <Text className="text-xs font-semibold text-emerald-400">
                    Rule passing cleanly
                  </Text>
                </View>
              )}
            </View>
          );
        })}
      </View>

      {/* Drilldown Modal */}
      {selectedIssueCode && (
        <Modal
          animationType="fade"
          transparent={true}
          visible={Boolean(selectedIssueCode)}
          onRequestClose={() => setSelectedIssueCode(null)}
        >
          <View className="flex-1 bg-black/80 justify-center items-center p-4">
            <View className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl max-h-[85vh] flex-col overflow-hidden shadow-2xl">
              {/* Modal Header */}
              <View className="flex-row items-center justify-between p-3 border-b border-dark-border bg-dark-bg/60">
                <View className="flex-1 pr-4">
                  <View className="flex-row items-center gap-2 mb-1">
                    <View className="bg-purple-950/80 border border-purple-800/60 px-2 py-0.5 rounded">
                      <Text className="text-[10px] font-mono font-bold text-purple-300">
                        {selectedIssueCode}
                      </Text>
                    </View>
                    <Text className="text-xs uppercase font-bold text-slate-400 tracking-wider">
                      Quality Issue Drilldown
                    </Text>
                  </View>
                  <Text className="text-lg font-bold text-white">{selectedRuleName}</Text>
                </View>

                <Pressable
                  onPress={() => setSelectedIssueCode(null)}
                  className="p-1 rounded-lg hover:bg-dark-border text-slate-400"
                >
                  <X size={20} color={THEME_COLORS.textMuted} />
                </Pressable>
              </View>

              {/* Modal Toolbar */}
              <View className="p-4 border-b border-dark-border bg-dark-card flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
                <View className="flex-1 flex-row items-center bg-dark-bg border border-dark-border rounded-xl px-3 py-1.5">
                  <Search size={14} color={THEME_COLORS.textMuted} />
                  <TextInput
                    className="flex-1 ml-2 text-xs text-white placeholder:text-slate-500 font-sans outline-none"
                    placeholder="Search record ID, employee name, employee code..."
                    placeholderTextColor="#64748b"
                    value={issueSearch}
                    onChangeText={(t) => {
                      setIssueSearch(t);
                      setPage(0);
                    }}
                  />
                </View>

                <Pressable
                  className="flex-row items-center justify-center gap-2 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/40 px-3.5 py-1.5 rounded-xl"
                  onPress={handleExportIssues}
                  disabled={isExporting}
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
                      <Text className="w-36 text-[11px] font-bold uppercase tracking-wider text-slate-400">Context Info</Text>
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
                          <Text className="text-xs text-purple-300 font-medium font-mono" numberOfLines={1}>
                            {it.context_info || "N/A"}
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
                        page + 1 >= totalPages
                          ? "opacity-30"
                          : "bg-dark-card hover:border-slate-600"
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
