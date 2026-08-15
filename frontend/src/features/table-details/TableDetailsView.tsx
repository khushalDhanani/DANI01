import React, { useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import {
  Activity,
  Columns,
  Database,
  Layers,
  LayoutDashboard,
  Network,
  ShieldCheck,
} from "lucide-react-native";
import {
  useTableClassification,
  useTableColumns,
  useTableIndexes,
  useTableKeys,
  useTableProfile,
  useTableSummary,
} from "@/hooks/useTable";
import { TableDetailHeader } from "@/components/tables/TableDetailHeader";
import { TableOverviewTab } from "@/components/tables/TableOverviewTab";
import { TableColumnsTab } from "@/components/tables/TableColumnsTab";
import { TableRelationshipsTab } from "@/components/tables/TableRelationshipsTab";
import { TableIndexesTab } from "@/components/tables/TableIndexesTab";
import { SampleDataGrid } from "@/components/tables/SampleDataGrid";
import { TableProfileTab } from "@/components/tables/TableProfileTab";
import { TableClassificationTab } from "@/components/tables/TableClassificationTab";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { THEME_COLORS } from "@/constants/theme";

interface TableDetailsViewProps {
  schema: string;
  table: string;
}

export type ActiveDetailTab =
  | "overview"
  | "columns"
  | "relationships"
  | "indexes"
  | "sample"
  | "profile"
  | "classification";

export const TableDetailsView: React.FC<TableDetailsViewProps> = ({
  schema,
  table,
}) => {
  const [activeTab, setActiveTab] = useState<ActiveDetailTab>("overview");

  // Summary query loads immediately
  const {
    data: summary,
    isLoading: isSummaryLoading,
    isError: isSummaryError,
    error: summaryError,
    refetch: refetchSummary,
  } = useTableSummary(schema, table);

  // Lazy tab queries enabled as needed
  const {
    data: columns,
    isLoading: isColumnsLoading,
    isError: isColumnsError,
    error: columnsError,
    refetch: refetchColumns,
  } = useTableColumns(schema, table, {
    enabled: Boolean(schema && table) && (activeTab === "columns" || activeTab === "overview"),
  });

  const {
    data: keys,
    isLoading: isKeysLoading,
    isError: isKeysError,
    error: keysError,
    refetch: refetchKeys,
  } = useTableKeys(schema, table, {
    enabled: Boolean(schema && table) && (activeTab === "relationships" || activeTab === "overview"),
  });

  const {
    data: indexesResponse,
    isLoading: isIndexesLoading,
    isError: isIndexesError,
    error: indexesError,
    refetch: refetchIndexes,
  } = useTableIndexes(schema, table, {
    enabled: Boolean(schema && table) && (activeTab === "indexes" || activeTab === "overview"),
  });

  // Query classification for tab count badge
  const { data: classificationData } = useTableClassification(schema, table, {
    enabled: Boolean(schema && table) && (activeTab === "classification" || activeTab === "sample" || activeTab === "profile"),
  });

  // Query profile for tab count badge
  const { data: profileData } = useTableProfile(schema, table, {
    enabled: Boolean(schema && table) && activeTab === "profile",
  });

  const estimatedRows = summary?.estimated_rows ?? 0;
  const columnCount = summary?.column_count ?? columns?.length ?? 0;
  const fkCount = keys?.foreign_keys.length ?? 0;
  const indexCount = indexesResponse?.indexes.length ?? 0;
  const classifiedCount = classificationData?.columns.length;
  const profiledCount = profileData?.columns.length;

  if (isSummaryLoading && !summary) {
    return <LoadingState message={`Inspecting ${schema}.${table} metadata…`} />;
  }

  if (isSummaryError) {
    return (
      <ErrorState
        message={summaryError?.message || `Failed to load table ${schema}.${table}`}
        onRetry={refetchSummary}
      />
    );
  }

  const tabs: {
    key: ActiveDetailTab;
    label: string;
    icon: React.ComponentType<{ size?: number; color?: string }>;
    count?: number;
  }[] = [
    { key: "overview", label: "Overview", icon: LayoutDashboard },
    { key: "columns", label: "Columns", icon: Columns, count: columnCount },
    { key: "relationships", label: "Relationships", icon: Network, count: fkCount },
    { key: "indexes", label: "Indexes", icon: Layers, count: indexCount },
    { key: "sample", label: "Sample", icon: Database },
    { key: "profile", label: "Profile", icon: Activity, count: profiledCount },
    { key: "classification", label: "Classification", icon: ShieldCheck, count: classifiedCount },
  ];

  return (
    <ScrollView
      style={{ flex: 1, height: "100%" }}
      showsVerticalScrollIndicator={true}
      contentContainerStyle={{ flexGrow: 1, paddingBottom: 24, gap: 14 }}
      nestedScrollEnabled={true}
    >
      {/* ── Table Header Banner ──────────────────────────── */}
      <TableDetailHeader
        schema={schema}
        table={table}
        estimatedRows={estimatedRows}
        columnCount={columnCount}
      />

      {/* ── Navigation Tabs Bar ──────────────────────────── */}
      <View className="bg-dark-card border border-dark-border p-1 rounded-xl">
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={{ gap: 6, alignItems: "center" }}
          style={{ flexGrow: 0 }}
        >
          {tabs.map((tab) => {
            const isActive = activeTab === tab.key;
            const Icon = tab.icon;

            return (
              <Pressable
                key={tab.key}
                onPress={() => setActiveTab(tab.key)}
                accessibilityRole="button"
                accessibilityLabel={`${tab.label} tab`}
                style={{ height: 32 }}
                className={`flex-row items-center justify-center gap-1.5 px-3 rounded-lg transition-colors ${
                  isActive
                    ? "bg-blue-600 shadow-sm"
                    : "hover:bg-slate-900 active:bg-slate-800"
                }`}
              >
                <Icon size={13} color={isActive ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted} />
                <Text
                  className={`text-xs font-semibold ${
                    isActive ? "text-white" : "text-slate-400"
                  }`}
                >
                  {tab.label}
                </Text>

                {tab.count !== undefined && (
                  <View
                    className={`px-1.5 py-0.5 rounded ${
                      isActive ? "bg-blue-700/90" : "bg-slate-900"
                    }`}
                  >
                    <Text
                      className={`text-[10px] font-mono font-bold ${
                        isActive ? "text-white" : "text-slate-400"
                      }`}
                    >
                      {tab.count}
                    </Text>
                  </View>
                )}
              </Pressable>
            );
          })}
        </ScrollView>
      </View>

      {/* ── Tab Content Area ─────────────────────────────── */}
      {activeTab === "overview" && (
        <TableOverviewTab
          schema={schema}
          table={table}
          estimatedRows={estimatedRows}
          columnCount={columnCount}
          columns={columns}
          keys={keys}
          indexes={indexesResponse?.indexes}
          onSelectTab={setActiveTab}
        />
      )}

      {activeTab === "columns" && (
        isColumnsLoading && !columns ? (
          <LoadingState message="Loading table columns…" />
        ) : isColumnsError ? (
          <ErrorState
            message={columnsError?.message || "Failed to load columns."}
            onRetry={refetchColumns}
          />
        ) : (
          <TableColumnsTab columns={columns || []} />
        )
      )}

      {activeTab === "relationships" && (
        isKeysLoading && !keys ? (
          <LoadingState message="Loading relationship constraints…" />
        ) : isKeysError ? (
          <ErrorState
            message={keysError?.message || "Failed to load relationships."}
            onRetry={refetchKeys}
          />
        ) : (
          <TableRelationshipsTab keys={keys} />
        )
      )}

      {activeTab === "indexes" && (
        isIndexesLoading && !indexesResponse ? (
          <LoadingState message="Loading table indexes…" />
        ) : isIndexesError ? (
          <ErrorState
            message={indexesError?.message || "Failed to load indexes."}
            onRetry={refetchIndexes}
          />
        ) : (
          <TableIndexesTab indexes={indexesResponse?.indexes} />
        )
      )}

      {activeTab === "sample" && (
        <SampleDataGrid schema={schema} table={table} />
      )}

      {activeTab === "profile" && (
        <TableProfileTab schema={schema} table={table} />
      )}

      {activeTab === "classification" && (
        <TableClassificationTab schema={schema} table={table} />
      )}
    </ScrollView>
  );
};
