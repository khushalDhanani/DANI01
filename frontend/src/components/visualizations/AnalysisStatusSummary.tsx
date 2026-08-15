import React from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import { Activity, Clock, Gauge, Table } from "lucide-react-native";
import type { DatabaseAnalysisResponse } from "@/types/analysis.types";
import { DistributionBar, type DistributionSegment } from "@/components/visualizations/DistributionBar";
import { formatDurationMs } from "@/utils/formatters";
import { THEME_COLORS } from "@/constants/theme";

interface AnalysisStatusSummaryProps {
  result: DatabaseAnalysisResponse;
}

export const AnalysisStatusSummary: React.FC<AnalysisStatusSummaryProps> = ({
  result,
}) => {
  const router = useRouter();
  const total = result.tables_total || 1;

  // Status Distribution Segments
  const statusSegments: DistributionSegment[] = [
    {
      label: "Completed",
      count: result.tables_analyzed,
      percent: (result.tables_analyzed / total) * 100,
      color: "bg-emerald-400",
      textColor: "text-emerald-400",
    },
    {
      label: "Skipped",
      count: result.tables_skipped,
      percent: (result.tables_skipped / total) * 100,
      color: "bg-amber-400",
      textColor: "text-amber-400",
    },
    {
      label: "Failed",
      count: result.tables_failed,
      percent: (result.tables_failed / total) * 100,
      color: "bg-rose-400",
      textColor: "text-rose-400",
    },
  ];

  // Calculate Throughput / Efficiency
  const durationSec = result.duration_ms > 0 ? result.duration_ms / 1000 : 1;
  const tablesPerSec = (result.tables_analyzed / durationSec).toFixed(1);
  const avgMsPerTable =
    result.tables_analyzed > 0
      ? Math.round(result.duration_ms / result.tables_analyzed)
      : 0;

  // Find Top 4 Slowest Tables
  const slowestTables = [...result.tables]
    .sort((a, b) => (b.duration_ms || 0) - (a.duration_ms || 0))
    .slice(0, 4);

  const maxDuration = Math.max(
    ...slowestTables.map((t) => t.duration_ms || 0),
    1
  );

  return (
    <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-4">
      {/* ── 1. Execution Status Proportions ───────────────── */}
      <View className="gap-2">
        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center gap-2">
            <Activity size={15} color={THEME_COLORS.successIcon} />
            <Text className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Analysis Execution Distribution
            </Text>
          </View>

          <View className="flex-row items-center gap-1.5 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
            <Gauge size={11} color={THEME_COLORS.primaryIcon} />
            <Text className="text-[10px] font-mono text-slate-400">
              Avg: <Text className="font-bold text-blue-400">{avgMsPerTable}ms</Text> / table
            </Text>
          </View>
        </View>

        <DistributionBar
          segments={statusSegments}
          totalCount={result.tables_total}
          totalLabel="Total Tables"
        />
      </View>

      {/* ── 2. Performance Metrics Row ────────────────────── */}
      <View className="flex-row flex-wrap gap-2.5 pt-2 border-t border-slate-800/80">
        <View className="flex-1 min-w-[130px] bg-slate-900/70 border border-slate-800/80 rounded-lg p-2.5">
          <Text className="text-[9px] uppercase font-bold text-slate-500">
            Throughput
          </Text>
          <Text className="text-sm font-mono font-bold text-emerald-400 mt-0.5">
            {tablesPerSec} <Text className="text-[10px] font-normal text-slate-400">tables/sec</Text>
          </Text>
        </View>

        <View className="flex-1 min-w-[130px] bg-slate-900/70 border border-slate-800/80 rounded-lg p-2.5">
          <Text className="text-[9px] uppercase font-bold text-slate-500">
            Columns / Second
          </Text>
          <Text className="text-sm font-mono font-bold text-purple-400 mt-0.5">
            {((result.columns_profiled + result.columns_classified) / durationSec).toFixed(0)} <Text className="text-[10px] font-normal text-slate-400">cols/sec</Text>
          </Text>
        </View>

        <View className="flex-1 min-w-[130px] bg-slate-900/70 border border-slate-800/80 rounded-lg p-2.5">
          <Text className="text-[9px] uppercase font-bold text-slate-500">
            Total Wall Time
          </Text>
          <Text className="text-sm font-mono font-bold text-amber-400 mt-0.5">
            {formatDurationMs(result.duration_ms)}
          </Text>
        </View>
      </View>

      {/* ── 3. Slowest Tables Leaderboard ─────────────────── */}
      {slowestTables.length > 0 && (
        <View className="gap-2 pt-2 border-t border-slate-800/80">
          <View className="flex-row items-center justify-between">
            <Text className="text-[10px] uppercase font-bold text-slate-400">
              Inspection Duration by Table
            </Text>
            <Text className="text-[9px] font-mono text-slate-500">
              Top compute-intensive entities
            </Text>
          </View>

          <View className="gap-1.5">
            {slowestTables.map((t) => {
              const fillPct = Math.min(
                100,
                Math.max(5, (t.duration_ms / maxDuration) * 100)
              );

              return (
                <Pressable
                  key={`${t.schema}.${t.table}`}
                  onPress={() => {
                    const s = encodeURIComponent(t.schema);
                    const tbl = encodeURIComponent(t.table);
                    router.push(`/database/${s}/${tbl}` as Href);
                  }}
                  className="gap-1 p-1.5 rounded-lg hover:bg-slate-900 active:bg-slate-800 transition-colors"
                >
                  <View className="flex-row items-center justify-between">
                    <View className="flex-row items-center gap-1.5">
                      <Table size={12} color={THEME_COLORS.textMuted} />
                      <Text
                        className="text-xs font-mono font-bold text-slate-200"
                        numberOfLines={1}
                      >
                        {t.schema}.{t.table}
                      </Text>
                    </View>

                    <View className="flex-row items-center gap-1">
                      <Clock size={10} color={THEME_COLORS.textMuted} />
                      <Text className="text-[11px] font-mono font-bold text-amber-400">
                        {formatDurationMs(t.duration_ms)}
                      </Text>
                    </View>
                  </View>

                  {/* Duration Fill Bar */}
                  <View className="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                    <View
                      style={{ width: `${fillPct}%` }}
                      className="h-full bg-amber-500 rounded-full"
                    />
                  </View>
                </Pressable>
              );
            })}
          </View>
        </View>
      )}
    </View>
  );
};
