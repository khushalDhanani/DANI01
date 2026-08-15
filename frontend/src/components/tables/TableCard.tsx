import React from "react";
import { Pressable, Text, View } from "react-native";
import { ArrowRight, Table } from "lucide-react-native";
import type { TableInfo } from "@/types/database.types";
import { formatNumber } from "@/utils/formatters";
import { THEME_COLORS } from "@/constants/theme";

interface TableCardProps {
  table: TableInfo;
  onPress?: () => void;
}

export const TableCard: React.FC<TableCardProps> = ({ table, onPress }) => {
  return (
    <Pressable
      onPress={onPress}
      className="p-3 bg-dark-card border border-dark-border rounded-xl active:bg-slate-900/60 flex-row items-center justify-between gap-3 transition-colors"
    >
      <View className="flex-row items-center gap-2.5 flex-1 min-w-[200px]">
        <View className="p-2 rounded-lg bg-slate-900 border border-slate-800">
          <Table size={16} color={THEME_COLORS.primaryIcon} />
        </View>
        <View>
          <Text className="text-xs font-bold text-white font-mono">
            {table.schema}.{table.table}
          </Text>
          <Text className="text-[10px] text-slate-400 mt-0.5">
            {table.table_type || "BASE TABLE"}
          </Text>
        </View>
      </View>

      <View className="flex-row items-center gap-4">
        <View className="items-end">
          <Text className="text-xs font-bold text-slate-200 font-mono">
            {formatNumber(table.estimated_rows)}
          </Text>
          <Text className="text-[10px] text-slate-500">Est. Rows</Text>
        </View>

        <View className="items-end">
          <Text className="text-xs font-bold text-slate-200 font-mono">
            {table.column_count}
          </Text>
          <Text className="text-[10px] text-slate-500">Columns</Text>
        </View>

        <ArrowRight size={14} color={THEME_COLORS.textDark} />
      </View>
    </Pressable>
  );
};
