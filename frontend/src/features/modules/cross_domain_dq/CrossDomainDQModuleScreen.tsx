import React, { useState } from "react";
import {
  ActivityIndicator,
  Modal,
  Pressable,
  ScrollView,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "expo-router";
import {
  AlertTriangle,
  Building2,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Download,
  ExternalLink,
  Layers,
  RefreshCw,
  Search,
  ShieldAlert,
  ShieldCheck,
  Table,
  X,
} from "lucide-react-native";
import { downloadCrossDomainExport } from "@/api/cross_domain_dq.api";
import { useCrossDomainIssues, useCrossDomainOverview } from "@/hooks/useCrossDomainDQ";
import type { CrossDomainQualityRuleInfo } from "@/types/cross_domain_dq.types";

type TabKey = "overview" | "evidence" | "rules";

const COMPANY_OPTIONS = [
  { id: undefined, label: "All", code: "ALL" },
  { id: 1, label: "AIL", code: "AIL" },
  { id: 2, label: "ASCL", code: "ASCL" },
];

export function CrossDomainDQModuleScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabKey>("overview");
  const [selectedCompId, setSelectedCompId] = useState<number | undefined>(undefined);

  // Evidence table states
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [selectedRuleCode, setSelectedRuleCode] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [page, setPage] = useState<number>(0);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const pageSize = 20;

  // Drilldown modal states
  const [selectedRuleModal, setSelectedRuleModal] = useState<CrossDomainQualityRuleInfo | null>(null);
  const [modalPage, setModalPage] = useState<number>(0);

  const { data: overview, isLoading: isOverviewLoading } = useCrossDomainOverview(selectedCompId);
  const { data: issuesData, isLoading: isIssuesLoading } = useCrossDomainIssues(
    selectedRuleCode || selectedRuleModal?.rule_code,
    selectedCategory,
    searchTerm,
    pageSize,
    (selectedRuleModal ? modalPage : page) * pageSize,
    selectedCompId,
  );

  const handleRefreshAll = () => {
    queryClient.invalidateQueries({ queryKey: ["crossDomainDQ"] });
  };

  const handleExport = async (ruleCode?: string, cat?: string) => {
    try {
      setIsExporting(true);
      await downloadCrossDomainExport(ruleCode, cat, searchTerm, selectedCompId);
    } catch (err) {
      console.error("Export failed:", err);
    } finally {
      setIsExporting(false);
    }
  };

  const tabs: { key: TabKey; label: string; icon: React.ReactNode; badge?: string }[] = [
    {
      key: "overview",
      label: "Health Overview",
      icon: <ShieldCheck size={14} color={activeTab === "overview" ? "#ffffff" : "#94a3b8"} />,
    },
    {
      key: "evidence",
      label: "Evidence Issues Directory",
      icon: <ShieldAlert size={14} color={activeTab === "evidence" ? "#ffffff" : "#94a3b8"} />,
      badge: overview ? `${overview.total_issues}` : undefined,
    },
    {
      key: "rules",
      label: "15 Rule Matrix",
      icon: <Layers size={14} color={activeTab === "rules" ? "#ffffff" : "#94a3b8"} />,
      badge: "15 Rules",
    },
  ];

  const totalPages = issuesData ? Math.ceil(issuesData.total / pageSize) : 0;

  return (
    <ScrollView className="flex-1 bg-dark-bg p-3 md:p-4" showsVerticalScrollIndicator={false}>
      {/* ── Compact Header Banner ──────────────────────────── */}
      <View className="flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
        <View className="flex-1 flex-row items-center gap-3">
          <View className="bg-rose-950/80 border border-rose-800/60 px-2 py-0.5 rounded">
            <Text className="text-[10px] font-mono font-bold text-rose-400">CROSS_DOMAIN_DQ</Text>
          </View>
          <View>
            <Text className="text-lg md:text-xl font-black text-white leading-tight">
              Cross-Domain Data Quality Intelligence
            </Text>
            <Text className="text-[11px] text-slate-400" numberOfLines={1}>
              Multi-table consistency validation across Employee, Org, Contact, User, Manager, Attendance, Leave & Payroll.
            </Text>
          </View>
        </View>

        <View className="flex-row items-center gap-2 self-start md:self-auto">
          {/* Company Selector */}
          <View className="flex-row items-center bg-dark-card border border-dark-border p-0.5 rounded-lg">
            <View className="px-1.5">
              <Building2 size={12} color="#94a3b8" />
            </View>
            {COMPANY_OPTIONS.map((c) => {
              const isSelected = selectedCompId === c.id;
              return (
                <TouchableOpacity
                  key={c.code}
                  onPress={() => {
                    setSelectedCompId(c.id);
                    setPage(0);
                  }}
                  className={`px-2.5 py-1 rounded-md transition-all ${
                    isSelected ? "bg-purple-600 border border-purple-400" : "border-transparent"
                  }`}
                >
                  <Text
                    className={`text-[11px] font-bold font-mono ${
                      isSelected ? "text-white" : "text-slate-400"
                    }`}
                  >
                    {c.label}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>

          {/* Sync Button */}
          <TouchableOpacity
            onPress={handleRefreshAll}
            className="bg-dark-card border border-dark-border px-2.5 py-1.5 rounded-lg flex-row items-center gap-1.5 active:bg-slate-800"
          >
            <RefreshCw size={12} color="#a855f7" />
            <Text className="text-[11px] font-bold text-slate-300">Sync</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* ── Navigation Tab Bar ─────────────────────────────── */}
      <View className="flex-row flex-wrap items-center gap-1.5 border-b border-dark-border pb-2 mb-3">
        {tabs.map((t) => {
          const isActive = activeTab === t.key;
          return (
            <TouchableOpacity
              key={t.key}
              onPress={() => setActiveTab(t.key)}
              className={`flex-row items-center gap-1.5 px-3 py-1.5 rounded-lg border transition-all ${
                isActive
                  ? "bg-purple-600 border-purple-400 shadow-sm"
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
                    isActive ? "bg-purple-800 text-white" : "bg-dark-bg text-slate-400 border border-dark-border"
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

      {/* TAB 1: OVERVIEW */}
      {activeTab === "overview" && (
        <View className="space-y-3">
          {isOverviewLoading || !overview ? (
            <View className="py-12 items-center justify-center">
              <ActivityIndicator size="small" color="#a855f7" />
              <Text className="text-[11px] text-slate-400 mt-2">Evaluating 15 cross-domain rules...</Text>
            </View>
          ) : (
            <View className="gap-3">
              {/* Top Banner: Score Gauge + Severity Cards */}
              <View className="grid grid-cols-1 lg:grid-cols-4 gap-3">
                {/* Score Circle Card */}
                <View className="bg-dark-card border border-dark-border p-3.5 rounded-xl flex-col items-center justify-center">
                  <View className="w-16 h-16 rounded-full bg-purple-950/40 border-2 border-purple-500/40 items-center justify-center">
                    <Text className="text-xl font-black text-purple-400">{overview.overall_health_score}%</Text>
                  </View>
                  <Text className="text-xs font-bold text-white mt-2">Cross-Domain Quality Index</Text>
                  <Text className="text-[10px] text-slate-400 mt-0.5 text-center font-mono">
                    15 SSoT rules across 8 workforce domains
                  </Text>
                </View>

                {/* 3 Severity Cards */}
                <View className="lg:col-span-3 grid grid-cols-1 sm:grid-cols-4 gap-3">
                  <View className="bg-dark-card border border-rose-900/60 p-3 rounded-xl bg-rose-950/20 flex-col justify-between">
                    <View className="flex-row items-center justify-between mb-1">
                      <Text className="text-[10px] font-bold uppercase tracking-wider text-rose-300">
                        Critical Issues
                      </Text>
                      <AlertTriangle size={14} color="#ef4444" />
                    </View>
                    <Text className="text-xl font-black text-rose-400 font-mono">{overview.critical_issues_count}</Text>
                    <Text className="text-[9px] text-rose-300/70 mt-1 font-mono">Broken references & corrupted data</Text>
                  </View>

                  <View className="bg-dark-card border border-amber-900/60 p-3 rounded-xl bg-amber-950/20 flex-col justify-between">
                    <View className="flex-row items-center justify-between mb-1">
                      <Text className="text-[10px] font-bold uppercase tracking-wider text-amber-300">
                        Warnings
                      </Text>
                      <AlertTriangle size={14} color="#f59e0b" />
                    </View>
                    <Text className="text-xl font-black text-amber-400 font-mono">{overview.warning_issues_count}</Text>
                    <Text className="text-[9px] text-amber-300/70 mt-1 font-mono">Duplicates & missing assignments</Text>
                  </View>

                  <View className="bg-dark-card border border-sky-900/60 p-3 rounded-xl bg-sky-950/20 flex-col justify-between">
                    <View className="flex-row items-center justify-between mb-1">
                      <Text className="text-[10px] font-bold uppercase tracking-wider text-sky-300">
                        Info Rules
                      </Text>
                      <ShieldCheck size={14} color="#38bdf8" />
                    </View>
                    <Text className="text-xl font-black text-sky-400 font-mono">{overview.info_issues_count}</Text>
                    <Text className="text-[9px] text-sky-300/70 mt-1 font-mono">Non-critical review rules</Text>
                  </View>

                  <View className="bg-dark-card border border-purple-900/60 p-3 rounded-xl bg-purple-950/20 flex-col justify-between">
                    <View className="flex-row items-center justify-between mb-1">
                      <Text className="text-[10px] font-bold uppercase tracking-wider text-purple-300">
                        Affected Staff
                      </Text>
                      <ShieldAlert size={14} color="#c084fc" />
                    </View>
                    <Text className="text-xl font-black text-purple-300 font-mono">{overview.total_affected_employees}</Text>
                    <Text className="text-[9px] text-purple-300/70 mt-1 font-mono">Distinct employees affected</Text>
                  </View>
                </View>
              </View>

              {/* Category Breakdown Matrix */}
              <View className="bg-dark-card border border-dark-border rounded-xl p-3">
                <Text className="text-xs font-bold text-white mb-2.5">Domain Category Health Matrix</Text>
                <View className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
                  {overview.categories.map((c) => (
                    <TouchableOpacity
                      key={c.category_code}
                      onPress={() => {
                        setSelectedCategory(c.category_code);
                        setActiveTab("evidence");
                        setPage(0);
                      }}
                      className={`p-2.5 rounded-lg border flex-col justify-between transition-all ${
                        c.total_issues > 0
                          ? c.critical_issues > 0
                            ? "border-rose-800/60 bg-rose-950/10 hover:bg-rose-950/20"
                            : "border-amber-800/60 bg-amber-950/10 hover:bg-amber-950/20"
                          : "border-dark-border bg-slate-900/30"
                      }`}
                    >
                      <View className="flex-row items-center justify-between mb-1">
                        <Text className="text-[11px] font-bold text-white" numberOfLines={1}>
                          {c.category_name}
                        </Text>
                        <Text className="text-[10px] font-mono text-purple-400">{c.rule_count} Rules</Text>
                      </View>

                      <View className="flex-row items-baseline justify-between mt-2">
                        <Text
                          className={`text-lg font-black font-mono ${
                            c.total_issues > 0
                              ? c.critical_issues > 0
                                ? "text-rose-400"
                                : "text-amber-400"
                              : "text-emerald-400"
                          }`}
                        >
                          {c.total_issues}
                        </Text>
                        <Text className="text-[9px] text-slate-500 font-mono">
                          {c.critical_issues} Crit / {c.warning_issues} Warn
                        </Text>
                      </View>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            </View>
          )}
        </View>
      )}

      {/* TAB 2: EVIDENCE ISSUES DIRECTORY */}
      {activeTab === "evidence" && (
        <View className="space-y-3">
          {/* Toolbar */}
          <View className="flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
            <View className="flex-1 flex-row items-center bg-dark-card border border-dark-border px-3 py-1.5 rounded-lg">
              <Search size={14} color="#94a3b8" />
              <TextInput
                className="flex-1 ml-2 text-[11px] text-white outline-none"
                placeholder="Search evidence by EmpCode, Name, Table, or Detail..."
                placeholderTextColor="#64748b"
                value={searchTerm}
                onChangeText={(txt) => {
                  setSearchTerm(txt);
                  setPage(0);
                }}
              />
            </View>

            <View className="flex-row items-center gap-2">
              {(selectedRuleCode || selectedCategory || searchTerm) && (
                <Pressable
                  onPress={() => {
                    setSelectedRuleCode("");
                    setSelectedCategory("");
                    setSearchTerm("");
                    setPage(0);
                  }}
                  className="px-2.5 py-1.5 rounded-lg border border-rose-800/60 bg-rose-950/20"
                >
                  <Text className="text-[11px] font-bold text-rose-300">Reset Filters</Text>
                </Pressable>
              )}

              <Pressable
                className="flex-row items-center gap-1.5 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/40 px-3 py-1.5 rounded-lg"
                onPress={() => handleExport(selectedRuleCode, selectedCategory)}
                disabled={isExporting}
              >
                {isExporting ? (
                  <ActivityIndicator size="small" color="#c084fc" />
                ) : (
                  <Download size={13} color="#c084fc" />
                )}
                <Text className="text-[11px] font-bold text-purple-300">
                  {isExporting ? "Exporting..." : "Export Evidence CSV"}
                </Text>
              </Pressable>
            </View>
          </View>

          {/* Evidence Table */}
          <View className="bg-dark-card border border-dark-border rounded-lg overflow-hidden w-full">
            {isIssuesLoading ? (
              <View className="py-12 items-center justify-center">
                <ActivityIndicator size="small" color="#a855f7" />
                <Text className="text-[11px] text-slate-400 mt-2">Loading evidence records...</Text>
              </View>
            ) : !issuesData || issuesData.items.length === 0 ? (
              <View className="py-12 items-center justify-center">
                <CheckCircle2 size={28} color="#34d399" />
                <Text className="text-xs font-semibold text-slate-300 mt-2">
                  No cross-domain data quality violations found.
                </Text>
              </View>
            ) : (
              <View className="w-full divide-y divide-dark-border">
                {/* Header */}
                <View className="flex-row items-center px-3 py-2 bg-slate-900/60 border-b border-dark-border">
                  <Text className="w-20 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Rec ID
                  </Text>
                  <Text className="w-44 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Employee Identity
                  </Text>
                  <Text className="w-36 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Target Table
                  </Text>
                  <Text className="w-32 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Rule Failed
                  </Text>
                  <Text className="flex-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Evidence Violation Detail
                  </Text>
                </View>

                {/* Rows */}
                {issuesData.items.map((row, idx) => (
                  <View
                    key={`${row.record_id}-${idx}`}
                    className="flex-row items-center px-3 py-2 hover:bg-dark-bg/40 transition-colors"
                  >
                    <Text className="w-20 text-[11px] font-mono text-slate-400">{row.record_id}</Text>

                    <Pressable
                      onPress={() => {
                        if (row.emp_id) {
                          router.push({
                            pathname: "/modules/attendance/employee/[empId]",
                            params: { empId: String(row.emp_id) },
                          });
                        }
                      }}
                      className="w-44 pr-2 flex-row items-center gap-1 group"
                    >
                      <View className="flex-1">
                        <Text
                          className="text-[11px] font-bold text-white group-hover:text-purple-400 underline transition-colors"
                          numberOfLines={1}
                        >
                          {row.emp_name || "N/A"}
                        </Text>
                        <Text className="text-[9px] text-slate-500 font-mono">
                          Code: {row.emp_code || "N/A"}
                        </Text>
                      </View>
                      {row.emp_id && <ExternalLink size={11} color="#c084fc" />}
                    </Pressable>

                    <View className="w-36 pr-2 flex-row items-center gap-1">
                      <Table size={11} color="#94a3b8" />
                      <Text className="text-[10px] font-mono text-slate-300" numberOfLines={1}>
                        {row.table_name}
                      </Text>
                    </View>

                    <View className="w-32 pr-2">
                      <View
                        className={`px-1.5 py-0.5 rounded border self-start ${
                          row.severity === "CRITICAL"
                            ? "bg-rose-950 border-rose-800 text-rose-300"
                            : "bg-amber-950 border-amber-800 text-amber-300"
                        }`}
                      >
                        <Text className="text-[9px] font-mono font-bold" numberOfLines={1}>
                          {row.rule_failed}
                        </Text>
                      </View>
                    </View>

                    <Text className="flex-1 text-[11px] text-rose-300 font-mono" numberOfLines={2}>
                      {row.issue_detail}
                    </Text>
                  </View>
                ))}
              </View>
            )}

            {/* Pagination Footer */}
            {issuesData && totalPages > 1 && (
              <View className="flex-row items-center justify-between px-3 py-2 bg-dark-bg/60 border-t border-dark-border">
                <Text className="text-[11px] text-slate-400">
                  Page <Text className="font-bold text-slate-200">{page + 1}</Text> of{" "}
                  <Text className="font-bold text-slate-200">{totalPages}</Text> ({issuesData.total} evidence items)
                </Text>

                <View className="flex-row items-center gap-1.5">
                  <Pressable
                    className={`p-1 rounded-md border ${
                      page === 0
                        ? "border-dark-border bg-dark-card/50 opacity-40"
                        : "border-dark-border bg-dark-card hover:bg-slate-800"
                    }`}
                    disabled={page === 0}
                    onPress={() => setPage((p) => Math.max(0, p - 1))}
                  >
                    <ChevronLeft size={14} color="#94a3b8" />
                  </Pressable>

                  <Text className="text-[11px] text-slate-300 font-mono">
                    {page + 1} / {totalPages}
                  </Text>

                  <Pressable
                    className={`p-1 rounded-md border ${
                      page >= totalPages - 1
                        ? "border-dark-border bg-dark-card/50 opacity-40"
                        : "border-dark-border bg-dark-card hover:bg-slate-800"
                    }`}
                    disabled={page >= totalPages - 1}
                    onPress={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                  >
                    <ChevronRight size={14} color="#94a3b8" />
                  </Pressable>
                </View>
              </View>
            )}
          </View>
        </View>
      )}

      {/* TAB 3: 15 RULE MATRIX */}
      {activeTab === "rules" && (
        <View className="space-y-3">
          {isOverviewLoading || !overview ? (
            <View className="py-12 items-center justify-center">
              <ActivityIndicator size="small" color="#a855f7" />
            </View>
          ) : (
            <View className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {overview.rules.map((rule) => {
                const isCritical = rule.severity === "CRITICAL";
                const hasIssues = rule.issue_count > 0;


                return (
                  <View
                    key={rule.rule_code}
                    className={`bg-dark-card border rounded-lg p-3 flex-col justify-between transition-all ${
                      hasIssues
                        ? isCritical
                          ? "border-rose-800/60 bg-rose-950/10"
                          : "border-amber-800/60 bg-amber-950/10"
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
                                  : "bg-amber-950 text-amber-400 border border-amber-800"
                              }`}
                            >
                              <Text
                                className={`text-[9px] font-mono font-bold ${
                                  isCritical ? "text-rose-400" : "text-amber-400"
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
                                  : "text-amber-400"
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
                            setSelectedRuleModal(rule);
                            setModalPage(0);
                          }}
                          className="px-2.5 py-1 rounded-md bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/40"
                        >
                          <Text className="text-[11px] font-bold text-purple-300">View Evidence ({rule.issue_count})</Text>
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
          )}
        </View>
      )}

      {/* ── Drilldown Evidence Modal ───────────────────────── */}
      {selectedRuleModal && (
        <Modal visible transparent animationType="fade">
          <View className="flex-1 bg-black/80 justify-center items-center p-3">
            <View className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl max-h-[85vh] overflow-hidden flex-col">
              {/* Modal Header */}
              <View className="px-4 py-3 border-b border-dark-border flex-row items-center justify-between bg-slate-900/60">
                <View>
                  <View className="flex-row items-center gap-2">
                    <Text className="text-[11px] font-mono font-bold text-purple-400">
                      {selectedRuleModal.rule_code}
                    </Text>
                    <Text className="text-sm font-bold text-white">{selectedRuleModal.rule_name}</Text>
                  </View>
                  <Text className="text-[11px] text-slate-400 mt-0.5">{selectedRuleModal.description}</Text>
                </View>

                <View className="flex-row items-center gap-2">
                  <Pressable
                    className="p-1.5 rounded-lg bg-purple-600/20 hover:bg-purple-600/40 border border-purple-500/40 flex-row items-center gap-1"
                    onPress={() => handleExport(selectedRuleModal.rule_code)}
                    disabled={isExporting}
                  >
                    {isExporting ? (
                      <ActivityIndicator size="small" color="#c084fc" />
                    ) : (
                      <Download size={13} color="#c084fc" />
                    )}
                    <Text className="text-[11px] font-bold text-purple-300">Export CSV</Text>
                  </Pressable>

                  <Pressable
                    onPress={() => setSelectedRuleModal(null)}
                    className="p-1.5 rounded-lg hover:bg-slate-800"
                  >
                    <X size={16} color="#94a3b8" />
                  </Pressable>
                </View>
              </View>

              {/* Modal Body Table */}
              <View className="flex-1 p-3">
                {isIssuesLoading ? (
                  <View className="py-12 items-center justify-center">
                    <ActivityIndicator size="small" color="#a855f7" />
                    <Text className="text-[11px] text-slate-400 mt-2">Loading issue evidence records...</Text>
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
                        <Text className="w-20 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                          Rec ID
                        </Text>
                        <Text className="w-44 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                          Employee
                        </Text>
                        <Text className="w-32 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                          Table
                        </Text>
                        <Text className="flex-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                          Evidence Failure Detail
                        </Text>
                      </View>

                      {issuesData.items.map((issue, idx) => (
                        <View
                          key={idx}
                          className="flex-row items-center px-3 py-2 hover:bg-dark-bg/40 transition-colors"
                        >
                          <Text className="w-20 text-[11px] font-mono text-slate-400">
                            {issue.record_id}
                          </Text>
                          <View className="w-44 pr-2">
                            <Text className="text-[11px] font-bold text-white" numberOfLines={1}>
                              {issue.emp_name || "N/A"}
                            </Text>
                            <Text className="text-[9px] text-slate-500 font-mono">
                              Code: {issue.emp_code || "N/A"}
                            </Text>
                          </View>
                          <Text className="w-32 text-[11px] font-mono text-slate-300" numberOfLines={1}>
                            {issue.table_name}
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
    </ScrollView>
  );
}
