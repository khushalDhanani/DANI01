import React, { useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { Database } from "lucide-react-native";
import { useTableClassification, useTableSample } from "@/hooks/useTable";
import { isColumnExposeSuppressed } from "@/utils/privacy";
import { MaskedValue } from "@/components/tables/MaskedValue";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { THEME_COLORS } from "@/constants/theme";

interface SampleDataGridProps {
  schema: string;
  table: string;
}

export const SampleDataGrid: React.FC<SampleDataGridProps> = ({
  schema,
  table,
}) => {
  const [limit, setLimit] = useState<number>(50);

  const {
    data: sampleData,
    isLoading: isSampleLoading,
    isError: isSampleError,
    error: sampleError,
    refetch: refetchSample,
  } = useTableSample(schema, table, limit);

  // Fetch classification to apply defense-in-depth privacy masking
  const { data: classificationData } = useTableClassification(schema, table);

  const classifications = classificationData?.columns;

  if (isSampleLoading && !sampleData) {
    return <LoadingState message={`Fetching sample rows from ${schema}.${table}…`} />;
  }

  if (isSampleError) {
    return (
      <ErrorState
        message={sampleError?.message || "Failed to fetch sample data."}
        onRetry={refetchSample}
      />
    );
  }

  const columns = sampleData?.columns || [];
  const rows = sampleData?.rows || [];

  return (
    <View className="gap-3">
      {/* ── Toolbar: Sample Size Selector & Privacy Badge ─── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2 bg-dark-card border border-dark-border p-2.5 rounded-xl">
        <View className="flex-row items-center gap-1.5">
          <Database size={13} color={THEME_COLORS.primaryIcon} />
          <Text className="text-xs font-semibold text-slate-300">
            Source Sample:{" "}
            <Text className="font-mono font-bold text-white">
              {rows.length} rows
            </Text>
          </Text>
        </View>

        {/* Limit Selector */}
        <View className="flex-row items-center gap-1.5">
          <Text className="text-[10px] font-bold uppercase text-slate-500">
            Rows:
          </Text>
          {[25, 50, 100].map((count) => (
            <Pressable
              key={count}
              onPress={() => setLimit(count)}
              className={`px-2 py-0.5 rounded text-xs ${
                limit === count
                  ? "bg-blue-600 border border-blue-500"
                  : "bg-slate-900 border border-slate-800 active:bg-slate-800"
              }`}
            >
              <Text
                className={`text-[11px] font-mono font-bold ${
                  limit === count ? "text-white" : "text-slate-400"
                }`}
              >
                {count}
              </Text>
            </Pressable>
          ))}
        </View>
      </View>

      {/* ── Scrollable Tabular Data Grid ─────────────────── */}
      {rows.length === 0 ? (
        <EmptyState
          title="No sample rows"
          message="This table currently contains 0 records."
        />
      ) : (
        <View className="bg-dark-card border border-dark-border rounded-xl overflow-hidden">
          <ScrollView horizontal showsHorizontalScrollIndicator={true} nestedScrollEnabled={true}>
            <View>
              {/* Table Header */}
              <View className="flex-row bg-slate-900/90 border-b border-dark-border">
                <View className="w-12 px-3 py-2 border-r border-slate-800 justify-center">
                  <Text className="text-[10px] font-mono font-bold text-slate-500">
                    #
                  </Text>
                </View>

                {columns.map((col) => {
                  const isMasked = isColumnExposeSuppressed(col, classifications);
                  return (
                    <View
                      key={col}
                      className="w-44 px-3 py-2 border-r border-slate-800 justify-center"
                    >
                      <View className="flex-row items-center justify-between gap-1">
                        <Text
                          className="text-xs font-mono font-bold text-slate-200"
                          numberOfLines={1}
                        >
                          {col}
                        </Text>
                        {isMasked && (
                          <View className="bg-rose-950/80 px-1 py-0.2 rounded border border-rose-600/40">
                            <Text className="text-[8px] font-mono text-rose-400 font-bold">
                              PII
                            </Text>
                          </View>
                        )}
                      </View>
                    </View>
                  );
                })}
              </View>

              {/* Table Rows */}
              <ScrollView
                style={{ maxHeight: 420 }}
                showsVerticalScrollIndicator={true}
                nestedScrollEnabled={true}
              >
                {rows.map((row, rowIndex) => (
                  <View
                    key={rowIndex}
                    className={`flex-row border-b border-dark-border/60 ${
                      rowIndex % 2 === 1 ? "bg-slate-900/30" : ""
                    }`}
                  >
                    {/* Row Index */}
                    <View className="w-12 px-3 py-2 border-r border-slate-800/80 justify-center">
                      <Text className="text-[10px] font-mono text-slate-500">
                        {rowIndex + 1}
                      </Text>
                    </View>

                    {/* Columns Cells */}
                    {columns.map((col) => {
                      const isMasked = isColumnExposeSuppressed(
                        col,
                        classifications
                      );
                      const rawValue = row[col];

                      return (
                        <View
                          key={col}
                          className="w-44 px-3 py-2 border-r border-slate-800/80 justify-center"
                        >
                          <MaskedValue value={rawValue} isMasked={isMasked} />
                        </View>
                      );
                    })}
                  </View>
                ))}
              </ScrollView>
            </View>
          </ScrollView>
        </View>
      )}
    </View>
  );
};
