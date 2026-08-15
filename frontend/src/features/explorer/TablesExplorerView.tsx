import React, { useState } from "react";
import { FlatList, Pressable, Text, View } from "react-native";
import {
  ArrowDownAZ,
  ArrowDownWideNarrow,
  ArrowUpAZ,
  ArrowUpNarrowWide,
  Database,
  Layers,
  RotateCcw,
} from "lucide-react-native";
import { useDatabaseSchemas, useDatabaseTables } from "@/hooks/useDatabase";
import { useUIStore } from "@/hooks/useUIStore";
import { TableSearch } from "@/components/tables/TableSearch";
import { SchemaFilter } from "@/components/tables/SchemaFilter";
import { TableListItem } from "@/components/tables/TableListItem";
import { PaginationControls } from "@/components/tables/PaginationControls";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { THEME_COLORS } from "@/constants/theme";
import type { TableInfo } from "@/types/database.types";

export const TablesExplorerView: React.FC = () => {
  const {
    selectedSchema,
    setSelectedSchema,
    searchQuery,
    setSearchQuery,
  } = useUIStore();

  const [page, setPage] = useState(0);
  const [sortBy, setSortBy] = useState<"table" | "estimated_rows" | "column_count">("table");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const limit = 25;

  const { data: schemas } = useDatabaseSchemas();

  const {
    data: tablesData,
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = useDatabaseTables({
    schema: selectedSchema || undefined,
    search: searchQuery || undefined,
    sort_by: sortBy,
    sort_order: sortOrder,
    limit,
    offset: page * limit,
  });

  const handleSearchChange = (query: string) => {
    setSearchQuery(query);
    setPage(0);
  };

  const handleSchemaChange = (schema: string | null) => {
    setSelectedSchema(schema);
    setPage(0);
  };

  const handleToggleSort = (field: "table" | "estimated_rows" | "column_count") => {
    if (sortBy === field) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(field);
      setSortOrder(field === "estimated_rows" ? "desc" : "asc");
    }
    setPage(0);
  };

  const handleResetFilters = () => {
    setSelectedSchema(null);
    setSearchQuery("");
    setSortBy("table");
    setSortOrder("asc");
    setPage(0);
  };

  const hasActiveFilters = Boolean(selectedSchema || searchQuery);

  return (
    <View style={{ flex: 1, height: "100%", minHeight: 0 }} className="gap-3">
      {/* ── Header: Title & Sort Controls ───────────────────────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2">
        <View>
          <View className="flex-row items-center gap-1.5 mb-0.5">
            <Database size={13} color={THEME_COLORS.primaryIcon} />
            <Text className="text-[10px] font-bold uppercase tracking-wider text-blue-400">
              MSSQL Catalog
            </Text>
          </View>
          <Text className="text-lg sm:text-xl font-black text-white tracking-tight">
            Database Tables ({tablesData?.total !== undefined ? tablesData.total : "…"})
          </Text>
        </View>

        {/* Sort Selectors */}
        <View className="flex-row items-center gap-1.5 bg-dark-card border border-dark-border p-1 rounded-lg">
          <Text className="text-[10px] font-bold text-slate-500 px-1.5">Sort:</Text>

          {/* Table Name Sort */}
          <Pressable
            onPress={() => handleToggleSort("table")}
            className={`px-2 py-1 rounded flex-row items-center gap-1 ${
              sortBy === "table" ? "bg-blue-600" : "bg-slate-900 active:bg-slate-800"
            }`}
          >
            {sortOrder === "asc" && sortBy === "table" ? (
              <ArrowDownAZ size={12} color={sortBy === "table" ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted} />
            ) : (
              <ArrowUpAZ size={12} color={sortBy === "table" ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted} />
            )}
            <Text
              className={`text-[11px] font-semibold ${
                sortBy === "table" ? "text-white" : "text-slate-300"
              }`}
            >
              Name
            </Text>
          </Pressable>

          {/* Row Count Sort */}
          <Pressable
            onPress={() => handleToggleSort("estimated_rows")}
            className={`px-2 py-1 rounded flex-row items-center gap-1 ${
              sortBy === "estimated_rows" ? "bg-blue-600" : "bg-slate-900 active:bg-slate-800"
            }`}
          >
            {sortOrder === "desc" && sortBy === "estimated_rows" ? (
              <ArrowDownWideNarrow size={12} color={sortBy === "estimated_rows" ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted} />
            ) : (
              <ArrowUpNarrowWide size={12} color={sortBy === "estimated_rows" ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted} />
            )}
            <Text
              className={`text-[11px] font-semibold ${
                sortBy === "estimated_rows" ? "text-white" : "text-slate-300"
              }`}
            >
              Rows
            </Text>
          </Pressable>

          {/* Column Count Sort */}
          <Pressable
            onPress={() => handleToggleSort("column_count")}
            className={`px-2 py-1 rounded flex-row items-center gap-1 ${
              sortBy === "column_count" ? "bg-blue-600" : "bg-slate-900 active:bg-slate-800"
            }`}
          >
            <Layers size={12} color={sortBy === "column_count" ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted} />
            <Text
              className={`text-[11px] font-semibold ${
                sortBy === "column_count" ? "text-white" : "text-slate-300"
              }`}
            >
              Cols
            </Text>
          </Pressable>
        </View>
      </View>

      {/* ── Toolbar: Search & Schema Filter ─────────────────────── */}
      <View className="flex-row items-center flex-wrap gap-2.5 bg-dark-card border border-dark-border p-2.5 rounded-xl">
        <TableSearch
          value={searchQuery}
          onSearch={handleSearchChange}
          placeholder="Search 970+ tables by name…"
        />

        <View className="flex-row items-center gap-2">
          <SchemaFilter
            schemas={schemas}
            selectedSchema={selectedSchema}
            onSelectSchema={handleSchemaChange}
          />

          {hasActiveFilters && (
            <Pressable
              onPress={handleResetFilters}
              className="p-1.5 rounded-lg bg-slate-900 border border-dark-border active:bg-slate-800"
              accessibilityLabel="Reset all filters"
              accessibilityRole="button"
            >
              <RotateCcw size={13} color={THEME_COLORS.textMuted} />
            </Pressable>
          )}
        </View>
      </View>

      {/* ── Main Content / Table List ──────────────────────────── */}
      {isLoading && !tablesData ? (
        <LoadingState message="Discovering catalog tables…" />
      ) : isError ? (
        <ErrorState
          message={error?.message || "Failed to load database tables."}
          onRetry={refetch}
        />
      ) : tablesData && tablesData.items.length === 0 ? (
        <EmptyState
          title="No tables found"
          message={
            searchQuery
              ? `No tables matched "${searchQuery}" in ${selectedSchema || "any"} schema.`
              : `No tables found in ${selectedSchema || "the database"}.`
          }
        />
      ) : (
        <FlatList<TableInfo>
          data={tablesData?.items || []}
          renderItem={({ item }) => <TableListItem table={item} />}
          keyExtractor={(item) => `${item.schema}.${item.table}`}
          ItemSeparatorComponent={() => <View className="h-2" />}
          showsVerticalScrollIndicator={false}
          ListFooterComponent={
            tablesData ? (
              <PaginationControls
                page={page}
                limit={limit}
                total={tablesData.total}
                onPageChange={setPage}
                isFetching={isFetching}
              />
            ) : null
          }
          contentContainerStyle={{ paddingBottom: 16 }}
        />
      )}
    </View>
  );
};
