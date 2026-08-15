import React from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import {
  ChevronRight,
  Clock,
  Columns,
  Database,
  ShieldAlert,
  Table,
} from "lucide-react-native";
import type { TableAnalysisSummary } from "@/types/analysis.types";
import { formatDurationMs, formatNumber } from "@/utils/formatters";
import { THEME_COLORS } from "@/constants/theme";

interface AnalysisTableResultCardProps {
  tableResult: TableAnalysisSummary;
}

export const AnalysisTableResultCard: React.FC<AnalysisTableResultCardProps> = ({
  tableResult,
}) => {
  const router = useRouter();

  const handlePress = () => {
    const safeSchema = encodeURIComponent(tableResult.schema);
    const safeTable = encodeURIComponent(tableResult.table);
    router.push(`/database/${safeSchema}/${safeTable}` as Href);
  };

  const isCompleted = tableResult.status === "COMPLETED";
  const isSkipped = tableResult.status === "SKIPPED";
  const isFailed = tableResult.status === "FAILED";

  const getStatusBadge = () => {
    if (isCompleted) {
      return { bg: "bg-emerald-950/80", border: "border-emerald-600/40", text: "text-emerald-400" };
    }
    if (isSkipped) {
      return { bg: "bg-slate-900", border: "border-slate-800", text: "text-slate-400" };
    }
    return { bg: "bg-rose-950/80", border: "border-rose-600/40", text: "text-rose-400" };
  };

  const statusBadge = getStatusBadge();

  return (
    <Pressable
      onPress={handlePress}
      className="bg-dark-card border border-dark-border rounded-xl p-3 hover:border-slate-700 active:bg-slate-900/80 gap-2 transition-colors"
    >
      {/* ── Top Row: Table Name + Status + Duration ─────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2">
        <View className="flex-row items-center gap-2 flex-1 min-w-[180px]">
          <View className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
            <Table size={14} color={THEME_COLORS.primaryIcon} />
          </View>
          <View className="flex-1">
            <View className="flex-row items-center gap-1.5 flex-wrap">
              <Text className="text-xs font-mono font-bold text-white" numberOfLines={1}>
                {tableResult.table}
              </Text>
              <View className="bg-slate-900 px-1.5 py-0.2 rounded border border-slate-800">
                <Text className="text-[9px] font-mono text-slate-400">
                  {tableResult.schema}
                </Text>
              </View>
            </View>
          </View>
        </View>

        <View className="flex-row items-center gap-2">
          {/* Status Badge */}
          <View
            className={`px-1.5 py-0.5 rounded border ${statusBadge.bg} ${statusBadge.border}`}
          >
            <Text className={`text-[9px] font-mono font-bold ${statusBadge.text}`}>
              {tableResult.status}
            </Text>
          </View>

          {/* Duration */}
          <View className="flex-row items-center gap-1">
            <Clock size={11} color={THEME_COLORS.textMuted} />
            <Text className="text-[11px] font-mono text-slate-400">
              {formatDurationMs(tableResult.duration_ms)}
            </Text>
          </View>

          <ChevronRight size={13} color={THEME_COLORS.textDark} />
        </View>
      </View>

      {/* ── Metrics Row ──────────────────────────────────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2 pt-1 border-t border-slate-800/60">
        <View className="flex-row items-center gap-3 flex-wrap">
          {/* Rows */}
          <View className="flex-row items-center gap-1">
            <Database size={11} color={THEME_COLORS.textMuted} />
            <Text className="text-[11px] font-mono text-slate-300">
              {formatNumber(tableResult.estimated_rows)}
            </Text>
            <Text className="text-[9px] text-slate-500">rows</Text>
          </View>

          {/* Sample Size */}
          <Text className="text-[11px] font-mono text-slate-400">
            Sample: {formatNumber(tableResult.returned_rows || tableResult.sample_size)}
          </Text>

          {/* Profiled Columns */}
          <View className="flex-row items-center gap-1">
            <Columns size={11} color={THEME_COLORS.accentIcon} />
            <Text className="text-[11px] font-mono text-purple-300">
              {tableResult.profiled_columns} / {tableResult.column_count}
            </Text>
            <Text className="text-[9px] text-slate-500">profiled</Text>
          </View>
        </View>

        {/* Skip Reason or Error Note */}
        {tableResult.skip_reason && (
          <Text className="text-[10px] font-mono text-slate-500 italic">
            skip: {tableResult.skip_reason}
          </Text>
        )}

        {isFailed && tableResult.error_message && (
          <View className="flex-row items-center gap-1">
            <ShieldAlert size={11} color={THEME_COLORS.dangerIcon} />
            <Text className="text-[10px] font-mono text-rose-400" numberOfLines={1}>
              {tableResult.error_message}
            </Text>
          </View>
        )}
      </View>
    </Pressable>
  );
};
