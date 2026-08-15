import React from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import { ArrowRight, ChevronRight, Database } from "lucide-react-native";
import { useDatabaseTables } from "@/hooks/useDatabase";
import { formatNumber } from "@/utils/formatters";
import { THEME_COLORS } from "@/constants/theme";

export const LargestTablesCard: React.FC = () => {
  const router = useRouter();

  const { data: tablesData, isLoading } = useDatabaseTables({
    sort_by: "estimated_rows",
    sort_order: "desc",
    limit: 5,
  });

  const tables = tablesData?.items || [];
  const maxRows = Math.max(...tables.map((t) => t.estimated_rows || 0), 1);

  if (isLoading && tables.length === 0) {
    return null;
  }

  return (
    <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3">
      <View className="flex-row items-center justify-between">
        <View className="flex-row items-center gap-2">
          <Database size={15} color={THEME_COLORS.successIcon} />
          <Text className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Largest Tables by Volume
          </Text>
        </View>

        <Pressable
          onPress={() => router.push("/database" as Href)}
          className="flex-row items-center gap-1"
        >
          <Text className="text-xs font-semibold text-blue-400">View All</Text>
          <ArrowRight size={11} color={THEME_COLORS.primaryIcon} />
        </Pressable>
      </View>

      {/* ── Ranked Tables List ───────────────────────────── */}
      <View className="gap-2.5">
        {tables.map((t, idx) => {
          const fillWidth = Math.min(
            100,
            Math.max(4, (t.estimated_rows / maxRows) * 100)
          );

          return (
            <Pressable
              key={`${t.schema}.${t.table}`}
              onPress={() => {
                const s = encodeURIComponent(t.schema);
                const tbl = encodeURIComponent(t.table);
                router.push(`/database/${s}/${tbl}` as Href);
              }}
              className="gap-1.5 p-2 rounded-lg hover:bg-slate-900 active:bg-slate-800 transition-colors"
            >
              <View className="flex-row items-center justify-between">
                <View className="flex-row items-center gap-2 flex-1 min-w-[180px]">
                  <Text className="text-[10px] font-mono text-slate-500 w-4">
                    #{idx + 1}
                  </Text>
                  <Text
                    className="text-xs font-mono font-bold text-slate-200"
                    numberOfLines={1}
                  >
                    {t.table}
                  </Text>
                  <View className="bg-slate-900 px-1 py-0.2 rounded border border-slate-800">
                    <Text className="text-[9px] font-mono text-slate-400">
                      {t.schema}
                    </Text>
                  </View>
                </View>

                <View className="flex-row items-center gap-1.5">
                  <Text className="text-xs font-mono font-bold text-emerald-400">
                    {formatNumber(t.estimated_rows)}
                  </Text>
                  <Text className="text-[10px] text-slate-500">rows</Text>
                  <ChevronRight size={12} color={THEME_COLORS.textDark} />
                </View>
              </View>

              {/* Proportional Volume Bar */}
              <View className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <View
                  style={{ width: `${fillWidth}%` }}
                  className="h-full bg-emerald-500 rounded-full"
                />
              </View>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
};
