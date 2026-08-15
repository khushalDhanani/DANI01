import React from "react";
import { Text, View } from "react-native";

interface ProgressMetricProps {
  label: string;
  percent: number;
  sublabel?: string;
  colorScheme?: "emerald" | "blue" | "purple" | "amber" | "rose" | "cyan";
  compact?: boolean;
}

export const ProgressMetric: React.FC<ProgressMetricProps> = ({
  label,
  percent,
  sublabel,
  colorScheme = "blue",
  compact = false,
}) => {
  const getTheme = () => {
    switch (colorScheme) {
      case "emerald":
        return { bar: "bg-emerald-400", text: "text-emerald-400" };
      case "purple":
        return { bar: "bg-purple-400", text: "text-purple-400" };
      case "amber":
        return { bar: "bg-amber-400", text: "text-amber-400" };
      case "rose":
        return { bar: "bg-rose-400", text: "text-rose-400" };
      case "cyan":
        return { bar: "bg-cyan-400", text: "text-cyan-400" };
      case "blue":
      default:
        return { bar: "bg-blue-400", text: "text-blue-400" };
    }
  };

  const theme = getTheme();
  const clamped = Math.min(100, Math.max(0, percent));

  return (
    <View className="gap-1.5 w-full">
      <View className="flex-row items-center justify-between">
        <Text className="text-[10px] uppercase font-bold text-slate-400">
          {label}
        </Text>
        <Text className={`text-xs font-mono font-bold ${theme.text}`}>
          {clamped.toFixed(1)}%
        </Text>
      </View>

      {/* Progress Track */}
      <View className={`w-full ${compact ? "h-1.5" : "h-2"} bg-slate-800 rounded-full overflow-hidden`}>
        <View
          style={{ width: `${clamped}%` }}
          className={`h-full rounded-full ${theme.bar}`}
        />
      </View>

      {sublabel && (
        <Text className="text-[9px] font-mono text-slate-500">{sublabel}</Text>
      )}
    </View>
  );
};
