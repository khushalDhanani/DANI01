import React from "react";
import { Text, View } from "react-native";

interface StatComparisonProps {
  min: number;
  max: number;
  mean?: number | null;
  median?: number | null;
}

export const StatComparison: React.FC<StatComparisonProps> = ({
  min,
  max,
  mean,
  median,
}) => {
  const range = max - min;
  const getPercent = (val: number) => {
    if (range <= 0) return 50;
    return Math.min(100, Math.max(0, ((val - min) / range) * 100));
  };

  const meanPct = mean !== null && mean !== undefined ? getPercent(mean) : null;
  const medianPct = median !== null && median !== undefined ? getPercent(median) : null;

  return (
    <View className="gap-2 w-full bg-slate-900/60 border border-slate-800/60 rounded-lg p-3">
      <View className="flex-row items-center justify-between">
        <Text className="text-[10px] uppercase font-bold text-blue-400">
          Numeric Value Range & Distribution
        </Text>
        <Text className="text-[9px] font-mono text-slate-500">
          Δ {range.toLocaleString()}
        </Text>
      </View>

      {/* ── Visual Continuous Track with Markers ─────────── */}
      <View className="py-2">
        <View className="h-2 bg-slate-800 rounded-full relative justify-center">
          {/* Inner Active Range Gradient */}
          <View className="absolute inset-0 bg-blue-600/30 rounded-full" />

          {/* Median Pin */}
          {medianPct !== null && (
            <View
              style={{ left: `${medianPct}%` }}
              className="absolute -top-1 w-1.5 h-4 bg-amber-400 rounded-full shadow-sm"
            />
          )}

          {/* Mean Pin */}
          {meanPct !== null && (
            <View
              style={{ left: `${meanPct}%` }}
              className="absolute -top-1 w-1.5 h-4 bg-emerald-400 rounded-full shadow-sm"
            />
          )}
        </View>
      </View>

      {/* ── Numeric Values Scale ─────────────────────────── */}
      <View className="flex-row items-center justify-between pt-1">
        <View>
          <Text className="text-[8px] uppercase font-bold text-slate-500">Min</Text>
          <Text className="text-xs font-mono font-bold text-slate-200">
            {min.toLocaleString()}
          </Text>
        </View>

        {median !== null && median !== undefined && (
          <View className="items-center">
            <View className="flex-row items-center gap-1">
              <View className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              <Text className="text-[8px] uppercase font-bold text-amber-400">Median</Text>
            </View>
            <Text className="text-xs font-mono font-bold text-slate-200">
              {median.toLocaleString()}
            </Text>
          </View>
        )}

        {mean !== null && mean !== undefined && (
          <View className="items-center">
            <View className="flex-row items-center gap-1">
              <View className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <Text className="text-[8px] uppercase font-bold text-emerald-400">Mean</Text>
            </View>
            <Text className="text-xs font-mono font-bold text-slate-200">
              {mean.toFixed(2)}
            </Text>
          </View>
        )}

        <View className="items-end">
          <Text className="text-[8px] uppercase font-bold text-slate-500">Max</Text>
          <Text className="text-xs font-mono font-bold text-slate-200">
            {max.toLocaleString()}
          </Text>
        </View>
      </View>
    </View>
  );
};
