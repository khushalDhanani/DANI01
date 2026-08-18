import React, { useState } from "react";
import { BarChart3, Layers, RefreshCw } from "lucide-react-native";
import { Pressable, Text, View } from "react-native";
import { PageContainer } from "@/components/layout/PageContainer";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { ModuleHeader } from "@/features/modules/components/ModuleHeader";
import { ModuleTablesList } from "@/features/modules/components/ModuleTablesList";
import { PersonMetricsView } from "@/features/modules/person/PersonMetricsView";
import { PersonOverview } from "@/features/modules/person/PersonOverview";
import {
  useModuleDefinition,
  useModuleValidation,
  usePersonMetrics,
} from "@/hooks/useModules";
import type {
  PersonModuleMetricsResponse,
  PersonMetricsResponseLite,
} from "@/types/modules.types";
import { THEME_COLORS } from "@/constants/theme";

type ModuleTab = "metrics" | "overview";

const selectPersonMetricsLite = (
  res: PersonModuleMetricsResponse,
): PersonMetricsResponseLite => ({
  metrics: res.metrics,
  duration_ms: res.duration_ms,
});

export default function DayliteDashboardScreen() {
  const [activeTab, setActiveTab] = useState<ModuleTab>("metrics");

  // Queries for PERSON module
  const {
    data: moduleDef,
    isLoading: isLoadingDef,
    isError: isErrorDef,
    error: errorDef,
    refetch: refetchDef,
  } = useModuleDefinition("PERSON");

  const {
    data: validation,
    isLoading: isLoadingVal,
  } = useModuleValidation("PERSON");

  const {
    data: personMetrics,
    isLoading: isLoadingMetrics,
    isError: isErrorMetrics,
    error: errorMetrics,
    refetch: refetchMetrics,
    isRefetching,
  } = usePersonMetrics(selectPersonMetricsLite);

  const handleRetryAll = () => {
    refetchDef();
    refetchMetrics();
  };

  if (isErrorDef && !moduleDef) {
    return (
      <PageContainer>
        <ErrorState
          message={errorDef?.message || "Failed to load Person module definition."}
          onRetry={handleRetryAll}
          title="Failed to load Day Lite Person"
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      {/* ── Top Header ────────────────────────────────────────── */}
      <ModuleHeader
        module={moduleDef}
        validation={validation}
        isLoading={isLoadingDef || isLoadingVal}
      />

      {/* ── Tab Switcher & Quick Refresh Bar ──────────────────── */}
      <View className="flex-row items-center justify-between border-b border-dark-border mb-3.5 gap-2">
        <View className="flex-row items-center gap-1">
          <Pressable
            onPress={() => setActiveTab("metrics")}
            accessibilityRole="tab"
            accessibilityState={{ selected: activeTab === "metrics" }}
            className={`flex-row items-center gap-1.5 px-3 py-2 border-b-2 transition-all ${
              activeTab === "metrics"
                ? "border-blue-500 bg-blue-500/5"
                : "border-transparent hover:bg-slate-800/40"
            }`}
          >
            <BarChart3
              size={14}
              color={activeTab === "metrics" ? THEME_COLORS.primaryIcon : THEME_COLORS.textMuted}
            />
            <Text
              className={`text-xs font-bold ${
                activeTab === "metrics" ? "text-white" : "text-slate-400"
              }`}
            >
              KPI Metrics
            </Text>
            <View className="bg-emerald-950/60 border border-emerald-800/60 px-1 py-0.1 rounded">
              <Text className="text-[8px] font-mono font-bold text-emerald-300">
                LIVE
              </Text>
            </View>
          </Pressable>

          <Pressable
            onPress={() => setActiveTab("overview")}
            accessibilityRole="tab"
            accessibilityState={{ selected: activeTab === "overview" }}
            className={`flex-row items-center gap-1.5 px-3 py-2 border-b-2 transition-all ${
              activeTab === "overview"
                ? "border-blue-500 bg-blue-500/5"
                : "border-transparent hover:bg-slate-800/40"
            }`}
          >
            <Layers
              size={14}
              color={activeTab === "overview" ? THEME_COLORS.primaryIcon : THEME_COLORS.textMuted}
            />
            <Text
              className={`text-xs font-bold ${
                activeTab === "overview" ? "text-white" : "text-slate-400"
              }`}
            >
              Overview & Schema
            </Text>
          </Pressable>
        </View>

        {/* Compact Refresh */}
        <Pressable
          onPress={() => refetchMetrics()}
          disabled={isLoadingMetrics || isRefetching}
          accessibilityRole="button"
          accessibilityLabel="Refresh metrics"
          className="flex-row items-center gap-1 px-2.5 py-1 rounded bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 transition-all mb-1"
        >
          <RefreshCw
            size={11}
            color={THEME_COLORS.textMuted}
            className={isRefetching ? "animate-spin" : ""}
          />
          <Text className="text-[10px] text-slate-300 font-medium">
            {isRefetching ? "Updating…" : "Refresh"}
          </Text>
        </Pressable>
      </View>

      {/* ── Tab Content ────────────────────────────────────────── */}
      {isLoadingDef ? (
        <View className="gap-3">
          <LoadingSkeleton height={80} borderRadius={10} />
          <LoadingSkeleton height={160} borderRadius={10} />
        </View>
      ) : activeTab === "metrics" ? (
        /* Metrics Tab */
        <View>
          {isErrorMetrics ? (
            <ErrorState
              message={errorMetrics?.message || "Failed to calculate Person Metrics."}
              onRetry={() => refetchMetrics()}
              title="Failed to calculate Person Metrics"
            />
          ) : (
            <PersonMetricsView
              metricsResponse={personMetrics}
              isLoading={isLoadingMetrics}
            />
          )}
        </View>
      ) : (
        /* Overview Tab */
        <View className="gap-4">
          <PersonOverview
            metricsResponse={personMetrics}
            isLoading={isLoadingMetrics}
          />

          {moduleDef && (
            <ModuleTablesList module={moduleDef} validation={validation} />
          )}
        </View>
      )}
    </PageContainer>
  );
}
