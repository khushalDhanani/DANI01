import React, { useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Database,
  Download,
  FileCode,
  RefreshCw,
  Search,
  X,
} from "lucide-react-native";
import {
  ActivityIndicator,
  Modal,
  Pressable,
  ScrollView,
  Text,
  TextInput,
  View,
} from "react-native";
import { procedureLogicApi } from "@/api/procedure_logic.api";
import { THEME_COLORS } from "@/constants/theme";
import {
  useLogicInconsistencies,
  useProcedureLogicOverview,
  useSqlObjectDetail,
  useSqlObjectsCatalog,
} from "@/hooks/useProcedureLogic";

export type ProcedureLogicTabType = "overview" | "inconsistencies" | "catalog";

export const ProcedureLogicModuleScreen: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ProcedureLogicTabType>("overview");
  const [selectedSeverity, setSelectedSeverity] = useState<string | undefined>(undefined);
  const [selectedObjectType, setSelectedObjectType] = useState<string | undefined>(undefined);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [inspectObjectId, setInspectObjectId] = useState<number | null>(null);


  const {
    data: overviewData,
    isLoading: loadingOverview,
    refetch: refetchOverview,
  } = useProcedureLogicOverview();

  const {
    data: catalogData,
    isLoading: loadingCatalog,
    refetch: refetchCatalog,
  } = useSqlObjectsCatalog({
    objectType: selectedObjectType,
    search: searchTerm || undefined,
    limit: 50,
    offset: 0,
  });

  const {
    data: inconsistenciesData,
    isLoading: loadingInconsistencies,
    refetch: refetchInconsistencies,
  } = useLogicInconsistencies({
    severity: selectedSeverity,
    search: searchTerm || undefined,
    limit: 50,
    offset: 0,
  });

  const { data: detailData, isLoading: loadingDetail } = useSqlObjectDetail(inspectObjectId);

  const handleRefresh = () => {
    refetchOverview();
    refetchCatalog();
    refetchInconsistencies();
  };

  const handleExport = () => {
    procedureLogicApi.exportInconsistencies({
      severity: selectedSeverity,
      search: searchTerm || undefined,
    });
  };


  return (
    <ScrollView className="flex-1 bg-dark-bg p-3 md:p-4" showsVerticalScrollIndicator={false}>
      {/* ── Compact Header Banner ──────────────────────────── */}
      <View className="flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
        <View className="flex-1 flex-row items-center gap-3">
          <View className="bg-purple-950/80 border border-purple-800/60 px-2 py-0.5 rounded">
            <Text className="text-[10px] font-mono font-bold text-purple-400">SQL METADATA</Text>
          </View>
          <View>
            <Text className="text-lg md:text-xl font-black text-white leading-tight">Stored Procedure Analyzer</Text>
            <Text className="text-[11px] text-slate-400" numberOfLines={1}>
              Inspects Procedures, Functions, Views & Triggers for logic predicates.
            </Text>
          </View>
        </View>

        <View className="flex-row items-center gap-2 self-start md:self-auto">
            <Pressable
              onPress={handleExport}
              accessibilityRole="button"
              accessibilityLabel="Export logic inconsistencies CSV"
              className="flex-row items-center gap-1.5 bg-dark-card border border-dark-border px-2.5 py-1.5 rounded-lg active:bg-slate-800 transition-all"
            >
              <Download size={12} color={THEME_COLORS.primaryIcon} />
              <Text className="text-[11px] font-bold text-slate-300">Export</Text>
            </Pressable>

            <Pressable
              onPress={handleRefresh}
              accessibilityRole="button"
              accessibilityLabel="Refresh SQL analysis"
              className="flex-row items-center gap-1.5 bg-dark-card border border-dark-border px-2.5 py-1.5 rounded-lg active:bg-slate-800 transition-all"
            >
              <RefreshCw size={12} color={THEME_COLORS.primaryIcon} />
              <Text className="text-[11px] font-bold text-slate-300">Sync</Text>
            </Pressable>
          </View>
        </View>

        {/* ── Navigation Tabs ────────────────────────────────── */}
        <View className="flex-row flex-wrap items-center gap-1.5 border-b border-dark-border pb-2 mb-3">
          {[
            { id: "overview", label: "Overview & Taxonomy", icon: Activity, count: overviewData?.total_sql_objects },
            { id: "inconsistencies", label: "Logic Inconsistency Matrix", icon: AlertTriangle, count: overviewData?.total_inconsistencies },
            { id: "catalog", label: "SQL Objects Catalog", icon: Database, count: catalogData?.total },
          ].map((tab) => {
            const Icon = tab.icon;
            const isSelected = activeTab === tab.id;
            return (
              <Pressable
                key={tab.id}
                onPress={() => setActiveTab(tab.id as ProcedureLogicTabType)}
                className={`flex-row items-center gap-1.5 px-3 py-1.5 rounded-lg border transition-all ${
                  isSelected
                    ? "bg-purple-600 border-purple-400 shadow-sm"
                    : "bg-dark-card border-dark-border hover:border-slate-600"
                }`}
              >
                <Icon size={12} color={isSelected ? "#ffffff" : "#94a3b8"} />
                <Text
                  className={`text-xs font-bold ${
                    isSelected ? "text-white" : "text-slate-400"
                  }`}
                >
                  {tab.label}
                </Text>
                {tab.count !== undefined && (
                  <View
                    className={`px-1.5 py-0.2 rounded ${
                      isSelected ? "bg-purple-800 text-white" : "bg-dark-bg border border-dark-border text-slate-400"
                    }`}
                  >
                    <Text className={`text-[9px] font-mono font-bold ${isSelected ? "text-white" : "text-slate-300"}`}>
                      {tab.count}
                    </Text>
                  </View>
                )}
              </Pressable>
            );
          })}
        </View>

      {/* ── Main Tab Content ─────────────────────────────────── */}
      <View className="flex-1">
        {/* OVERVIEW TAB */}
        {activeTab === "overview" && (
          <View className="gap-4">
            {loadingOverview ? (
              <View className="p-12 items-center justify-center">
                <ActivityIndicator size="large" color="#a855f7" />
                <Text className="text-xs text-slate-400 mt-2">Parsing SQL definitions and analyzing predicates...</Text>
              </View>
            ) : overviewData ? (
              <>
                {/* Metric Summary Cards */}
                <View className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <View className="bg-dark-card border border-dark-border p-3 rounded-lg">
                    <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Total Scanned SQL Objects</Text>
                    <Text className="text-xl md:text-xl font-black text-white mt-1 font-mono">{overviewData.total_sql_objects}</Text>
                    <Text className="text-[10px] text-slate-400 mt-0.5">Stored Procedures, Functions, Views &amp; Triggers</Text>
                  </View>

                  <View className="bg-dark-card border border-dark-border p-3 rounded-lg">
                    <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Logic Inconsistencies</Text>
                    <Text className="text-xl md:text-xl font-black text-amber-400 mt-1 font-mono">{overviewData.total_inconsistencies}</Text>
                    <Text className="text-[10px] text-slate-400 mt-0.5">Predicate variations across procedures</Text>
                  </View>

                  <View className="bg-dark-card border border-dark-border p-3 rounded-lg">
                    <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Critical Conflicts</Text>
                    <Text className="text-xl md:text-xl font-black text-rose-400 mt-1 font-mono">{overviewData.critical_inconsistencies_count}</Text>
                    <Text className="text-[10px] text-slate-400 mt-0.5">Missing soft-delete or resign date checks</Text>
                  </View>

                  <View className="bg-dark-card border border-dark-border p-3 rounded-lg">
                    <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Warning Conflicts</Text>
                    <Text className="text-xl md:text-xl font-black text-amber-300 mt-1 font-mono">{overviewData.warning_inconsistencies_count}</Text>
                    <Text className="text-[10px] text-slate-400 mt-0.5">Missing active assignment/reporting flags</Text>
                  </View>
                </View>

                {/* Object Types & Modules Distribution */}
                <View className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <View className="bg-dark-card border border-dark-border p-3 md:p-4 rounded-lg">
                    <Text className="text-xs font-bold text-white mb-3">SQL Object Types Distribution</Text>
                    <View className="gap-2">
                      {[
                        { label: "Stored Procedures", count: overviewData.total_stored_procedures, color: "bg-purple-500" },
                        { label: "Functions (Scalar & Table)", count: overviewData.total_functions, color: "bg-blue-500" },
                        { label: "Views", count: overviewData.total_views, color: "bg-emerald-500" },
                        { label: "Triggers", count: overviewData.total_triggers, color: "bg-amber-500" },
                      ].map((item) => (
                        <View key={item.label} className="flex-row items-center justify-between bg-dark-bg p-2 rounded border border-dark-border">
                          <View className="flex-row items-center gap-2">
                            <View className={`w-2 h-2 rounded-full ${item.color}`} />
                            <Text className="text-[11px] text-slate-300">{item.label}</Text>
                          </View>
                          <Text className="text-[11px] font-mono font-bold text-white">{item.count}</Text>
                        </View>
                      ))}
                    </View>
                  </View>

                  <View className="bg-dark-card border border-dark-border p-3 md:p-4 rounded-lg">
                    <Text className="text-xs font-bold text-white mb-3">Workforce Module Distribution</Text>
                    <View className="gap-2">
                      {Object.entries(overviewData.module_distribution).map(([mod, cnt]) => (
                        <View key={mod} className="flex-row items-center justify-between bg-dark-bg p-2 rounded border border-dark-border">
                          <Text className="text-[11px] font-bold text-purple-400 font-mono">{mod}</Text>
                          <Text className="text-[11px] font-mono font-bold text-white">{cnt} Objects</Text>
                        </View>
                      ))}
                    </View>
                  </View>
                </View>

                {/* Business Rules Taxonomy Cards */}
                <View className="bg-dark-card border border-dark-border p-3 md:p-4 rounded-lg">
                  <Text className="text-xs font-bold text-white mb-1">Target Business Rule Concepts Taxonomy</Text>
                  <Text className="text-[11px] text-slate-400 mb-3">Single-source-of-truth canonical predicate recommendations for core workforce concepts.</Text>
                  <View className="gap-2.5">
                    {overviewData.business_rules.map((rule) => (
                      <View key={rule.rule_code} className="bg-dark-bg border border-dark-border p-3 rounded-lg">
                        <View className="flex-row items-center justify-between mb-1">
                          <View className="flex-row items-center gap-2">
                            <Text className="text-[11px] font-bold text-purple-400 font-mono">{rule.rule_code}</Text>
                            <Text className="text-[11px] font-bold text-white">— {rule.rule_name}</Text>
                          </View>
                          <View className="bg-purple-950 border border-purple-800 px-2 py-0.5 rounded">
                            <Text className="text-[9px] font-mono font-bold text-purple-300">{rule.objects_count} SQL Objects</Text>
                          </View>
                        </View>
                        <Text className="text-[11px] text-slate-300 mb-2">{rule.description}</Text>
                        <View className="bg-black/50 p-2 rounded border border-dark-border">
                          <Text className="text-[9px] uppercase font-bold text-emerald-400 mb-0.5">Recommended Canonical SSoT Predicate:</Text>
                          <Text className="text-[11px] font-mono text-emerald-300">{rule.canonical_recommendation}</Text>
                        </View>
                      </View>
                    ))}
                  </View>
                </View>
              </>
            ) : null}
          </View>
        )}

        {/* LOGIC INCONSISTENCY MATRIX TAB */}
        {activeTab === "inconsistencies" && (
          <View className="gap-3">
            {/* Filter Bar */}
            <View className="flex-col md:flex-row md:items-center justify-between gap-2 bg-dark-card border border-dark-border p-2.5 rounded-lg">
              <View className="flex-row items-center gap-2 flex-1">
                <Search size={13} color={THEME_COLORS.textMuted} />
                <TextInput
                  value={searchTerm}
                  onChangeText={setSearchTerm}
                  placeholder="Search predicate, object name, or rule..."
                  placeholderTextColor="#64748b"
                  className="flex-1 text-xs text-white p-0 bg-transparent"
                />
              </View>

              <View className="flex-row items-center gap-2">
                {["ALL", "CRITICAL", "WARNING", "INFO"].map((sev) => {
                  const isSel = (sev === "ALL" && !selectedSeverity) || selectedSeverity === sev;
                  return (
                    <Pressable
                      key={sev}
                      onPress={() => setSelectedSeverity(sev === "ALL" ? undefined : sev)}
                      className={`px-2.5 py-1 rounded transition-all ${
                        isSel ? "bg-purple-600 border border-purple-400" : "bg-dark-bg border border-dark-border"
                      }`}
                    >
                      <Text className={`text-[10px] font-bold ${isSel ? "text-white" : "text-slate-400"}`}>{sev}</Text>
                    </Pressable>
                  );
                })}
              </View>
            </View>

            {loadingInconsistencies ? (
              <View className="p-12 items-center justify-center">
                <ActivityIndicator size="large" color="#a855f7" />
                <Text className="text-xs text-slate-400 mt-2">Loading logic inconsistencies...</Text>
              </View>
            ) : inconsistenciesData && inconsistenciesData.items.length > 0 ? (
              <View className="gap-3">
                {inconsistenciesData.items.map((item) => (
                  <View key={item.inconsistency_id} className="bg-dark-card border border-dark-border p-3 md:p-4 rounded-lg">
                    <View className="flex-row items-center justify-between mb-2">
                      <View className="flex-row items-center gap-2">
                        <View
                          className={`px-2 py-0.5 rounded border ${
                            item.severity === "CRITICAL"
                              ? "bg-rose-950 border-rose-800"
                              : item.severity === "WARNING"
                              ? "bg-amber-950 border-amber-800"
                              : "bg-blue-950 border-blue-800"
                          }`}
                        >
                          <Text
                            className={`text-[9px] font-black tracking-wider ${
                              item.severity === "CRITICAL"
                                ? "text-rose-300"
                                : item.severity === "WARNING"
                                ? "text-amber-300"
                                : "text-blue-300"
                            }`}
                          >
                            {item.severity}
                          </Text>
                        </View>

                        <Text className="text-xs font-bold text-white">{item.rule_name}</Text>
                        <Text className="text-[10px] font-mono text-purple-400">({item.rule_code})</Text>
                      </View>

                      <View className="bg-dark-bg border border-dark-border px-2 py-0.5 rounded">
                        <Text className="text-[10px] font-mono font-bold text-slate-300">{item.affected_objects_count} Objects Affected</Text>
                      </View>
                    </View>

                    {/* Predicate Used */}
                    <View className="bg-black/60 p-2.5 rounded border border-dark-border mb-2.5">
                      <Text className="text-[9px] font-bold text-slate-400 uppercase tracking-wider mb-1">Extracted SQL Predicate Used:</Text>
                      <Text className="text-[11px] font-mono text-amber-200">{item.predicate_used}</Text>
                    </View>

                    {/* Difference & Risk */}
                    <View className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-2.5">
                      <View className="bg-dark-bg p-2.5 rounded border border-dark-border">
                        <Text className="text-[10px] font-bold text-slate-300 mb-0.5">Difference Analysis:</Text>
                        <Text className="text-[11px] text-slate-400">{item.difference_analysis}</Text>
                      </View>
                      <View className="bg-dark-bg p-2.5 rounded border border-dark-border">
                        <Text className="text-[10px] font-bold text-rose-300 mb-0.5">Business Risk:</Text>
                        <Text className="text-[11px] text-slate-400">{item.business_risk}</Text>
                      </View>
                    </View>

                    {/* Canonical Recommendation */}
                    <View className="bg-emerald-950/40 p-2.5 rounded border border-emerald-800/60 mb-2.5">
                      <Text className="text-[9px] font-bold text-emerald-400 uppercase tracking-wider mb-0.5">Recommended Centralized Canonical Predicate:</Text>
                      <Text className="text-[11px] font-mono text-emerald-200">{item.canonical_recommendation}</Text>
                    </View>

                    {/* Affected Objects List */}
                    <View className="flex-row items-center gap-1.5 flex-wrap">
                      <Text className="text-[10px] font-bold text-slate-400">Sample Objects:</Text>
                      {item.sample_objects.map((obj) => (
                        <View key={obj} className="bg-dark-bg border border-dark-border px-2 py-0.5 rounded">
                          <Text className="text-[10px] font-mono text-slate-300">{obj}</Text>
                        </View>
                      ))}
                    </View>
                  </View>
                ))}
              </View>
            ) : (
              <View className="p-12 items-center justify-center bg-dark-card border border-dark-border rounded-lg">
                <CheckCircle2 size={24} color="#10b981" />
                <Text className="text-xs font-bold text-white mt-2">No matching logic inconsistencies found.</Text>
              </View>
            )}
          </View>
        )}

        {/* SQL OBJECTS CATALOG TAB */}
        {activeTab === "catalog" && (
          <View className="gap-3">
            {/* Filter Bar */}
            <View className="flex-col md:flex-row md:items-center justify-between gap-2 bg-dark-card border border-dark-border p-2.5 rounded-lg">
              <View className="flex-row items-center gap-2 flex-1">
                <Search size={13} color={THEME_COLORS.textMuted} />
                <TextInput
                  value={searchTerm}
                  onChangeText={setSearchTerm}
                  placeholder="Search object name or table..."
                  placeholderTextColor="#64748b"
                  className="flex-1 text-xs text-white p-0 bg-transparent"
                />
              </View>

              <View className="flex-row items-center gap-2 overflow-x-auto">
                {["ALL", "PROCEDURE", "FUNCTION", "VIEW", "TRIGGER"].map((ot) => {
                  const isSel = (ot === "ALL" && !selectedObjectType) || selectedObjectType === ot;
                  return (
                    <Pressable
                      key={ot}
                      onPress={() => setSelectedObjectType(ot === "ALL" ? undefined : ot)}
                      className={`px-2.5 py-1 rounded transition-all ${
                        isSel ? "bg-purple-600 border border-purple-400" : "bg-dark-bg border border-dark-border"
                      }`}
                    >
                      <Text className={`text-[10px] font-bold ${isSel ? "text-white" : "text-slate-400"}`}>{ot}</Text>
                    </Pressable>
                  );
                })}
              </View>
            </View>

            {loadingCatalog ? (
              <View className="p-12 items-center justify-center">
                <ActivityIndicator size="large" color="#a855f7" />
                <Text className="text-xs text-slate-400 mt-2">Loading SQL objects catalog...</Text>
              </View>
            ) : catalogData && catalogData.items.length > 0 ? (
              <View className="gap-2">
                {catalogData.items.map((item) => (
                  <Pressable
                    key={item.object_id}
                    onPress={() => setInspectObjectId(item.object_id)}
                    className="bg-dark-card border border-dark-border p-3 rounded-lg hover:border-purple-500/50 transition-all"
                  >
                    <View className="flex-row items-center justify-between mb-1.5">
                      <View className="flex-row items-center gap-2">
                        <Text className="text-xs font-mono font-bold text-purple-400">{item.object_name}</Text>
                        <View className="bg-dark-bg border border-dark-border px-2 py-0.5 rounded">
                          <Text className="text-[9px] font-bold text-slate-300">{item.object_type}</Text>
                        </View>
                        <View className="bg-purple-950 border border-purple-800 px-2 py-0.5 rounded">
                          <Text className="text-[9px] font-bold text-purple-300">{item.related_module}</Text>
                        </View>
                      </View>

                      {/* DML Badges */}
                      <View className="flex-row items-center gap-1">
                        {item.dml_operations.map((op) => (
                          <View
                            key={op}
                            className={`px-1.5 py-0.2 rounded border ${
                              op === "SELECT"
                                ? "bg-slate-800 border-slate-700"
                                : op === "INSERT"
                                ? "bg-emerald-950 border-emerald-800"
                                : op === "UPDATE"
                                ? "bg-amber-950 border-amber-800"
                                : "bg-rose-950 border-rose-800"
                            }`}
                          >
                            <Text
                              className={`text-[8px] font-mono font-bold ${
                                op === "SELECT"
                                  ? "text-slate-300"
                                  : op === "INSERT"
                                  ? "text-emerald-300"
                                  : op === "UPDATE"
                                  ? "text-amber-300"
                                  : "text-rose-300"
                              }`}
                            >
                              {op}
                            </Text>
                          </View>
                        ))}
                      </View>
                    </View>

                    {/* Tables Used */}
                    <View className="flex-row items-center gap-1.5 flex-wrap mb-1.5">
                      <Text className="text-[10px] text-slate-400">Tables Used:</Text>
                      {item.used_tables.map((t) => (
                        <View key={t} className="bg-dark-bg border border-dark-border px-1.5 py-0.5 rounded">
                          <Text className="text-[9px] font-mono text-slate-300">{t}</Text>
                        </View>
                      ))}
                    </View>

                    {/* Definition snippet */}
                    <Text className="text-[10px] font-mono text-slate-400 truncate bg-black/40 p-1.5 rounded">
                      {item.def_snippet}
                    </Text>
                  </Pressable>
                ))}
              </View>
            ) : (
              <View className="p-12 items-center justify-center bg-dark-card border border-dark-border rounded-lg">
                <Text className="text-xs font-bold text-white">No matching SQL objects found.</Text>
              </View>
            )}
          </View>
        )}
      </View>

      {/* ── SQL Definition Inspector Modal ───────────────────── */}
      {inspectObjectId && (
        <Modal visible transparent animationType="fade" onRequestClose={() => setInspectObjectId(null)}>
          <View className="flex-1 bg-black/80 justify-center items-center p-4">
            <View className="bg-dark-card border border-dark-border w-full max-w-4xl max-h-[85vh] rounded-xl overflow-hidden flex-col">
              <View className="p-4 border-b border-dark-border flex-row items-center justify-between bg-dark-bg">
                <View className="flex-row items-center gap-2">
                  <FileCode size={16} color="#a855f7" />
                  <Text className="text-sm font-mono font-bold text-white">
                    {detailData?.object_name || "Inspecting SQL Object..."}
                  </Text>
                  {detailData && (
                    <View className="bg-purple-950 border border-purple-800 px-2 py-0.5 rounded">
                      <Text className="text-[10px] font-bold text-purple-300">{detailData.object_type}</Text>
                    </View>
                  )}
                </View>
                <Pressable onPress={() => setInspectObjectId(null)} className="p-1 rounded hover:bg-dark-card">
                  <X size={16} color="#94a3b8" />
                </Pressable>
              </View>

              <ScrollView className="flex-1 p-4" showsVerticalScrollIndicator>
                {loadingDetail ? (
                  <View className="p-4 items-center justify-center">
                    <ActivityIndicator size="large" color="#a855f7" />
                  </View>
                ) : detailData ? (
                  <View className="gap-3">
                    <View className="flex-row items-center gap-2 flex-wrap">
                      <Text className="text-xs font-bold text-slate-300">Tables Referenced:</Text>
                      {detailData.used_tables.map((t) => (
                        <View key={t} className="bg-dark-bg border border-dark-border px-2 py-0.5 rounded">
                          <Text className="text-[10px] font-mono text-purple-300">{t}</Text>
                        </View>
                      ))}
                    </View>

                    <View className="bg-black/90 p-4 rounded-lg border border-dark-border">
                      <Text className="text-[11px] font-mono text-emerald-300 whitespace-pre-wrap">
                        {detailData.definition}
                      </Text>
                    </View>
                  </View>
                ) : null}
              </ScrollView>
            </View>
          </View>
        </Modal>
      )}
    </ScrollView>
  );
};
