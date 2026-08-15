import React from "react";
import { Text, View } from "react-native";
import type { SensitivityLevel } from "@/types/classification.types";

interface SensitivityBadgeProps {
  sensitivity: SensitivityLevel | string;
}

export const SensitivityBadge: React.FC<SensitivityBadgeProps> = ({ sensitivity }) => {
  const getStyles = () => {
    switch (sensitivity) {
      case "PII":
        return { bg: "bg-rose-950/80", border: "border-rose-500/50", text: "text-rose-400" };
      case "SENSITIVE":
        return { bg: "bg-purple-950/80", border: "border-purple-500/50", text: "text-purple-400" };
      case "INTERNAL":
        return { bg: "bg-blue-950/80", border: "border-blue-500/50", text: "text-blue-400" };
      case "PUBLIC":
      default:
        return { bg: "bg-emerald-950/80", border: "border-emerald-500/50", text: "text-emerald-400" };
    }
  };

  const styles = getStyles();

  return (
    <View className={`px-2 py-0.5 rounded border self-start ${styles.bg} ${styles.border}`}>
      <Text className={`text-[10px] font-bold uppercase tracking-wider ${styles.text}`}>
        {sensitivity}
      </Text>
    </View>
  );
};
