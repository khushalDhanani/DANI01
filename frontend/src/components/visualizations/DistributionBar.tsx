import React from "react";
import { Text, View } from "react-native";

export interface DistributionSegment {
  label: string;
  count: number;
  percent: number;
  color: string; // e.g. "bg-emerald-400"
  textColor?: string; // e.g. "text-emerald-400"
}

interface DistributionBarProps {
  segments: DistributionSegment[];
  totalLabel?: string;
  totalCount?: number;
  showLegend?: boolean;
}

export const DistributionBar: React.FC<DistributionBarProps> = ({
  segments,
  totalLabel,
  totalCount,
  showLegend = true,
}) => {
  // Filter out 0% segments from the bar fill, but keep them in legend if count > 0
  const activeSegments = segments.filter((s) => s.percent > 0);

  return (
    <View className="gap-2 w-full">
      {/* ── Segmented Progress Bar ────────────────────────── */}
      <View className="h-2.5 w-full bg-slate-800 rounded-full overflow-hidden flex-row">
        {activeSegments.map((seg, idx) => (
          <View
            key={idx}
            style={{ width: `${Math.min(100, Math.max(0.5, seg.percent))}%` }}
            className={`h-full ${seg.color}`}
          />
        ))}
      </View>

      {/* ── Legend Breakdown ─────────────────────────────── */}
      {showLegend && (
        <View className="flex-row items-center justify-between flex-wrap gap-2 pt-0.5">
          <View className="flex-row items-center gap-3 flex-wrap">
            {segments.map((seg, idx) => (
              <View key={idx} className="flex-row items-center gap-1.5">
                <View className={`w-2 h-2 rounded-full ${seg.color}`} />
                <Text className="text-[10px] text-slate-400 font-medium">
                  {seg.label}:{" "}
                  <Text className={`font-mono font-bold ${seg.textColor || "text-white"}`}>
                    {seg.percent.toFixed(1)}%
                  </Text>
                  {seg.count !== undefined && (
                    <Text className="text-slate-500 font-normal"> ({seg.count})</Text>
                  )}
                </Text>
              </View>
            ))}
          </View>

          {totalCount !== undefined && totalLabel && (
            <Text className="text-[10px] font-mono text-slate-500">
              {totalLabel}: <Text className="text-slate-300 font-bold">{totalCount}</Text>
            </Text>
          )}
        </View>
      )}
    </View>
  );
};
