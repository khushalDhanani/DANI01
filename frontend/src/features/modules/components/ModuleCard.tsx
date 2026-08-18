import React from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import { ArrowRight, Database, GitFork, Table as TableIcon } from "lucide-react-native";
import type { ModuleInfo } from "@/types/modules.types";
import { ModuleStatusBadge } from "./ModuleStatusBadge";
import { THEME_COLORS } from "@/constants/theme";

interface ModuleCardProps {
  module: ModuleInfo;
}

export const ModuleCard: React.FC<ModuleCardProps> = ({ module }) => {
  const router = useRouter();

  const handleOpen = () => {
    router.push(`/modules/${module.code}` as Href);
  };

  return (
    <Pressable
      onPress={handleOpen}
      accessibilityRole="button"
      accessibilityLabel={`Open ${module.name} module`}
      className="bg-dark-card border border-dark-border hover:border-slate-700 active:border-blue-500/60 rounded-xl p-3 mb-4 shadow-sm transition-all"
    >
      {/* Header */}
      <View className="flex-row items-start justify-between gap-3 mb-2.5">
        <View className="flex-1">
          <View className="flex-row items-center gap-2 mb-1">
            <Text className="text-base font-bold text-white tracking-tight" numberOfLines={1}>
              {module.name}
            </Text>
            <View className="bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
              <Text className="text-[10px] font-mono font-bold text-slate-300">
                {module.code}
              </Text>
            </View>
          </View>
          <Text className="text-xs text-slate-400 leading-relaxed" numberOfLines={2}>
            {module.description}
          </Text>
        </View>

        <ModuleStatusBadge status={module.enabled ? "READY" : "DISABLED"} size="sm" />
      </View>

      {/* Metadata Chips */}
      <View className="flex-row flex-wrap items-center gap-3 py-3 border-t border-b border-dark-border/80 my-2">
        <View className="flex-row items-center gap-1.5 bg-slate-800/60 px-2.5 py-1 rounded-md">
          <Database size={13} color={THEME_COLORS.textMuted} />
          <Text className="text-xs text-slate-300 font-mono" numberOfLines={1}>
            {module.root_table}
          </Text>
        </View>

        <View className="flex-row items-center gap-1.5 bg-slate-800/60 px-2.5 py-1 rounded-md">
          <TableIcon size={13} color={THEME_COLORS.textMuted} />
          <Text className="text-xs text-slate-300">
            {module.table_count} tables
          </Text>
        </View>

        <View className="flex-row items-center gap-1.5 bg-slate-800/60 px-2.5 py-1 rounded-md">
          <GitFork size={13} color={THEME_COLORS.textMuted} />
          <Text className="text-xs text-slate-300">
            Active Module
          </Text>
        </View>
      </View>

      {/* Footer / CTA */}
      <View className="flex-row items-center justify-between mt-1">
        {/* Tags */}
        <View className="flex-row flex-wrap items-center gap-1.5 flex-1 mr-3">
          {(module.tags ?? []).slice(0, 3).map((tag: string) => (
            <View key={tag} className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
              <Text className="text-[10px] text-slate-400">#{tag}</Text>
            </View>
          ))}
        </View>

        {/* Action Button */}
        <View className="flex-row items-center gap-1.5 bg-blue-600/10 hover:bg-blue-600/20 active:bg-blue-600 px-3 py-1.5 rounded-lg border border-blue-500/30">
          <Text className="text-xs font-semibold text-blue-400">Open Module</Text>
          <ArrowRight size={13} color={THEME_COLORS.primaryIcon} />
        </View>
      </View>
    </Pressable>
  );
};
