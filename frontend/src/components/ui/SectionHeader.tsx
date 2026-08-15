import React from "react";
import { Text, View } from "react-native";

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  right?: React.ReactNode;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  subtitle,
  right,
}) => (
  <View className="flex-row items-center justify-between mb-2.5">
    <View>
      <Text className="text-sm font-bold text-white tracking-tight">{title}</Text>
      {subtitle && (
        <Text className="text-[11px] text-slate-400 mt-0.5">{subtitle}</Text>
      )}
    </View>
    {right}
  </View>
);
