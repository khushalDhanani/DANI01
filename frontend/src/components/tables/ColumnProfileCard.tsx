import React from "react";
import { Text, View } from "react-native";
import { Lock } from "lucide-react-native";
import type { ColumnProfile } from "@/types/profiling.types";
import { ProgressMetric } from "@/components/visualizations/ProgressMetric";
import { StatComparison } from "@/components/visualizations/StatComparison";
import { TopValuesChart } from "@/components/visualizations/TopValuesChart";
import { DistributionBar, type DistributionSegment } from "@/components/visualizations/DistributionBar";
import { formatNumber } from "@/utils/formatters";
import { THEME_COLORS } from "@/constants/theme";

interface ColumnProfileCardProps {
  profile: ColumnProfile;
  isMasked?: boolean;
}

export const ColumnProfileCard: React.FC<ColumnProfileCardProps> = ({
  profile,
  isMasked = false,
}) => {
  const colName = profile.name || profile.column_name || "Unknown";
  const pType = profile.profile_type?.toLowerCase() || "unknown";

  const getProfileTypeBadge = () => {
    switch (pType) {
      case "numeric":
        return { bg: "bg-blue-950/80", border: "border-blue-600/40", text: "text-blue-400" };
      case "text":
        return { bg: "bg-purple-950/80", border: "border-purple-600/40", text: "text-purple-400" };
      case "datetime":
        return { bg: "bg-cyan-950/80", border: "border-cyan-600/40", text: "text-cyan-400" };
      case "boolean":
        return { bg: "bg-emerald-950/80", border: "border-emerald-600/40", text: "text-emerald-400" };
      default:
        return { bg: "bg-slate-900", border: "border-slate-800", text: "text-slate-400" };
    }
  };

  const typeBadge = getProfileTypeBadge();

  // Text Quality Distribution
  const nullPct = profile.null_percent || 0;
  const emptyPct = profile.empty_percent || 0;
  const blankPct = profile.blank_percent || 0;
  const populatedPct = Math.max(0, 100 - (nullPct + emptyPct + blankPct));

  const textSegments: DistributionSegment[] = [
    { label: "Valid", count: 0, percent: populatedPct, color: "bg-emerald-400", textColor: "text-emerald-400" },
    { label: "Null", count: profile.null_count, percent: nullPct, color: "bg-amber-400", textColor: "text-amber-400" },
    { label: "Empty", count: profile.empty_count || 0, percent: emptyPct, color: "bg-purple-400", textColor: "text-purple-400" },
    { label: "Blank", count: profile.blank_count || 0, percent: blankPct, color: "bg-slate-500", textColor: "text-slate-400" },
  ].filter((s) => s.percent > 0 || s.label === "Valid" || s.label === "Null");

  // Boolean Distribution Segments
  const booleanSegments: DistributionSegment[] = [
    { label: "True", count: profile.true_count || 0, percent: profile.true_percent || 0, color: "bg-emerald-400", textColor: "text-emerald-400" },
    { label: "False", count: profile.false_count || 0, percent: profile.false_percent || 0, color: "bg-rose-400", textColor: "text-rose-400" },
  ];

  return (
    <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3.5">
      {/* ── Column Header ───────────────────────────────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2">
        <View className="flex-row items-center gap-2 flex-wrap">
          <Text className="text-xs font-mono font-bold text-white">
            {colName}
          </Text>
          <Text className="text-[10px] font-mono text-slate-500">
            {profile.data_type}
          </Text>
        </View>

        <View className="flex-row items-center gap-1.5">
          <View
            className={`px-1.5 py-0.5 rounded border ${typeBadge.bg} ${typeBadge.border}`}
          >
            <Text className={`text-[9px] font-mono font-bold uppercase ${typeBadge.text}`}>
              {pType}
            </Text>
          </View>
          {isMasked && (
            <View className="flex-row items-center gap-0.5 bg-rose-950/80 border border-rose-600/40 px-1.5 py-0.5 rounded">
              <Lock size={9} color={THEME_COLORS.dangerIcon} />
              <Text className="text-[8px] font-mono text-rose-400 font-bold">
                MASKED
              </Text>
            </View>
          )}
        </View>
      </View>

      {/* ── Common Stats Visual Meters ───────────────────── */}
      <View className="flex-row flex-wrap gap-3">
        <View className="flex-1 min-w-[140px] bg-slate-900/80 border border-slate-800/80 rounded-lg p-2.5">
          <ProgressMetric
            label="Null Ratio"
            percent={profile.null_percent || 0}
            sublabel={`${formatNumber(profile.null_count)} null rows`}
            colorScheme={profile.null_percent > 20 ? "amber" : "emerald"}
          />
        </View>

        <View className="flex-1 min-w-[140px] bg-slate-900/80 border border-slate-800/80 rounded-lg p-2.5">
          <ProgressMetric
            label="Distinct Ratio"
            percent={profile.distinct_percent || 0}
            sublabel={`${formatNumber(profile.distinct_count)} unique values`}
            colorScheme="purple"
          />
        </View>
      </View>

      {/* ── 1. Numeric Visualizations ────────────────────── */}
      {pType === "numeric" && profile.min !== null && profile.min !== undefined && profile.max !== null && profile.max !== undefined && (
        <StatComparison
          min={profile.min}
          max={profile.max}
          mean={profile.mean}
          median={profile.median}
        />
      )}

      {/* ── 2. Text Visualizations ───────────────────────── */}
      {pType === "text" && (
        <View className="bg-slate-900/60 border border-slate-800/60 rounded-lg p-3 gap-2.5">
          <Text className="text-[10px] uppercase font-bold text-purple-400">
            Text String Metrics & Quality Distribution
          </Text>

          <DistributionBar segments={textSegments} showLegend={true} />

          <View className="flex-row items-center justify-between flex-wrap gap-2 pt-1 border-t border-slate-800/60">
            <Text className="text-[10px] font-mono text-slate-400">
              Length: <Text className="font-bold text-slate-200">{profile.min_length ?? 0} – {profile.max_length ?? 0}</Text> chars
            </Text>
            <Text className="text-[10px] font-mono text-slate-400">
              Avg: <Text className="font-bold text-slate-200">{profile.avg_length?.toFixed(1) ?? 0}</Text> chars
            </Text>
          </View>
        </View>
      )}

      {/* ── 3. Datetime Range Visualizations ─────────────── */}
      {pType === "datetime" && (
        <View className="bg-slate-900/60 border border-slate-800/60 rounded-lg p-3 gap-2">
          <Text className="text-[10px] uppercase font-bold text-cyan-400">
            Temporal Span
          </Text>
          <View className="flex-row items-center justify-between flex-wrap gap-2">
            <View>
              <Text className="text-[9px] text-slate-500">Earliest</Text>
              <Text className="text-xs font-mono font-bold text-slate-200">
                {profile.earliest || "—"}
              </Text>
            </View>
            <View className="items-end">
              <Text className="text-[9px] text-slate-500">Latest</Text>
              <Text className="text-xs font-mono font-bold text-slate-200">
                {profile.latest || "—"}
              </Text>
            </View>
          </View>
        </View>
      )}

      {/* ── 4. Boolean Visualizations ────────────────────── */}
      {pType === "boolean" && (
        <View className="bg-slate-900/60 border border-slate-800/60 rounded-lg p-3 gap-2">
          <Text className="text-[10px] uppercase font-bold text-emerald-400">
            Boolean True / False Proportions
          </Text>
          <DistributionBar segments={booleanSegments} showLegend={true} />
        </View>
      )}

      {/* ── 5. Top Values Frequency Chart ────────────────── */}
      {profile.top_values && profile.top_values.length > 0 && (
        <TopValuesChart
          topValues={profile.top_values}
          isMasked={isMasked}
        />
      )}
    </View>
  );
};
