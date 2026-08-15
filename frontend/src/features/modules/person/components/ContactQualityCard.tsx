import React from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import { ChevronRight } from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";

interface ContactQualityCardProps {
  title: string;
  count: number;
  issueCode: string;
  description: string;
  severity: "CRITICAL" | "WARNING" | "INFO";
  icon: React.ReactNode;
}

export const ContactQualityCard: React.FC<ContactQualityCardProps> = ({
  title,
  count,
  issueCode,
  description,
  severity,
  icon,
}) => {
  const router = useRouter();

  const handlePress = () => {
    router.push(`/daylite/quality?issue=${encodeURIComponent(issueCode)}` as Href);
  };

  const severityBadge = {
    CRITICAL: "bg-rose-950/60 border-rose-800/60 text-rose-300",
    WARNING: "bg-amber-950/60 border-amber-800/60 text-amber-300",
    INFO: "bg-blue-950/60 border-blue-800/60 text-blue-300",
  }[severity];

  return (
    <Pressable
      onPress={handlePress}
      accessibilityRole="button"
      accessibilityLabel={`View ${title} issues (${count} records)`}
      className="bg-dark-card border border-dark-border hover:border-blue-500/50 hover:bg-slate-800/60 active:bg-slate-900/90 rounded-xl p-3 shadow-sm transition-all flex-col justify-between gap-2 flex-1 min-w-[200px] group cursor-pointer"
    >
      <View className="flex-row items-center justify-between gap-2">
        <View className="flex-row items-center gap-2">
          <View className="w-6 h-6 rounded-md bg-slate-900 border border-slate-800 items-center justify-center group-hover:border-slate-700">
            {icon}
          </View>
          <Text className="text-xs font-bold text-white tracking-tight" numberOfLines={1}>
            {title}
          </Text>
        </View>
        <View className={`px-1.5 py-0.5 rounded border ${severityBadge}`}>
          <Text className={`text-[9px] font-bold ${severityBadge.split(" ").pop()}`}>
            {severity}
          </Text>
        </View>
      </View>

      <View className="flex-row items-baseline justify-between gap-2 mt-1">
        <Text
          className={`text-xl sm:text-2xl font-black font-mono ${
            count > 0 && severity === "CRITICAL"
              ? "text-rose-400"
              : count > 0 && severity === "WARNING"
              ? "text-amber-400"
              : count > 0
              ? "text-blue-400"
              : "text-slate-400"
          }`}
        >
          {count.toLocaleString()}
        </Text>
        <View className="flex-row items-center gap-0.5 opacity-80 group-hover:opacity-100 transition-opacity">
          <Text className="text-[10px] font-semibold text-blue-400">Drilldown</Text>
          <ChevronRight size={11} color={THEME_COLORS.primaryIcon} />
        </View>
      </View>

      <Text className="text-[10px] text-slate-400 line-clamp-1" numberOfLines={1}>
        {description}
      </Text>
    </Pressable>
  );
};
