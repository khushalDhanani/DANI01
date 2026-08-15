import React, { useState } from "react";
import { Text, TextInput, View } from "react-native";
import { Activity, Search } from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import { useTableClassification, useTableProfile } from "@/hooks/useTable";
import { isColumnExposeSuppressed } from "@/utils/privacy";
import { ColumnProfileCard } from "@/components/tables/ColumnProfileCard";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";

interface TableProfileTabProps {
  schema: string;
  table: string;
}

export const TableProfileTab: React.FC<TableProfileTabProps> = ({
  schema,
  table,
}) => {
  const [filter, setFilter] = useState("");

  const {
    data: profileData,
    isLoading: isProfileLoading,
    isError: isProfileError,
    error: profileError,
    refetch: refetchProfile,
  } = useTableProfile(schema, table);

  const { data: classificationData } = useTableClassification(schema, table);
  const classifications = classificationData?.columns;

  if (isProfileLoading && !profileData) {
    return <LoadingState message={`Profiling columns in ${schema}.${table}…`} />;
  }

  if (isProfileError) {
    return (
      <ErrorState
        message={profileError?.message || "Failed to load column profiles."}
        onRetry={refetchProfile}
      />
    );
  }

  const columns = profileData?.columns || [];
  const filteredColumns = columns.filter((col) => {
    const name = col.name || col.column_name || "";
    return (
      name.toLowerCase().includes(filter.toLowerCase()) ||
      col.profile_type?.toLowerCase().includes(filter.toLowerCase()) ||
      col.data_type?.toLowerCase().includes(filter.toLowerCase())
    );
  });

  return (
    <View className="gap-3">
      {/* ── Toolbar: Column Search & Sample Summary ──────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2 bg-dark-card border border-dark-border p-2.5 rounded-xl">
        <View className="flex-row items-center gap-1.5 flex-1 min-w-[200px] bg-slate-900 border border-slate-800 rounded-lg px-2 py-1">
          <Search size={13} color={THEME_COLORS.textMuted} />
          <TextInput
            value={filter}
            onChangeText={setFilter}
            placeholder={`Search ${columns.length} column profiles…`}
            placeholderTextColor={THEME_COLORS.textDark}
            className="flex-1 text-xs text-white px-2 py-0"
            autoCapitalize="none"
          />
        </View>

        {profileData && (
          <View className="flex-row items-center gap-1.5 px-2">
            <Activity size={13} color={THEME_COLORS.successIcon} />
            <Text className="text-xs text-slate-400">
              Sample size:{" "}
              <Text className="font-mono font-bold text-white">
                {profileData.returned_rows} rows
              </Text>
            </Text>
          </View>
        )}
      </View>

      {/* ── Profile Cards List ───────────────────────────── */}
      {filteredColumns.length === 0 ? (
        <EmptyState
          title="No profiles found"
          message={
            filter
              ? `No column profiles match "${filter}".`
              : "No column profile statistics available."
          }
        />
      ) : (
        <View className="gap-2.5">
          {filteredColumns.map((col) => {
            const colName = col.name || col.column_name || "";
            const isMasked = isColumnExposeSuppressed(colName, classifications);

            return (
              <ColumnProfileCard
                key={colName}
                profile={col}
                isMasked={isMasked}
              />
            );
          })}
        </View>
      )}
    </View>
  );
};
