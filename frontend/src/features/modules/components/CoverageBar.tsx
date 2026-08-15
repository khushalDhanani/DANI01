import React from "react";
import { Text, View } from "react-native";

interface CoverageBarProps {
  label: string;
  percent?: number | null;
  count?: number | null;
  total?: number | null;
  subtitle?: string;
  colorScheme?: "blue" | "emerald" | "amber" | "purple" | "indigo" | "rose" | "auto";
}

function getStyleClasses(
  colorScheme: string,
  validPct: number,
  isAvailable: boolean
): { fillClass: string; textPctClass: string } {
  if (colorScheme === "auto") {
    if (!isAvailable) {
      return { fillClass: "bg-slate-700", textPctClass: "text-slate-500" };
    }
    if (validPct >= 80) {
      return { fillClass: "bg-emerald-500", textPctClass: "text-emerald-400" };
    }
    if (validPct >= 50) {
      return { fillClass: "bg-blue-500", textPctClass: "text-blue-400" };
    }
    if (validPct >= 20) {
      return { fillClass: "bg-amber-500", textPctClass: "text-amber-400" };
    }
    return { fillClass: "bg-rose-500", textPctClass: "text-rose-400" };
  }

  switch (colorScheme) {
    case "emerald":
      return { fillClass: "bg-emerald-500", textPctClass: "text-emerald-400" };
    case "amber":
      return { fillClass: "bg-amber-500", textPctClass: "text-amber-400" };
    case "purple":
      return { fillClass: "bg-purple-500", textPctClass: "text-purple-400" };
    case "indigo":
      return { fillClass: "bg-indigo-500", textPctClass: "text-indigo-400" };
    case "rose":
      return { fillClass: "bg-rose-500", textPctClass: "text-rose-400" };
    default:
      return { fillClass: "bg-blue-500", textPctClass: "text-blue-400" };
  }
}

export const CoverageBar: React.FC<CoverageBarProps> = ({
  label,
  percent,
  count,
  total,
  subtitle,
  colorScheme = "auto",
}) => {
  const isAvailable = percent !== undefined && percent !== null;
  const validPct = isAvailable ? Math.min(100, Math.max(0, percent)) : 0;
  const { fillClass, textPctClass } = getStyleClasses(colorScheme, validPct, isAvailable);

  const hasCount = count !== undefined && count !== null;
  const hasTotal = total !== undefined && total !== null;

  return (
    <View className="py-1">
      {/* Header with Title and Percentage */}
      <View className="flex-row items-center justify-between mb-1">
        <Text className="text-[11px] font-semibold text-slate-300" numberOfLines={1}>
          {label}
        </Text>
        <Text className={`text-[11px] font-bold font-mono ${textPctClass}`}>
          {isAvailable ? `${validPct.toFixed(2)}%` : "N/A"}
        </Text>
      </View>

      {/* Progress Track */}
      <View className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
        {isAvailable && (
          <View
            className={`h-full rounded-full ${fillClass}`}
            style={{ width: `${validPct}%` }}
          />
        )}
      </View>

      {/* Footer Details: count / total and optional subtitle */}
      {(hasCount || subtitle) && (
        <View className="flex-row items-center justify-between mt-1">
          {hasCount && hasTotal ? (
            <Text className="text-[10px] text-slate-400 font-mono">
              {count.toLocaleString()} / {total.toLocaleString()}
            </Text>
          ) : hasCount ? (
            <Text className="text-[10px] text-slate-400 font-mono">
              {count.toLocaleString()}
            </Text>
          ) : (
            <View />
          )}

          {subtitle && (
            <Text className="text-[10px] text-slate-500" numberOfLines={1}>
              {subtitle}
            </Text>
          )}
        </View>
      )}
    </View>
  );
};
