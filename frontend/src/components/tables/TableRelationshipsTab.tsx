import React from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import { ArrowRight, Key, Link2, ShieldAlert } from "lucide-react-native";
import type { TableKeysResponse } from "@/types/database.types";
import { EmptyState } from "@/components/ui/EmptyState";
import { THEME_COLORS } from "@/constants/theme";

interface TableRelationshipsTabProps {
  keys?: TableKeysResponse;
}

export const TableRelationshipsTab: React.FC<TableRelationshipsTabProps> = ({
  keys,
}) => {
  const router = useRouter();
  const pk = keys?.primary_key;
  const fks = keys?.foreign_keys ?? [];

  const handleNavigateToReferencedTable = (schema: string, table: string) => {
    const safeSchema = encodeURIComponent(schema);
    const safeTable = encodeURIComponent(table);
    router.push(`/database/${safeSchema}/${safeTable}` as Href);
  };

  return (
    <View className="gap-5">
      {/* ── Primary Key Section ───────────────────────────── */}
      <View className="gap-2">
        <Text className="text-xs font-bold uppercase tracking-wider text-slate-400">
          Primary Key Constraint
        </Text>

        {pk ? (
          <View className="bg-dark-card border border-amber-500/30 rounded-xl p-3.5 gap-2">
            <View className="flex-row items-center justify-between">
              <View className="flex-row items-center gap-2">
                <View className="p-1.5 rounded-lg bg-amber-950/80 border border-amber-600/40">
                  <Key size={14} color={THEME_COLORS.warningIcon} />
                </View>
                <Text className="text-xs font-bold text-white font-mono">
                  {pk.name}
                </Text>
              </View>
              <View className="bg-amber-950/60 px-2 py-0.5 rounded border border-amber-600/30">
                <Text className="text-[10px] font-mono text-amber-400 font-bold">
                  {pk.columns.length} column{pk.columns.length > 1 ? "s" : ""}
                </Text>
              </View>
            </View>

            <View className="flex-row items-center gap-1.5 flex-wrap pt-1">
              <Text className="text-[10px] text-slate-400">Key Columns:</Text>
              {pk.columns.map((col) => (
                <View
                  key={col.name}
                  className="bg-slate-900 border border-slate-800 px-2 py-0.5 rounded"
                >
                  <Text className="text-xs font-mono font-bold text-slate-200">
                    {col.name} <Text className="text-slate-500 font-normal">#{col.ordinal}</Text>
                  </Text>
                </View>
              ))}
            </View>
          </View>
        ) : (
          <View className="bg-dark-card border border-dark-border rounded-xl p-4 flex-row items-center gap-2.5">
            <ShieldAlert size={16} color={THEME_COLORS.textMuted} />
            <Text className="text-xs text-slate-400">
              This table does not have a primary key defined (Heap structure).
            </Text>
          </View>
        )}
      </View>

      {/* ── Foreign Keys Section ──────────────────────────── */}
      <View className="gap-2">
        <View className="flex-row items-center justify-between">
          <Text className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Foreign Key Relationships ({fks.length})
          </Text>
        </View>

        {fks.length === 0 ? (
          <EmptyState
            title="No foreign keys"
            message="This table has no outgoing foreign key constraints."
          />
        ) : (
          <View className="gap-2">
            {fks.map((fk) => (
              <View
                key={fk.name}
                className="bg-dark-card border border-dark-border rounded-xl p-3.5 gap-2.5"
              >
                {/* FK Name and Actions Header */}
                <View className="flex-row items-center justify-between flex-wrap gap-2">
                  <View className="flex-row items-center gap-2">
                    <View className="p-1 rounded-md bg-purple-950/80 border border-purple-600/40">
                      <Link2 size={12} color={THEME_COLORS.companyIcon} />
                    </View>
                    <Text className="text-xs font-bold text-white font-mono">
                      {fk.name}
                    </Text>
                  </View>

                  <View className="flex-row items-center gap-1.5">
                    {fk.on_delete && (
                      <View className="bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                        <Text className="text-[9px] font-mono text-slate-400">
                          DEL: {fk.on_delete}
                        </Text>
                      </View>
                    )}
                    {fk.on_update && (
                      <View className="bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                        <Text className="text-[9px] font-mono text-slate-400">
                          UPD: {fk.on_update}
                        </Text>
                      </View>
                    )}
                  </View>
                </View>

                {/* Local Column -> Referenced Column */}
                <View className="bg-slate-900/80 border border-slate-800/80 rounded-lg p-2.5 flex-row items-center justify-between flex-wrap gap-2">
                  <View className="flex-row items-center gap-1.5 flex-wrap">
                    {fk.columns.map((c) => (
                      <View key={c.column} className="flex-row items-center gap-1.5">
                        <Text className="text-xs font-mono font-bold text-slate-200">
                          {c.column}
                        </Text>
                        <ArrowRight size={11} color={THEME_COLORS.textDark} />
                        <Pressable
                          onPress={() =>
                            handleNavigateToReferencedTable(
                              fk.references.schema,
                              fk.references.table
                            )
                          }
                          className="flex-row items-center gap-1 hover:underline"
                        >
                          <Text className="text-xs font-mono font-bold text-blue-400">
                            {fk.references.schema}.{fk.references.table}
                          </Text>
                          <Text className="text-xs font-mono text-slate-400">
                            ({c.referenced_column})
                          </Text>
                        </Pressable>
                      </View>
                    ))}
                  </View>
                </View>
              </View>
            ))}
          </View>
        )}
      </View>
    </View>
  );
};
