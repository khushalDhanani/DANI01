import React from "react";
import { Text, View } from "react-native";
import type { BaseColumnProfile } from "../../types/profiling.types";

interface ColumnProfileInspectorProps {
  profile: BaseColumnProfile;
}

export const ColumnProfileInspector: React.FC<ColumnProfileInspectorProps> = ({
  profile,
}) => {
  return (
    <View className="py-4 px-2 flex-row items-center justify-between gap-4">
      <View className="flex-1">
        <Text className="text-sm font-bold text-white mb-1">
          {profile.column_name}
        </Text>
        <View className="flex-row items-center gap-2">
          <View className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
            <Text className="text-[10px] font-mono text-slate-300">
              {profile.data_type}
            </Text>
          </View>
          <Text className="text-xs text-slate-400">
            Nulls: {profile.null_percent.toFixed(1)}% • Distinct: {profile.distinct_count}
          </Text>
        </View>
      </View>

      {profile.stats && (
        <View className="items-end hidden sm:flex">
          <Text className="text-xs text-slate-300 font-mono">
            {profile.stats.min !== undefined
              ? `Min: ${profile.stats.min} | Max: ${profile.stats.max}`
              : ""}
          </Text>
        </View>
      )}
    </View>
  );
};
