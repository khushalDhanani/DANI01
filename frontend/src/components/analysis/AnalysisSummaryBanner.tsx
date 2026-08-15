import React from "react";
import { Pressable, Text, View } from "react-native";
import {
  Activity,
  CheckCircle2,
  Clock,
  Columns,
  RotateCcw,
  ShieldAlert,
  ShieldCheck,
  Table,
} from "lucide-react-native";
import type { DatabaseAnalysisResponse } from "@/types/analysis.types";
import { MetricCard } from "@/components/ui/MetricCard";
import { AnalysisStatusSummary } from "@/components/visualizations/AnalysisStatusSummary";
import { formatDurationMs, formatNumber } from "@/utils/formatters";
import { THEME_COLORS } from "@/constants/theme";

interface AnalysisSummaryBannerProps {
  result: DatabaseAnalysisResponse;
  onReset: () => void;
}

export const AnalysisSummaryBanner: React.FC<AnalysisSummaryBannerProps> = ({
  result,
  onReset,
}) => {
  const isComplete =
    result.status === "COMPLETED" || result.status === "COMPLETED_WITH_ERRORS";
  const hasErrors =
    result.status === "COMPLETED_WITH_ERRORS" || result.tables_failed > 0;

  return (
    <View className="gap-4">
      {/* ── Status Header ────────────────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 flex-row items-center justify-between flex-wrap gap-3">
        <View className="flex-row items-center gap-3">
          <View
            className={`w-9 h-9 rounded-lg items-center justify-center ${
              isComplete
                ? hasErrors
                  ? "bg-amber-950/80 border border-amber-600/40"
                  : "bg-emerald-950/80 border border-emerald-600/40"
                : "bg-rose-950/80 border border-rose-600/40"
            }`}
          >
            {isComplete ? (
              hasErrors ? (
                <ShieldAlert size={18} color={THEME_COLORS.warningIcon} />
              ) : (
                <CheckCircle2 size={18} color={THEME_COLORS.successIcon} />
              )
            ) : (
              <ShieldAlert size={18} color={THEME_COLORS.dangerIcon} />
            )}
          </View>
          <View>
            <View className="flex-row items-center gap-2">
              <Text className="text-sm font-bold text-white font-mono">
                {result.database} Analysis
              </Text>
              <View
                className={`px-2 py-0.5 rounded border ${
                  isComplete
                    ? hasErrors
                      ? "bg-amber-950/70 border-amber-600/40"
                      : "bg-emerald-950/70 border-emerald-600/40"
                    : "bg-rose-950/70 border-rose-600/40"
                }`}
              >
                <Text
                  className={`text-[10px] font-mono font-bold ${
                    isComplete
                      ? hasErrors
                        ? "text-amber-400"
                        : "text-emerald-400"
                      : "text-rose-400"
                  }`}
                >
                  {result.status}
                </Text>
              </View>
            </View>

            <View className="flex-row items-center gap-2 mt-0.5">
              <Clock size={11} color={THEME_COLORS.textMuted} />
              <Text className="text-[11px] text-slate-400">
                Completed in {formatDurationMs(result.duration_ms)}
              </Text>
            </View>
          </View>
        </View>

        <Pressable
          onPress={onReset}
          className="bg-slate-900 border border-dark-border hover:bg-slate-800 px-3.5 py-2 rounded-lg flex-row items-center gap-1.5"
        >
          <RotateCcw size={13} color={THEME_COLORS.textMuted} />
          <Text className="text-xs font-semibold text-slate-300">
            Configure New Run
          </Text>
        </Pressable>
      </View>

      {/* ── Summary Metric Cards Grid ────────────────────── */}
      <View className="flex-row flex-wrap gap-3">
        <MetricCard
          label="Tables Analyzed"
          value={`${formatNumber(result.tables_analyzed)} / ${formatNumber(result.tables_total)}`}
          sublabel={`${formatNumber(result.tables_skipped)} skipped (empty/filtered)`}
          icon={<Table size={15} color={THEME_COLORS.primaryIcon} />}
          accentBorder="border-blue-500/30"
        />

        <MetricCard
          label="Columns Profiled"
          value={formatNumber(result.columns_profiled)}
          sublabel={`${formatNumber(result.columns_discovered)} discovered`}
          icon={<Columns size={15} color={THEME_COLORS.accentIcon} />}
          accentBorder="border-purple-500/30"
        />

        <MetricCard
          label="Classifications"
          value={formatNumber(result.columns_classified)}
          sublabel="Semantic & sensitivity tags"
          icon={<ShieldCheck size={15} color={THEME_COLORS.successIcon} />}
          accentBorder="border-emerald-500/30"
        />

        <MetricCard
          label="Failed Tables"
          value={result.tables_failed}
          sublabel={result.tables_failed === 0 ? "Zero errors" : "Inspection errors"}
          icon={<Activity size={15} color={result.tables_failed === 0 ? THEME_COLORS.successIcon : THEME_COLORS.dangerIcon} />}
          accentBorder={result.tables_failed === 0 ? "border-emerald-500/30" : "border-rose-500/30"}
        />
      </View>

      {/* ── Visual Analysis Execution Summary & Leaderboard ── */}
      <AnalysisStatusSummary result={result} />
    </View>
  );
};
