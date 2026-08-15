import React from "react";
import { Text, View } from "react-native";
import { ArrowDown, ArrowUp, Key, Layers } from "lucide-react-native";
import type { IndexInfo } from "@/types/database.types";
import { EmptyState } from "@/components/ui/EmptyState";
import { THEME_COLORS } from "@/constants/theme";

interface TableIndexesTabProps {
  indexes?: IndexInfo[];
}

export const TableIndexesTab: React.FC<TableIndexesTabProps> = ({ indexes }) => {
  const indexList = indexes ?? [];

  if (indexList.length === 0) {
    return (
      <EmptyState
        title="No indexes found"
        message="This table has no indexes defined."
      />
    );
  }

  return (
    <View className="gap-2.5">
      {indexList.map((idx) => {
        const isPk = idx.primary_key;
        const isClustered = idx.type.toUpperCase() === "CLUSTERED";

        return (
          <View
            key={idx.name}
            className="bg-dark-card border border-dark-border rounded-xl p-3.5 gap-2.5"
          >
            {/* Header: Index Name + Badges */}
            <View className="flex-row items-center justify-between flex-wrap gap-2">
              <View className="flex-row items-center gap-2">
                <View className="p-1 rounded-md bg-amber-950/80 border border-amber-600/40">
                  <Layers size={13} color={THEME_COLORS.warningIcon} />
                </View>
                <Text className="text-xs font-bold text-white font-mono">
                  {idx.name}
                </Text>
              </View>

              <View className="flex-row items-center gap-1.5 flex-wrap">
                {/* Index Type Badge */}
                <View
                  className={`px-1.5 py-0.5 rounded border ${
                    isClustered
                      ? "bg-blue-950/80 border-blue-600/40"
                      : "bg-slate-900 border-slate-800"
                  }`}
                >
                  <Text
                    className={`text-[9px] font-mono font-bold ${
                      isClustered ? "text-blue-400" : "text-slate-400"
                    }`}
                  >
                    {idx.type}
                  </Text>
                </View>

                {/* Unique Badge */}
                {idx.unique && (
                  <View className="bg-emerald-950/80 border border-emerald-600/40 px-1.5 py-0.5 rounded">
                    <Text className="text-[9px] font-mono font-bold text-emerald-400">
                      UNIQUE
                    </Text>
                  </View>
                )}

                {/* PK Badge */}
                {isPk && (
                  <View className="flex-row items-center gap-0.5 bg-amber-950/80 border border-amber-600/40 px-1.5 py-0.5 rounded">
                    <Key size={9} color={THEME_COLORS.warningIcon} />
                    <Text className="text-[9px] font-mono font-bold text-amber-400">
                      PRIMARY KEY
                    </Text>
                  </View>
                )}

                {/* Disabled Badge */}
                {idx.disabled && (
                  <View className="bg-rose-950/80 border border-rose-600/40 px-1.5 py-0.5 rounded">
                    <Text className="text-[9px] font-mono font-bold text-rose-400">
                      DISABLED
                    </Text>
                  </View>
                )}
              </View>
            </View>

            {/* Key Columns in Order */}
            <View className="bg-slate-900/80 border border-slate-800/80 rounded-lg p-2.5 gap-2">
              <View className="flex-row items-center gap-1.5 flex-wrap">
                <Text className="text-[10px] text-slate-500 font-medium">
                  Key Columns:
                </Text>
                {idx.key_columns.map((kc) => (
                  <View
                    key={kc.name}
                    className="flex-row items-center gap-1 bg-slate-800/90 border border-slate-700/60 px-1.5 py-0.5 rounded"
                  >
                    <Text className="text-xs font-mono font-bold text-slate-200">
                      {kc.name}
                    </Text>
                    {kc.descending ? (
                      <View className="flex-row items-center">
                        <ArrowDown size={10} color={THEME_COLORS.dangerIcon} />
                        <Text className="text-[8px] font-mono text-rose-400">DESC</Text>
                      </View>
                    ) : (
                      <View className="flex-row items-center">
                        <ArrowUp size={10} color={THEME_COLORS.successIcon} />
                        <Text className="text-[8px] font-mono text-emerald-400">ASC</Text>
                      </View>
                    )}
                  </View>
                ))}
              </View>

              {/* Included Columns if present */}
              {idx.included_columns && idx.included_columns.length > 0 && (
                <View className="flex-row items-center gap-1.5 flex-wrap pt-1 border-t border-slate-800">
                  <Text className="text-[10px] text-slate-500 font-medium">
                    Covered / Included:
                  </Text>
                  {idx.included_columns.map((inc) => (
                    <View
                      key={inc}
                      className="bg-slate-800/50 px-1.5 py-0.2 rounded border border-slate-700/40"
                    >
                      <Text className="text-[10px] font-mono text-slate-400">
                        {inc}
                      </Text>
                    </View>
                  ))}
                </View>
              )}
            </View>
          </View>
        );
      })}
    </View>
  );
};
