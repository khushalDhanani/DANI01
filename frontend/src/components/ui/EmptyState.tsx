import React from "react";
import { Text, View } from "react-native";

interface EmptyStateProps {
  title?: string;
  message?: string;
  icon?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = "No data",
  message = "Nothing to display yet.",
  icon,
}) => (
  <View className="flex-1 items-center justify-center gap-3 py-16 px-6">
    {icon && (
      <View className="w-12 h-12 rounded-2xl bg-slate-800 border border-slate-700 items-center justify-center">
        {icon}
      </View>
    )}
    <View className="items-center gap-1">
      <Text className="text-white text-base font-semibold">{title}</Text>
      <Text className="text-slate-500 text-sm text-center max-w-xs">{message}</Text>
    </View>
  </View>
);
