import React from "react";
import { Pressable, Text, View } from "react-native";
import {
  ArrowRight,
  Columns,
  Database,
  Key,
  Layers,
  Network,
  ShieldAlert,
} from "lucide-react-native";
import type {
  ColumnInfo,
  IndexInfo,
  TableKeysResponse,
} from "@/types/database.types";
import { MetricCard } from "@/components/ui/MetricCard";
import { THEME_COLORS } from "@/constants/theme";

interface TableOverviewTabProps {
  schema: string;
  table: string;
  estimatedRows: number;
  columnCount: number;
  columns?: ColumnInfo[];
  keys?: TableKeysResponse;
  indexes?: IndexInfo[];
  onSelectTab: (tab: "columns" | "relationships" | "indexes") => void;
}

export const TableOverviewTab: React.FC<TableOverviewTabProps> = ({
  schema,
  table,
  estimatedRows,
  columnCount,
  columns,
  keys,
  indexes,
  onSelectTab,
}) => {
  const pkName = keys?.primary_key?.name;
  const pkColumns = keys?.primary_key?.columns.map((c) => c.name).join(", ");
  const fkCount = keys?.foreign_keys.length ?? 0;
  const indexCount = indexes?.length ?? 0;

  return (
    <View className="gap-4">
      {/* ── Summary Metric Cards Grid ──────────────────────── */}
      <View className="flex-row flex-wrap gap-3">
        <MetricCard
          label="Estimated Rows"
          value={estimatedRows}
          sublabel="sys.partitions partition count"
          icon={<Database size={15} color={THEME_COLORS.successIcon} />}
          accentBorder="border-emerald-500/30"
        />
        <MetricCard
          label="Total Columns"
          value={columnCount}
          sublabel="Discovered SQL attributes"
          icon={<Columns size={15} color={THEME_COLORS.accentIcon} />}
          accentBorder="border-purple-500/30"
        />
        <MetricCard
          label="Foreign Keys"
          value={fkCount}
          sublabel="Outgoing foreign references"
          icon={<Network size={15} color={THEME_COLORS.primaryIcon} />}
          accentBorder="border-blue-500/30"
        />
        <MetricCard
          label="Indexes"
          value={indexCount}
          sublabel="Clustered & Nonclustered"
          icon={<Layers size={15} color={THEME_COLORS.warningIcon} />}
          accentBorder="border-amber-500/30"
        />
      </View>

      {/* ── Structural Specifications Card ─────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3.5">
        <Text className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Table Specifications & Integrity
        </Text>

        <View className="divide-y divide-dark-border">
          {/* Fully Qualified Name */}
          <View className="py-2 flex-row items-center justify-between">
            <Text className="text-xs text-slate-400">Fully Qualified Name</Text>
            <Text className="text-xs font-mono font-bold text-white">
              [{schema}].[{table}]
            </Text>
          </View>

          {/* Primary Key Status */}
          <View className="py-2 flex-row items-center justify-between">
            <Text className="text-xs text-slate-400">Primary Key</Text>
            {pkName ? (
              <View className="flex-row items-center gap-1.5">
                <Key size={12} color={THEME_COLORS.warningIcon} />
                <Text className="text-xs font-mono font-bold text-amber-400">
                  {pkName} ({pkColumns})
                </Text>
              </View>
            ) : (
              <View className="flex-row items-center gap-1">
                <ShieldAlert size={12} color={THEME_COLORS.textMuted} />
                <Text className="text-xs text-slate-500">No primary key defined (Heap)</Text>
              </View>
            )}
          </View>

          {/* Identity Columns */}
          <View className="py-2 flex-row items-center justify-between">
            <Text className="text-xs text-slate-400">Identity Columns</Text>
            {columns ? (
              <Text className="text-xs font-mono text-slate-300">
                {columns.filter((c) => c.identity).map((c) => c.name).join(", ") || "None"}
              </Text>
            ) : (
              <Text className="text-xs text-slate-500 font-mono">—</Text>
            )}
          </View>

          {/* Nullable Ratio */}
          <View className="py-2 flex-row items-center justify-between">
            <Text className="text-xs text-slate-400">Nullability Ratio</Text>
            {columns ? (
              <Text className="text-xs font-mono text-slate-300">
                {columns.filter((c) => c.nullable).length} Nullable / {columns.filter((c) => !c.nullable).length} NOT NULL
              </Text>
            ) : (
              <Text className="text-xs text-slate-500 font-mono">—</Text>
            )}
          </View>
        </View>
      </View>

      {/* ── Quick Navigation Section Jumps ─────────────────── */}
      <View className="flex-row flex-wrap gap-2.5">
        <Pressable
          onPress={() => onSelectTab("columns")}
          className="flex-1 min-w-[140px] bg-dark-card border border-dark-border hover:border-slate-700 active:bg-slate-900/80 rounded-xl p-3 flex-row items-center justify-between"
        >
          <View className="flex-row items-center gap-2">
            <Columns size={15} color={THEME_COLORS.accentIcon} />
            <Text className="text-xs font-semibold text-slate-200">
              Inspect Columns
            </Text>
          </View>
          <ArrowRight size={13} color={THEME_COLORS.textDark} />
        </Pressable>

        <Pressable
          onPress={() => onSelectTab("relationships")}
          className="flex-1 min-w-[140px] bg-dark-card border border-dark-border hover:border-slate-700 active:bg-slate-900/80 rounded-xl p-3 flex-row items-center justify-between"
        >
          <View className="flex-row items-center gap-2">
            <Network size={15} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-semibold text-slate-200">
              Foreign Keys ({fkCount})
            </Text>
          </View>
          <ArrowRight size={13} color={THEME_COLORS.textDark} />
        </Pressable>

        <Pressable
          onPress={() => onSelectTab("indexes")}
          className="flex-1 min-w-[140px] bg-dark-card border border-dark-border hover:border-slate-700 active:bg-slate-900/80 rounded-xl p-3 flex-row items-center justify-between"
        >
          <View className="flex-row items-center gap-2">
            <Layers size={15} color={THEME_COLORS.warningIcon} />
            <Text className="text-xs font-semibold text-slate-200">
              Indexes ({indexCount})
            </Text>
          </View>
          <ArrowRight size={13} color={THEME_COLORS.textDark} />
        </Pressable>
      </View>
    </View>
  );
};
