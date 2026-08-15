import React from "react";
import { Text, View } from "react-native";
import { Lock } from "lucide-react-native";
import type { ValueFrequency } from "@/types/profiling.types";
import { THEME_COLORS } from "@/constants/theme";

interface TopValuesChartProps {
  topValues: ValueFrequency[];
  isMasked?: boolean;
}

export const TopValuesChart: React.FC<TopValuesChartProps> = ({
  topValues,
  isMasked = false,
}) => {
  if (isMasked) {
    return (
      <View className="bg-slate-900/60 border border-slate-800/60 rounded-lg p-3 gap-1.5">
        <Text className="text-[10px] uppercase font-bold text-slate-500">
          Value Distribution
        </Text>
        <View className="flex-row items-center gap-1.5 py-1">
          <Lock size={12} color={THEME_COLORS.dangerIcon} />
          <Text className="text-xs font-mono text-slate-500">
            Top values suppressed for privacy (PII classified column)
          </Text>
        </View>
      </View>
    );
  }

  const items = topValues.slice(0, 5);
  const maxPercent = Math.max(...items.map((i) => i.percent || 0), 1);

  return (
    <View className="bg-slate-900/60 border border-slate-800/60 rounded-lg p-3 gap-2">
      <Text className="text-[10px] uppercase font-bold text-purple-400">
        Top Value Frequency Distribution
      </Text>

      <View className="gap-2">
        {items.map((item, idx) => {
          const fillWidth = Math.min(100, Math.max(2, (item.percent / maxPercent) * 100));
          const label = item.value === null ? "NULL" : String(item.value);

          return (
            <View key={idx} className="gap-1">
              <View className="flex-row items-center justify-between">
                <Text
                  className={`text-xs font-mono font-medium max-w-[220px] ${
                    item.value === null ? "italic text-amber-400" : "text-slate-200"
                  }`}
                  numberOfLines={1}
                >
                  {label}
                </Text>
                <Text className="text-[10px] font-mono text-slate-400">
                  {item.count} ({item.percent.toFixed(1)}%)
                </Text>
              </View>

              {/* Bar Fill */}
              <View className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <View
                  style={{ width: `${fillWidth}%` }}
                  className="h-full bg-purple-500 rounded-full"
                />
              </View>
            </View>
          );
        })}
      </View>
    </View>
  );
};
