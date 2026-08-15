import React from "react";
import { Text, View } from "react-native";
import {
  AlertTriangle,
  CheckCircle2,
  Database,
  ExternalLink,
  Key,
  XCircle,
} from "lucide-react-native";
import { Link } from "expo-router";
import type { Href } from "expo-router";
import type {
  DetailedModuleValidation,
  ModuleDefinition,
  ModuleTableDefinition,
  TableValidationDetail,
} from "@/types/modules.types";
import { THEME_COLORS } from "@/constants/theme";

interface ModuleTablesListProps {
  module: ModuleDefinition;
  validation?: DetailedModuleValidation;
}

export const ModuleTablesList: React.FC<ModuleTablesListProps> = ({
  module,
  validation,
}) => {
  const tableValByName = React.useMemo(() => {
    const map = new Map<string, TableValidationDetail>();
    if (validation?.table_validations) {
      for (const tv of validation.table_validations) {
        const tblName = tv.table ?? tv.table_name ?? "";
        map.set(tblName.toLowerCase(), tv);
      }
    }
    return map;
  }, [validation]);

  return (
    <View className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-sm">
      {/* Header */}
      <View className="flex-row items-center justify-between mb-4 pb-3 border-b border-dark-border">
        <View>
          <Text className="text-sm font-bold text-white uppercase tracking-wider">
            Domain Schema & Mapped Tables
          </Text>
          <Text className="text-xs text-slate-400 mt-0.5">
            Configured MSSQL tables, primary keys, and schema validation
          </Text>
        </View>

        <View className="flex-row items-center gap-2">
          <View className="bg-slate-800 px-2.5 py-1 rounded-md border border-slate-700">
            <Text className="text-xs font-mono font-bold text-slate-300">
              {module.tables.length} Tables
            </Text>
          </View>
        </View>
      </View>

      {/* Validation Banner if warnings or errors */}
      {validation && (
        <View className="mb-4 gap-2">
          {validation.validation_warnings.length > 0 && (
            <View className="bg-amber-950/40 border border-amber-800/50 rounded-lg p-3">
              <View className="flex-row items-start gap-2">
                <AlertTriangle size={15} color={THEME_COLORS.warning} className="mt-0.5" />
                <View className="flex-1">
                  <Text className="text-xs font-semibold text-amber-300 mb-1">
                    Validation Warnings
                  </Text>
                  {validation.validation_warnings.map((warn: string, i: number) => (
                    <Text key={i} className="text-xs text-amber-200/80">
                      • {warn}
                    </Text>
                  ))}
                </View>
              </View>
            </View>
          )}

          {validation.validation_errors.length > 0 && (
            <View className="bg-rose-950/40 border border-rose-800/50 rounded-lg p-3">
              <View className="flex-row items-start gap-2">
                <XCircle size={15} color={THEME_COLORS.danger} className="mt-0.5" />
                <View className="flex-1">
                  <Text className="text-xs font-semibold text-rose-300 mb-1">
                    Validation Errors
                  </Text>
                  {validation.validation_errors.map((err: string, i: number) => (
                    <Text key={i} className="text-xs text-rose-200/80">
                      • {err}
                    </Text>
                  ))}
                </View>
              </View>
            </View>
          )}
        </View>
      )}

      {/* Tables Grid */}
      <View className="gap-3">
        {module.tables.map((tbl: ModuleTableDefinition) => {
          const valInfo = tableValByName.get(tbl.table.toLowerCase());
          const isRoot = tbl.role === "ROOT";
          const exists = valInfo ? valInfo.exists : true;
          const rowsEstimate = valInfo?.estimated_rows ?? valInfo?.row_count_estimate;

          return (
            <View
              key={`${tbl.schema}.${tbl.table}`}
              className={`border rounded-xl p-4 transition-all ${
                isRoot
                  ? "bg-blue-950/20 border-blue-500/30"
                  : "bg-dark-bg/60 border-dark-border/80"
              }`}
            >
              {/* Top Row: Table Name & Role */}
              <View className="flex-row items-center justify-between mb-2">
                <View className="flex-row items-center gap-2 flex-1">
                  <Database
                    size={15}
                    color={isRoot ? THEME_COLORS.primaryIcon : THEME_COLORS.textMuted}
                  />
                  <Text className="text-sm font-bold text-white font-mono">
                    {tbl.schema}.{tbl.table}
                  </Text>

                  {/* Role Badge */}
                  <View
                    className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider ${
                      isRoot
                        ? "bg-blue-600/30 border border-blue-500/40 text-blue-300"
                        : "bg-slate-800 text-slate-400"
                    }`}
                  >
                    <Text
                      className={`text-[10px] font-bold ${
                        isRoot ? "text-blue-300" : "text-slate-400"
                      }`}
                    >
                      {tbl.role}
                    </Text>
                  </View>

                  {/* Required Indicator */}
                  {tbl.required && (
                    <View className="bg-amber-950/60 border border-amber-800/60 px-1.5 py-0.5 rounded">
                      <Text className="text-[9px] font-bold text-amber-300 uppercase">
                        Required
                      </Text>
                    </View>
                  )}
                </View>

                {/* Validation Status / DB Link */}
                <View className="flex-row items-center gap-3">
                  {valInfo && (
                    <View className="flex-row items-center gap-1.5">
                      {exists ? (
                        <CheckCircle2 size={14} color={THEME_COLORS.success} />
                      ) : (
                        <XCircle size={14} color={THEME_COLORS.danger} />
                      )}
                      <Text
                        className={`text-xs font-semibold ${
                          exists ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {exists ? "Verified" : "Missing"}
                      </Text>
                    </View>
                  )}

                  <Link
                    href={`/database/${tbl.schema}/${tbl.table}` as Href}
                    className="flex-row items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                  >
                    <Text className="text-xs text-blue-400">View Table</Text>
                    <ExternalLink size={12} color={THEME_COLORS.primaryIcon} />
                  </Link>
                </View>
              </View>

              {/* Description */}
              {tbl.description && (
                <Text className="text-xs text-slate-400 mb-3 leading-relaxed">
                  {tbl.description}
                </Text>
              )}

              {/* Stats & Columns */}
              <View className="flex-row flex-wrap items-center gap-4 pt-2.5 border-t border-dark-border/60">
                {valInfo && (
                  <>
                    <View className="flex-row items-center gap-1.5">
                      <Text className="text-[11px] text-slate-500">Rows:</Text>
                      <Text className="text-xs font-mono font-bold text-slate-300">
                        {rowsEstimate !== undefined && rowsEstimate !== null
                          ? rowsEstimate.toLocaleString()
                          : "N/A"}
                      </Text>
                    </View>

                    <View className="flex-row items-center gap-1.5">
                      <Text className="text-[11px] text-slate-500">Columns:</Text>
                      <Text className="text-xs font-mono font-bold text-slate-300">
                        {valInfo.column_count ?? tbl.key_columns.length + tbl.important_columns.length}
                      </Text>
                    </View>
                  </>
                )}

                {/* Key Columns */}
                <View className="flex-row items-center gap-1.5 flex-wrap">
                  <Key size={12} color={THEME_COLORS.warning} />
                  <Text className="text-[11px] text-slate-500">Keys:</Text>
                  {tbl.key_columns.map((kc: string) => (
                    <Text
                      key={kc}
                      className="text-[11px] font-mono bg-slate-800 text-amber-300 px-1.5 py-0.5 rounded"
                    >
                      {kc}
                    </Text>
                  ))}
                </View>
              </View>
            </View>
          );
        })}
      </View>
    </View>
  );
};
