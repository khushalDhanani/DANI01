import React, { useState } from "react";
import { Text, TextInput, View } from "react-native";
import { Key, Link, Search, Sparkles } from "lucide-react-native";
import type { ColumnInfo } from "@/types/database.types";
import { EmptyState } from "@/components/ui/EmptyState";
import { THEME_COLORS } from "@/constants/theme";

interface TableColumnsTabProps {
  columns: ColumnInfo[];
}

export const TableColumnsTab: React.FC<TableColumnsTabProps> = ({ columns }) => {
  const [filter, setFilter] = useState("");

  const filteredColumns = columns.filter(
    (c) =>
      c.name.toLowerCase().includes(filter.toLowerCase()) ||
      c.data_type.toLowerCase().includes(filter.toLowerCase())
  );

  const formatDataType = (col: ColumnInfo): string => {
    let type = col.data_type;
    if (col.max_length !== null && col.max_length !== undefined) {
      if (col.max_length === -1) {
        type += "(max)";
      } else if (
        ["varchar", "nvarchar", "char", "nchar", "varbinary"].includes(
          col.data_type.toLowerCase()
        )
      ) {
        type += `(${col.max_length})`;
      }
    } else if (
      col.precision !== null &&
      col.precision !== undefined &&
      col.scale !== null &&
      col.scale !== undefined
    ) {
      if (["decimal", "numeric"].includes(col.data_type.toLowerCase())) {
        type += `(${col.precision},${col.scale})`;
      }
    }
    return type;
  };

  return (
    <View className="gap-3">
      {/* Search columns input if table has many columns */}
      {columns.length > 8 && (
        <View className="flex-row items-center bg-slate-900 border border-dark-border rounded-lg px-2.5 py-1.5">
          <Search size={13} color={THEME_COLORS.textMuted} />
          <TextInput
            value={filter}
            onChangeText={setFilter}
            placeholder={`Filter ${columns.length} columns…`}
            placeholderTextColor={THEME_COLORS.textDark}
            className="flex-1 text-xs text-white px-2 py-0"
            autoCapitalize="none"
          />
        </View>
      )}

      {/* Header Row */}
      <View className="flex-row items-center justify-between px-3 py-1 bg-slate-900/60 rounded-lg border border-slate-800 text-slate-500">
        <View className="flex-row items-center gap-3 flex-1">
          <Text className="text-[10px] font-bold uppercase text-slate-500 w-6">#</Text>
          <Text className="text-[10px] font-bold uppercase text-slate-500 flex-1">Column Name</Text>
        </View>
        <Text className="text-[10px] font-bold uppercase text-slate-500 w-32 text-right">Data Type</Text>
      </View>

      {/* Column Rows */}
      {filteredColumns.length === 0 ? (
        <EmptyState
          title="No matching columns"
          message={`No columns match "${filter}".`}
        />
      ) : (
        <View className="gap-1.5">
          {filteredColumns.map((col) => {
            const isPk = col.primary_key;
            const isFk = col.foreign_key;

            return (
              <View
                key={col.name}
                className="bg-dark-card border border-dark-border rounded-xl p-3 flex-row items-center justify-between gap-3"
              >
                {/* Left: Ordinal + Name + Badges */}
                <View className="flex-row items-center gap-2.5 flex-1 min-w-[200px]">
                  <Text className="text-[10px] font-mono text-slate-500 w-6">
                    {col.ordinal}
                  </Text>

                  <View className="flex-1">
                    <View className="flex-row items-center gap-1.5 flex-wrap">
                      <Text className="text-xs font-bold text-white font-mono">
                        {col.name}
                      </Text>

                      {/* PK Badge */}
                      {isPk && (
                        <View className="flex-row items-center gap-0.5 bg-amber-950/80 border border-amber-600/40 px-1.5 py-0.2 rounded">
                          <Key size={9} color={THEME_COLORS.warningIcon} />
                          <Text className="text-[9px] font-mono font-bold text-amber-400">
                            PK
                          </Text>
                        </View>
                      )}

                      {/* FK Badge */}
                      {isFk && (
                        <View className="flex-row items-center gap-0.5 bg-purple-950/80 border border-purple-600/40 px-1.5 py-0.2 rounded">
                          <Link size={9} color={THEME_COLORS.companyIcon} />
                          <Text className="text-[9px] font-mono font-bold text-purple-400">
                            FK
                          </Text>
                        </View>
                      )}

                      {/* Identity Badge */}
                      {col.identity && (
                        <View className="bg-blue-950/80 border border-blue-600/40 px-1.5 py-0.2 rounded">
                          <Text className="text-[9px] font-mono font-bold text-blue-400">
                            IDENTITY
                          </Text>
                        </View>
                      )}

                      {/* Computed Badge */}
                      {col.computed && (
                        <View className="flex-row items-center gap-0.5 bg-emerald-950/80 border border-emerald-600/40 px-1.5 py-0.2 rounded">
                          <Sparkles size={9} color={THEME_COLORS.successIcon} />
                          <Text className="text-[9px] font-mono font-bold text-emerald-400">
                            COMPUTED
                          </Text>
                        </View>
                      )}
                    </View>

                    {/* Default Definition if present */}
                    {col.default_definition && (
                      <Text className="text-[10px] text-slate-500 font-mono mt-0.5" numberOfLines={1}>
                        default: {col.default_definition}
                      </Text>
                    )}
                  </View>
                </View>

                {/* Right: Data Type & Nullability */}
                <View className="items-end gap-1">
                  <Text className="text-xs font-mono font-bold text-blue-400">
                    {formatDataType(col)}
                  </Text>
                  <View
                    className={`px-1.5 py-0.2 rounded border ${
                      col.nullable
                        ? "bg-slate-900 border-slate-800"
                        : "bg-rose-950/50 border-rose-600/30"
                    }`}
                  >
                    <Text
                      className={`text-[9px] font-mono ${
                        col.nullable ? "text-slate-400" : "text-rose-400 font-bold"
                      }`}
                    >
                      {col.nullable ? "NULL" : "NOT NULL"}
                    </Text>
                  </View>
                </View>
              </View>
            );
          })}
        </View>
      )}
    </View>
  );
};
