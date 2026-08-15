import React from "react";
import { Text, View } from "react-native";
import type { SchemaInfo } from "@/types/database.types";
import { formatNumber } from "@/utils/formatters";

interface SchemaDistributionCardProps {
  schema: SchemaInfo;
  totalTables?: number;
}

export const SchemaDistributionCard: React.FC<SchemaDistributionCardProps> = ({
  schema,
  totalTables,
}) => {
  const percent =
    totalTables && totalTables > 0
      ? ((schema.table_count / totalTables) * 100).toFixed(1)
      : null;

  return (
    <View className="bg-dark-card border border-dark-border rounded-xl p-2.5 px-3 flex-row items-center justify-between">
      <View className="flex-row items-center gap-2.5">
        <View className="w-7 h-7 rounded-lg bg-blue-950/80 border border-blue-600/30 items-center justify-center">
          <Text className="text-[10px] font-mono font-bold text-blue-400">
            {schema.name.slice(0, 2).toUpperCase()}
          </Text>
        </View>
        <View>
          <Text className="text-xs font-bold text-white font-mono">
            {schema.name}
          </Text>
          {percent && (
            <Text className="text-[10px] text-slate-400 mt-0.5">
              {percent}% of catalog
            </Text>
          )}
        </View>
      </View>
      <View className="bg-slate-900/90 px-2.5 py-1 rounded-md border border-slate-800 flex-row items-center gap-1.5">
        <Text className="text-xs font-bold text-blue-400">
          {formatNumber(schema.table_count)}
        </Text>
        <Text className="text-[10px] text-slate-400 font-medium">tables</Text>
      </View>
    </View>
  );
};
