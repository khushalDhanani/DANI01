import React, { useState } from "react";
import { Text, TextInput, View } from "react-native";
import { Lock, Search, ShieldCheck, Tag } from "lucide-react-native";
import { useTableClassification } from "@/hooks/useTable";
import { SemanticBadge } from "@/components/tables/SemanticBadge";
import { SensitivityBadge } from "@/components/ui/SensitivityBadge";
import { ConfidenceIndicator } from "@/components/tables/ConfidenceIndicator";
import { ClassificationSummaryCard } from "@/components/visualizations/ClassificationSummaryCard";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { THEME_COLORS } from "@/constants/theme";

interface TableClassificationTabProps {
  schema: string;
  table: string;
}

export const TableClassificationTab: React.FC<TableClassificationTabProps> = ({
  schema,
  table,
}) => {
  const [filter, setFilter] = useState("");

  const {
    data: classificationData,
    isLoading,
    isError,
    error,
    refetch,
  } = useTableClassification(schema, table);

  if (isLoading && !classificationData) {
    return (
      <LoadingState
        message={`Running semantic classification for ${schema}.${table}…`}
      />
    );
  }

  if (isError) {
    return (
      <ErrorState
        message={error?.message || "Failed to load classifications."}
        onRetry={refetch}
      />
    );
  }

  const columns = classificationData?.columns || [];
  const filteredColumns = columns.filter((col) => {
    const name = col.name || col.column_name || "";
    return (
      name.toLowerCase().includes(filter.toLowerCase()) ||
      col.semantic_type?.toLowerCase().includes(filter.toLowerCase()) ||
      col.sensitivity?.toLowerCase().includes(filter.toLowerCase()) ||
      col.sql_type?.toLowerCase().includes(filter.toLowerCase())
    );
  });

  return (
    <View className="gap-3.5">
      {/* ── 1. Aggregate Classification Intelligence Card ─── */}
      <ClassificationSummaryCard classifications={columns} />

      {/* ── 2. Toolbar: Search & Summary ─────────────────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2 bg-dark-card border border-dark-border p-2.5 rounded-xl">
        <View className="flex-row items-center gap-1.5 flex-1 min-w-[200px] bg-slate-900 border border-slate-800 rounded-lg px-2 py-1">
          <Search size={13} color={THEME_COLORS.textMuted} />
          <TextInput
            value={filter}
            onChangeText={setFilter}
            placeholder={`Filter ${columns.length} classified columns…`}
            placeholderTextColor={THEME_COLORS.textDark}
            className="flex-1 text-xs text-white px-2 py-0"
            autoCapitalize="none"
          />
        </View>

        <View className="flex-row items-center gap-1.5 px-2">
          <ShieldCheck size={13} color={THEME_COLORS.primaryIcon} />
          <Text className="text-xs text-slate-400">
            Classified:{" "}
            <Text className="font-mono font-bold text-white">
              {columns.length} columns
            </Text>
          </Text>
        </View>
      </View>

      {/* ── 3. Classification Rows ───────────────────────── */}
      {filteredColumns.length === 0 ? (
        <EmptyState
          title="No classifications found"
          message={
            filter
              ? `No columns match "${filter}".`
              : "No semantic classifications available."
          }
        />
      ) : (
        <View className="gap-2">
          {filteredColumns.map((col) => {
            const colName = col.name || col.column_name || "";

            return (
              <View
                key={colName}
                className="bg-dark-card border border-dark-border rounded-xl p-3.5 gap-2.5"
              >
                {/* Top Row: Column Name + SQL Type + Confidence */}
                <View className="flex-row items-center justify-between flex-wrap gap-2">
                  <View className="flex-row items-center gap-2">
                    <Text className="text-xs font-mono font-bold text-white">
                      {colName}
                    </Text>
                    <Text className="text-[10px] font-mono text-slate-500">
                      {col.sql_type}
                    </Text>
                  </View>

                  <ConfidenceIndicator confidence={col.confidence} />
                </View>

                {/* Middle Row: Semantic Type Badge + Sensitivity Badge + Expose Policy */}
                <View className="flex-row items-center justify-between flex-wrap gap-2 pt-1">
                  <View className="flex-row items-center gap-2 flex-wrap">
                    <SemanticBadge type={col.semantic_type} />
                    <SensitivityBadge sensitivity={col.sensitivity} />
                  </View>

                  {/* Expose Policy Indicator */}
                  {col.expose_values ? (
                    <View className="flex-row items-center gap-1 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                      <Text className="text-[9px] font-mono text-slate-400">
                        Expose: ALLOWED
                      </Text>
                    </View>
                  ) : (
                    <View className="flex-row items-center gap-1 bg-rose-950/80 px-1.5 py-0.5 rounded border border-rose-600/40">
                      <Lock size={9} color={THEME_COLORS.dangerIcon} />
                      <Text className="text-[9px] font-mono text-rose-400 font-bold">
                        Expose: MASKED
                      </Text>
                    </View>
                  )}
                </View>

                {/* Signals Row */}
                {col.signals && col.signals.length > 0 && (
                  <View className="flex-row items-center gap-1 flex-wrap pt-1.5 border-t border-slate-800/80">
                    <Tag size={10} color={THEME_COLORS.textDark} />
                    <Text className="text-[9px] text-slate-500 font-medium mr-1">
                      Signals:
                    </Text>
                    {col.signals.map((sig) => (
                      <View
                        key={sig}
                        className="bg-slate-900 px-1.5 py-0.2 rounded border border-slate-800"
                      >
                        <Text className="text-[9px] font-mono text-slate-400">
                          {sig}
                        </Text>
                      </View>
                    ))}
                  </View>
                )}
              </View>
            );
          })}
        </View>
      )}
    </View>
  );
};
