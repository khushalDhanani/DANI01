import React, { useState } from "react";
import { Pressable, Text, View } from "react-native";
import { Database, Play, ShieldCheck, Zap } from "lucide-react-native";
import type { SchemaInfo } from "@/types/database.types";
import { THEME_COLORS } from "@/constants/theme";

interface AnalysisConfigCardProps {
  databaseName: string;
  totalTables?: number;
  schemas?: SchemaInfo[];
  isRunning: boolean;
  onStartAnalysis: (config: {
    schema?: string | null;
    maxConcurrent: number;
  }) => void;
}

export const AnalysisConfigCard: React.FC<AnalysisConfigCardProps> = ({
  databaseName,
  totalTables,
  schemas,
  isRunning,
  onStartAnalysis,
}) => {
  const [selectedSchema, setSelectedSchema] = useState<string | null>(null);
  const [maxConcurrent, setMaxConcurrent] = useState<number>(4);

  const handleStart = () => {
    onStartAnalysis({
      schema: selectedSchema,
      maxConcurrent,
    });
  };

  return (
    <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-4">
      {/* ── Context Header ───────────────────────────────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2">
        <View className="flex-row items-center gap-2.5">
          <View className="w-8 h-8 rounded-lg bg-blue-600 items-center justify-center">
            <Zap size={16} color={THEME_COLORS.onPrimary} />
          </View>
          <View>
            <Text className="text-sm font-bold text-white font-mono">
              {databaseName}
            </Text>
            <Text className="text-[10px] text-slate-500">
              Database-Wide Profiling & Semantic Classification
            </Text>
          </View>
        </View>

        <View className="flex-row items-center gap-1.5 bg-slate-900 border border-slate-800 px-2.5 py-1 rounded-md">
          <ShieldCheck size={12} color={THEME_COLORS.primaryIcon} />
          <Text className="text-[10px] font-semibold text-slate-400">
            Read-Only MSSQL Safe
          </Text>
        </View>
      </View>

      {/* ── Scope Selection (All vs Schema) ──────────────── */}
      <View className="gap-1.5">
        <Text className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
          Analysis Scope
        </Text>

        <View className="flex-row flex-wrap gap-2">
          {/* All Tables */}
          <Pressable
            onPress={() => setSelectedSchema(null)}
            className={`px-3 py-1.5 rounded-lg border flex-row items-center gap-1.5 ${
              selectedSchema === null
                ? "bg-blue-600 border-blue-500"
                : "bg-slate-900 border-slate-800 active:bg-slate-800"
            }`}
          >
            <Database
              size={12}
              color={selectedSchema === null ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted}
            />
            <Text
              className={`text-xs font-semibold ${
                selectedSchema === null ? "text-white" : "text-slate-300"
              }`}
            >
              All Tables ({totalTables ?? "970+"})
            </Text>
          </Pressable>

          {/* Individual Schemas */}
          {schemas?.map((s) => {
            const isSelected = selectedSchema === s.name;
            return (
              <Pressable
                key={s.name}
                onPress={() => setSelectedSchema(s.name)}
                className={`px-3 py-1.5 rounded-lg border flex-row items-center gap-1.5 ${
                  isSelected
                    ? "bg-blue-600 border-blue-500"
                    : "bg-slate-900 border-slate-800 active:bg-slate-800"
                }`}
              >
                <Text
                  className={`text-xs font-mono font-semibold ${
                    isSelected ? "text-white" : "text-slate-300"
                  }`}
                >
                  {s.name}
                </Text>
                <View
                  className={`px-1.5 py-0.2 rounded ${
                    isSelected ? "bg-blue-700/80" : "bg-slate-800"
                  }`}
                >
                  <Text
                    className={`text-[10px] font-mono ${
                      isSelected ? "text-blue-100" : "text-slate-400"
                    }`}
                  >
                    {s.table_count}
                  </Text>
                </View>
              </Pressable>
            );
          })}
        </View>
      </View>

      {/* ── Concurrency & Start Action ───────────────────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-3 pt-2 border-t border-slate-800/80">
        <View className="flex-row items-center gap-2">
          <Text className="text-[10px] font-bold uppercase text-slate-500">
            Concurrency:
          </Text>
          {[2, 4, 6, 8].map((c) => (
            <Pressable
              key={c}
              onPress={() => setMaxConcurrent(c)}
              className={`px-2 py-0.5 rounded text-xs ${
                maxConcurrent === c
                  ? "bg-blue-600 border border-blue-500"
                  : "bg-slate-900 border border-slate-800 active:bg-slate-800"
              }`}
            >
              <Text
                className={`text-[11px] font-mono font-bold ${
                  maxConcurrent === c ? "text-white" : "text-slate-400"
                }`}
              >
                {c}
              </Text>
            </Pressable>
          ))}
        </View>

        <Pressable
          onPress={handleStart}
          disabled={isRunning}
          className={`bg-blue-600 active:bg-blue-700 px-4 py-2 rounded-lg flex-row items-center gap-2 ${
            isRunning ? "opacity-50" : ""
          }`}
        >
          <Play size={14} color={THEME_COLORS.onPrimary} />
          <Text className="text-xs font-bold text-white">
            Run Quick Analysis
          </Text>
        </Pressable>
      </View>
    </View>
  );
};
