import React from "react";
import { Text, View } from "react-native";
import { formatCompactNumber, formatNumber } from "@/utils/formatters";

interface MetricCardProps {
  label: string;
  /** Raw numeric value — formatted for display internally */
  value: number | string;
  sublabel?: string;
  icon?: React.ReactNode;
  accentBorder?: string;
  /** If true, uses compact format (124.9M). Default: false */
  compact?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  sublabel,
  icon,
  accentBorder = "border-dark-border",
  compact = false,
}) => {
  const displayValue =
    typeof value === "number"
      ? compact
        ? formatCompactNumber(value)
        : formatNumber(value)
      : value;

  return (
    <View
      className={`bg-dark-card border ${accentBorder} rounded-xl p-3.5 flex-1 min-w-[140px]`}
    >
      <View className="flex-row items-center justify-between mb-2">
        <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
          {label}
        </Text>
        {icon && (
          <View className="p-1.5 rounded-lg bg-slate-800/80">{icon}</View>
        )}
      </View>
      <Text className="text-2xl font-bold text-white tracking-tight leading-none">
        {displayValue}
      </Text>
      {sublabel && (
        <Text className="text-[10px] text-slate-400 mt-1 font-medium" numberOfLines={1}>
          {sublabel}
        </Text>
      )}
    </View>
  );
};
