import React from "react";
import { Text, View } from "react-native";
import { Database, Table as TableIcon } from "lucide-react-native";
import type { ModuleDefinition, ModuleValidationResult } from "@/types/modules.types";
import { ModuleStatusBadge } from "./ModuleStatusBadge";
import { THEME_COLORS } from "@/constants/theme";

interface ModuleHeaderProps {
  module?: ModuleDefinition;
  validation?: ModuleValidationResult;
  isLoading?: boolean;
}

export const ModuleHeader: React.FC<ModuleHeaderProps> = ({
  module,
  validation,
  isLoading = false,
}) => {
  if (isLoading || !module) {
    return (
      <View className="mb-3 pb-3 border-b border-dark-border">
        <View className="h-6 w-48 bg-slate-800 rounded mb-1.5" />
        <View className="h-3 w-80 bg-slate-800 rounded" />
      </View>
    );
  }

  return (
    <View className="mb-3 pb-3 border-b border-dark-border">
      {/* Title & Status Row */}
      <View className="flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <View className="flex-1">
          <View className="flex-row items-center gap-2 flex-wrap mb-1">
            <Text className="text-xl md:text-2xl font-black text-white tracking-tight">
              Daylite — Person Insights
            </Text>
            <View className="bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
              <Text className="text-[10px] font-mono font-bold text-slate-300">
                {module.code}
              </Text>
            </View>
            <ModuleStatusBadge
              status={validation?.status || (module.enabled ? "READY" : "DISABLED")}
              size="sm"
            />
          </View>

          <Text className="text-xs text-slate-400 max-w-3xl leading-snug">
            Real-time MSSQL telemetry across master entities, reachability channels, addresses, and linkages.
          </Text>
        </View>

        {/* Compact Metadata Chips */}
        <View className="flex-row items-center gap-2 self-start sm:self-auto flex-wrap">
          <View className="bg-dark-card border border-dark-border px-2.5 py-1 rounded-lg flex-row items-center gap-1.5">
            <Database size={12} color={THEME_COLORS.textMuted} />
            <Text className="text-[11px] font-mono text-slate-300">
              {module.root_schema}.{module.root_table}
            </Text>
          </View>

          <View className="bg-dark-card border border-dark-border px-2.5 py-1 rounded-lg flex-row items-center gap-1.5">
            <TableIcon size={12} color={THEME_COLORS.textMuted} />
            <Text className="text-[11px] font-mono text-slate-300">
              {module.tables.length} Tables
            </Text>
          </View>
        </View>
      </View>
    </View>
  );
};
