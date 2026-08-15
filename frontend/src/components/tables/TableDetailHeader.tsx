import React from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import { ArrowLeft, Columns, Database, ShieldCheck, Table } from "lucide-react-native";
import { formatNumber } from "@/utils/formatters";
import { THEME_COLORS } from "@/constants/theme";

interface TableDetailHeaderProps {
  schema: string;
  table: string;
  estimatedRows?: number;
  columnCount?: number;
}

export const TableDetailHeader: React.FC<TableDetailHeaderProps> = ({
  schema,
  table,
  estimatedRows,
  columnCount,
}) => {
  const router = useRouter();
  const isDbo = schema.toLowerCase() === "dbo";

  return (
    <View className="gap-3">
      {/* ── Breadcrumb Bar ───────────────────────────────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2">
        <View className="flex-row items-center gap-1.5">
          <Pressable
            onPress={() => router.push("/database" as Href)}
            accessibilityRole="button"
            accessibilityLabel="Back to Tables Explorer"
            className="flex-row items-center gap-1.5 p-1 rounded-md active:bg-slate-800"
          >
            <ArrowLeft size={13} color={THEME_COLORS.textMuted} />
            <Text className="text-xs font-semibold text-slate-400">
              Tables Explorer
            </Text>
          </Pressable>
          <Text className="text-slate-600">/</Text>
          <View
            className={`px-1.5 py-0.5 rounded border ${
              isDbo
                ? "bg-blue-950/70 border-blue-600/30"
                : "bg-purple-950/70 border-purple-600/30"
            }`}
          >
            <Text
              className={`text-[10px] font-mono font-bold ${
                isDbo ? "text-blue-400" : "text-purple-400"
              }`}
            >
              {schema}
            </Text>
          </View>
          <Text className="text-slate-600">/</Text>
          <Text className="text-xs font-mono font-bold text-white">
            {table}
          </Text>
        </View>

        {/* Read-Only Status Indicator */}
        <View className="flex-row items-center gap-1.5 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-md">
          <ShieldCheck size={12} color={THEME_COLORS.primaryIcon} />
          <Text className="text-[10px] font-semibold text-slate-400">
            MSSQL Read-Only
          </Text>
        </View>
      </View>

      {/* ── Header Title & Metrics ───────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-3.5 flex-row items-center justify-between flex-wrap gap-3">
        <View className="flex-row items-center gap-3">
          <View className="w-9 h-9 rounded-lg bg-blue-950/80 border border-blue-600/30 items-center justify-center">
            <Table size={18} color={THEME_COLORS.primaryIcon} />
          </View>
          <View>
            <Text className="text-base sm:text-lg font-black text-white font-mono tracking-tight">
              {table}
            </Text>
            <Text className="text-[10px] text-slate-500">
              Schema namespace: <Text className="font-mono text-slate-400">{schema}</Text>
            </Text>
          </View>
        </View>

        <View className="flex-row items-center gap-4">
          {estimatedRows !== undefined && (
            <View className="flex-row items-center gap-1.5 bg-slate-900 px-2.5 py-1.5 rounded-lg border border-slate-800">
              <Database size={13} color={THEME_COLORS.successIcon} />
              <Text className="text-xs font-mono font-bold text-emerald-400">
                {formatNumber(estimatedRows)}
              </Text>
              <Text className="text-[10px] text-slate-500">rows</Text>
            </View>
          )}

          {columnCount !== undefined && (
            <View className="flex-row items-center gap-1.5 bg-slate-900 px-2.5 py-1.5 rounded-lg border border-slate-800">
              <Columns size={13} color={THEME_COLORS.accentIcon} />
              <Text className="text-xs font-mono font-bold text-purple-400">
                {columnCount}
              </Text>
              <Text className="text-[10px] text-slate-500">cols</Text>
            </View>
          )}
        </View>
      </View>
    </View>
  );
};
