import React from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import {
  ArrowRight,
  Database,
  FolderTree,
  Layers,
  Table,
} from "lucide-react-native";
import { useDatabaseSchemas, useDatabaseSummary } from "@/hooks/useDatabase";
import { MetricCard } from "@/components/ui/MetricCard";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { SchemaDistributionCard } from "@/components/database/SchemaDistributionCard";
import { DistributionBar, type DistributionSegment } from "@/components/visualizations/DistributionBar";
import { LargestTablesCard } from "@/components/visualizations/LargestTablesCard";
import { formatNumber } from "@/utils/formatters";
import { THEME_COLORS } from "@/constants/theme";

export const DashboardView: React.FC = () => {
  const router = useRouter();
  const {
    data: summary,
    isLoading: isSummaryLoading,
    isError: isSummaryError,
    error: summaryError,
    refetch: refetchSummary,
  } = useDatabaseSummary();

  const {
    data: schemas,
    isLoading: isSchemasLoading,
    isError: isSchemasError,
    error: schemasError,
    refetch: refetchSchemas,
  } = useDatabaseSchemas();

  const isLoading = isSummaryLoading || isSchemasLoading;
  const isError = isSummaryError || isSchemasError;
  const errorMessage =
    summaryError?.message ||
    schemasError?.message ||
    "An error occurred while fetching database metrics.";

  const handleRetry = () => {
    refetchSummary();
    refetchSchemas();
  };

  if (isLoading) {
    return <LoadingState message="Fetching live database metadata…" />;
  }

  if (isError) {
    return <ErrorState message={errorMessage} onRetry={handleRetry} />;
  }

  if (!summary) {
    return (
      <EmptyState
        title="No database summary available"
        message="Could not retrieve metadata for the current database catalog."
      />
    );
  }

  const schemaPalette = [
    { color: "bg-blue-500", text: "text-blue-400" },
    { color: "bg-purple-500", text: "text-purple-400" },
    { color: "bg-emerald-500", text: "text-emerald-400" },
    { color: "bg-amber-500", text: "text-amber-400" },
  ];

  const schemaSegments: DistributionSegment[] = (schemas || []).map(
    (s, idx) => {
      const p = schemaPalette[idx % schemaPalette.length];
      const pct = summary.table_count > 0 ? (s.table_count / summary.table_count) * 100 : 0;
      return {
        label: s.name,
        count: s.table_count,
        percent: pct,
        color: p.color,
        textColor: p.text,
      };
    }
  );

  return (
    <View className="gap-5">
      {/* ── Compact Database Hero Header ───────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 shadow-sm">
        <View className="flex-row items-center justify-between flex-wrap gap-3">
          <View className="gap-0.5">
            <View className="flex-row items-center gap-1.5">
              <View className="w-2 h-2 rounded-full bg-emerald-400" />
              <Text className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">
                MSSQL Catalog Live
              </Text>
            </View>
            <Text className="text-xl sm:text-2xl font-black text-white tracking-tight font-mono">
              {summary.database}
            </Text>
            <Text className="text-xs text-slate-400 leading-normal max-w-lg">
              Primary production catalog intelligence: {formatNumber(summary.table_count)} tables across {summary.schema_count} schema namespaces.
            </Text>
          </View>

          <Pressable
            onPress={() => router.push("/database" as Href)}
            className="bg-blue-600 active:bg-blue-700 px-3.5 py-2 rounded-lg flex-row items-center gap-1.5"
          >
            <Text className="text-xs font-semibold text-white">
              Explore Tables
            </Text>
            <ArrowRight size={13} color={THEME_COLORS.onPrimary} />
          </Pressable>
        </View>
      </View>

      {/* ── Metric Cards Grid ─────────────────────────────────── */}
      <View>
        <SectionHeader
          title="Catalog Overview"
          subtitle="Summary statistics across all schemas"
        />
        <View className="flex-row flex-wrap gap-3">
          <MetricCard
            label="Total Tables"
            value={summary.table_count}
            sublabel="Catalog entities"
            icon={<Table size={15} color={THEME_COLORS.primaryIcon} />}
            accentBorder="border-blue-500/30"
          />
          <MetricCard
            label="Total Columns"
            value={summary.column_count}
            sublabel="Discovered attributes"
            icon={<Layers size={15} color={THEME_COLORS.accentIcon} />}
            accentBorder="border-purple-500/30"
          />
          <MetricCard
            label="Estimated Rows"
            value={summary.estimated_rows}
            compact={true}
            sublabel={`${formatNumber(summary.estimated_rows)} exact`}
            icon={<Database size={15} color={THEME_COLORS.successIcon} />}
            accentBorder="border-emerald-500/30"
          />
          <MetricCard
            label="Schemas"
            value={summary.schema_count}
            sublabel="Active namespaces"
            icon={<FolderTree size={15} color={THEME_COLORS.warningIcon} />}
            accentBorder="border-amber-500/30"
          />
        </View>
      </View>

      {/* ── Visual Schema Proportions Banner ──────────────────── */}
      {schemaSegments.length > 0 && (
        <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-2.5">
          <Text className="text-[10px] uppercase font-bold text-slate-400">
            Schema Namespace Table Distribution
          </Text>
          <DistributionBar
            segments={schemaSegments}
            totalCount={summary.table_count}
            totalLabel="Catalog Tables"
          />
        </View>
      )}

      {/* ── Largest Tables Visual Ranking ─────────────────────── */}
      <LargestTablesCard />

      {/* ── Schema Cards Detail Section ──────────────────────── */}
      <View>
        <SectionHeader
          title="Database Schemas"
          subtitle={`${schemas?.length || summary.schema_count} namespaces configured in catalog`}
          right={
            <Pressable
              onPress={() => router.push("/database" as Href)}
              className="flex-row items-center gap-1"
            >
              <Text className="text-xs font-semibold text-blue-400">
                View All Tables
              </Text>
              <ArrowRight size={12} color={THEME_COLORS.primaryIcon} />
            </Pressable>
          }
        />

        {schemas && schemas.length > 0 ? (
          <View className="gap-2">
            {schemas.map((s) => (
              <SchemaDistributionCard
                key={s.name}
                schema={s}
                totalTables={summary.table_count}
              />
            ))}
          </View>
        ) : (
          <EmptyState
            title="No schemas found"
            message="No schemas were returned by the backend."
          />
        )}
      </View>
    </View>
  );
};
