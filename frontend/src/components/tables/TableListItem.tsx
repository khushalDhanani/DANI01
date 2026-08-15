import React from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import { ChevronRight, Columns, Database, Table } from "lucide-react-native";
import type { TableInfo } from "@/types/database.types";
import { formatNumber } from "@/utils/formatters";
import { THEME_COLORS } from "@/constants/theme";

interface TableListItemProps {
  table: TableInfo;
}

export const TableListItem: React.FC<TableListItemProps> = ({ table }) => {
  const router = useRouter();

  const handlePress = () => {
    // Safely encode schema and table for routing
    const safeSchema = encodeURIComponent(table.schema);
    const safeTable = encodeURIComponent(table.table);
    router.push(`/database/${safeSchema}/${safeTable}` as Href);
  };

  const isDbo = table.schema.toLowerCase() === "dbo";

  return (
    <Pressable
      onPress={handlePress}
      accessibilityRole="button"
      accessibilityLabel={`Inspect table ${table.schema}.${table.table}`}
      className="bg-dark-card border border-dark-border rounded-xl p-3 hover:border-slate-700 active:bg-slate-900/80 flex-row items-center justify-between gap-3 transition-colors"
    >
      {/* Left: Icon + Table & Schema info */}
      <View className="flex-row items-center gap-2.5 flex-1 min-w-[200px]">
        <View className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 items-center justify-center">
          <Table size={15} color={THEME_COLORS.primaryIcon} />
        </View>

        <View className="flex-1">
          <View className="flex-row items-center gap-1.5 flex-wrap">
            <Text className="text-xs font-bold text-white font-mono" numberOfLines={1}>
              {table.table}
            </Text>
            <View
              className={`px-1.5 py-0.2 rounded border ${
                isDbo
                  ? "bg-blue-950/70 border-blue-600/30"
                  : "bg-purple-950/70 border-purple-600/30"
              }`}
            >
              <Text
                className={`text-[9px] font-mono font-bold ${
                  isDbo ? "text-blue-400" : "text-purple-400"
                }`}
              >
                {table.schema}
              </Text>
            </View>
          </View>

          <Text className="text-[10px] text-slate-500 mt-0.5">
            SQL Server Catalog Object
          </Text>
        </View>
      </View>

      {/* Right: Metrics + Chevron */}
      <View className="flex-row items-center gap-4">
        {/* Estimated Rows Metric */}
        <View className="flex-row items-center gap-1">
          <Database size={12} color={THEME_COLORS.textMuted} />
          <Text className="text-xs font-semibold text-slate-300 font-mono">
            {formatNumber(table.estimated_rows)}
          </Text>
          <Text className="text-[10px] text-slate-500">rows</Text>
        </View>

        {/* Columns Metric */}
        <View className="hidden sm:flex flex-row items-center gap-1">
          <Columns size={12} color={THEME_COLORS.textMuted} />
          <Text className="text-xs font-semibold text-slate-300 font-mono">
            {table.column_count}
          </Text>
          <Text className="text-[10px] text-slate-500">cols</Text>
        </View>

        <ChevronRight size={14} color={THEME_COLORS.textDark} />
      </View>
    </Pressable>
  );
};
