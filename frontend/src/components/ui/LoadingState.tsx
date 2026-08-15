import React from "react";
import { ActivityIndicator, Text, View } from "react-native";
import { THEME_COLORS } from "@/constants/theme";

interface LoadingStateProps {
  message?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = "Loading…",
}) => (
  <View className="flex-1 items-center justify-center gap-3 py-16">
    <ActivityIndicator size="large" color={THEME_COLORS.primary} />
    <Text className="text-slate-500 text-sm">{message}</Text>
  </View>
);
