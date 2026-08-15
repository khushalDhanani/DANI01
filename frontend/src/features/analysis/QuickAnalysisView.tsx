import React, { useRef, useState } from "react";
import { FlatList, Pressable, ScrollView, Text, TextInput, View } from "react-native";
import { AlertTriangle, Filter, Search } from "lucide-react-native";
import { useDatabaseSummary, useSchemas } from "@/hooks/useDatabase";
import { useRunQuickAnalysis } from "@/hooks/useAnalysis";
import type { DatabaseAnalysisResponse, TableAnalysisSummary } from "@/types/analysis.types";
import { AnalysisConfigCard } from "@/components/analysis/AnalysisConfigCard";
import { AnalysisRunningCard } from "@/components/analysis/AnalysisRunningCard";
import { AnalysisSummaryBanner } from "@/components/analysis/AnalysisSummaryBanner";
import { AnalysisTableResultCard } from "@/components/analysis/AnalysisTableResultCard";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { THEME_COLORS } from "@/constants/theme";

type StatusFilter = "ALL" | "COMPLETED" | "SKIPPED" | "FAILED";

export const QuickAnalysisView: React.FC = () => {
  const [result, setResult] = useState<DatabaseAnalysisResponse | null>(null);
  const [isStoppedWaiting, setIsStoppedWaiting] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("ALL");
  const [schemaFilter, setSchemaFilter] = useState<string>("ALL");
  const [currentScopeText, setCurrentScopeText] = useState<string>("Entire Database");

  const abortControllerRef = useRef<AbortController | null>(null);

  // Database metadata queries for context
  const { data: summary } = useDatabaseSummary();
  const { data: schemasData } = useSchemas();

  // Quick analysis mutation
  const runMutation = useRunQuickAnalysis();

  const handleStartAnalysis = (config: {
    schema?: string | null;
    maxConcurrent: number;
  }) => {
    setIsStoppedWaiting(false);
    setResult(null);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    const scope = config.schema ? `Schema [${config.schema}]` : "Entire Database";
    setCurrentScopeText(scope);

    runMutation.mutate(
      {
        payload: {
          schema: config.schema,
          max_concurrent: config.maxConcurrent,
        },
        signal: controller.signal,
      },
      {
        onSuccess: (data) => {
          setResult(data);
          abortControllerRef.current = null;
        },
        onError: () => {
          abortControllerRef.current = null;
        },
      }
    );
  };

  const handleStopWaiting = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStoppedWaiting(true);
  };

  const handleReset = () => {
    setResult(null);
    setIsStoppedWaiting(false);
    runMutation.reset();
  };

  const isRunning = runMutation.isPending && !isStoppedWaiting;

  // Filter table results if results exist
  const tableResults = result?.tables || [];
  const filteredTables = tableResults.filter((t) => {
    const matchesSearch =
      t.table.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.schema.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus =
      statusFilter === "ALL" ? true : t.status === statusFilter;

    const matchesSchema =
      schemaFilter === "ALL" ? true : t.schema.toLowerCase() === schemaFilter.toLowerCase();

    return matchesSearch && matchesStatus && matchesSchema;
  });

  // If not displaying results, use ScrollView for form / status views
  if (!result) {
    return (
      <ScrollView
        style={{ flex: 1, height: "100%" }}
        contentContainerStyle={{ flexGrow: 1, paddingBottom: 24, gap: 16 }}
        showsVerticalScrollIndicator={true}
        keyboardShouldPersistTaps="handled"
      >
        {/* ── 1. Configuration State (Idle) ────────────────── */}
        {!isRunning && !isStoppedWaiting && (
          <AnalysisConfigCard
            databaseName={summary?.database || "AIRIS_TEST"}
            totalTables={summary?.table_count}
            schemas={schemasData}
            isRunning={isRunning}
            onStartAnalysis={handleStartAnalysis}
          />
        )}

        {/* ── 2. Long-Running State ────────────────────────── */}
        {isRunning && (
          <AnalysisRunningCard
            onStopWaiting={handleStopWaiting}
            scopeText={currentScopeText}
          />
        )}

        {/* ── 3. Stopped Waiting State ─────────────────────── */}
        {isStoppedWaiting && (
          <View className="bg-dark-card border border-amber-600/40 rounded-xl p-4 gap-3">
            <View className="flex-row items-center gap-2.5">
              <AlertTriangle size={18} color={THEME_COLORS.warningIcon} />
              <Text className="text-sm font-bold text-white">
                Stopped Waiting for HTTP Response
              </Text>
            </View>
            <Text className="text-xs text-slate-400 leading-relaxed">
              The client HTTP connection was aborted. The backend analysis job may continue executing on SQL Server in the background.
            </Text>
            <Pressable
              onPress={handleReset}
              className="bg-blue-600 active:bg-blue-700 self-start px-3.5 py-1.5 rounded-lg mt-1"
            >
              <Text className="text-xs font-bold text-white">Configure New Run</Text>
            </Pressable>
          </View>
        )}

        {/* ── 4. Error State (Network/Timeout) ─────────────── */}
        {runMutation.isError && !isStoppedWaiting && (
          <ErrorState
            message={
              runMutation.error?.message ||
              "Quick analysis failed to complete within the timeout window."
            }
            onRetry={handleReset}
          />
        )}
      </ScrollView>
    );
  }

  // ── 5. Results & Virtualized Table List (Unified Header) ──
  return (
    <View style={{ flex: 1, height: "100%", minHeight: 0 }}>
      <FlatList<TableAnalysisSummary>
        style={{ flex: 1 }}
        data={filteredTables}
        keyExtractor={(item) => `${item.schema}.${item.table}`}
        renderItem={({ item }) => (
          <AnalysisTableResultCard tableResult={item} />
        )}
        ItemSeparatorComponent={() => <View className="h-2" />}
        showsVerticalScrollIndicator={true}
        contentContainerStyle={{ paddingBottom: 32 }}
        initialNumToRender={15}
        maxToRenderPerBatch={20}
        windowSize={7}
        ListHeaderComponent={
          <View className="gap-3.5 mb-3">
            <AnalysisSummaryBanner result={result} onReset={handleReset} />

            {/* ── Filters Bar ──────────────────────────────── */}
            <View className="bg-dark-card border border-dark-border p-2.5 rounded-xl gap-2.5">
              <View className="flex-row items-center justify-between flex-wrap gap-2">
                {/* Search Bar */}
                <View className="flex-row items-center flex-1 min-w-[180px] bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1">
                  <Search size={13} color={THEME_COLORS.textMuted} />
                  <TextInput
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                    placeholder={`Search ${tableResults.length} analyzed tables…`}
                    placeholderTextColor={THEME_COLORS.textDark}
                    className="flex-1 text-xs text-white px-2 py-0"
                    autoCapitalize="none"
                  />
                </View>

                {/* Status Filter Pills */}
                <View className="flex-row items-center gap-1">
                  {(["ALL", "COMPLETED", "SKIPPED", "FAILED"] as StatusFilter[]).map(
                    (st) => (
                      <Pressable
                        key={st}
                        onPress={() => setStatusFilter(st)}
                        className={`px-2 py-1 rounded text-xs ${
                          statusFilter === st
                            ? "bg-blue-600 border border-blue-500"
                            : "bg-slate-900 border border-slate-800"
                        }`}
                      >
                        <Text
                          className={`text-[10px] font-mono font-bold ${
                            statusFilter === st ? "text-white" : "text-slate-400"
                          }`}
                        >
                          {st}
                        </Text>
                      </Pressable>
                    )
                  )}
                </View>
              </View>

              {/* Schema Filter Pills */}
              <View className="flex-row items-center gap-1.5 flex-wrap pt-1 border-t border-slate-800/80">
                <Filter size={11} color={THEME_COLORS.textDark} />
                <Text className="text-[10px] font-bold uppercase text-slate-500 mr-1">
                  Schema:
                </Text>
                {["ALL", "dbo", "cvai"].map((sch) => (
                  <Pressable
                    key={sch}
                    onPress={() => setSchemaFilter(sch)}
                    className={`px-2 py-0.5 rounded border ${
                      schemaFilter === sch
                        ? "bg-purple-950/80 border-purple-600/40"
                        : "bg-slate-900 border-slate-800"
                    }`}
                  >
                    <Text
                      className={`text-[10px] font-mono ${
                        schemaFilter === sch
                          ? "text-purple-300 font-bold"
                          : "text-slate-400"
                      }`}
                    >
                      {sch}
                    </Text>
                  </Pressable>
                ))}
              </View>
            </View>
          </View>
        }
        ListEmptyComponent={
          <EmptyState
            title="No matching tables"
            message="No table results match your current search and filter criteria."
          />
        }
      />
    </View>
  );
};
