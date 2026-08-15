import React from "react";
import { Pressable, Text, View } from "react-native";
import { AlertCircle, RefreshCw, WifiOff } from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";

interface ErrorStateProps {
  title?: string;
  message?: string;
  isNetworkError?: boolean;
  onRetry?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Failed to load",
  message = "Something went wrong.",
  isNetworkError = false,
  onRetry,
}) => (
  <View className="flex-1 items-center justify-center gap-4 py-16 px-6">
    <View className="w-12 h-12 rounded-2xl bg-rose-950/60 border border-rose-500/30 items-center justify-center">
      {isNetworkError ? (
        <WifiOff size={22} color={THEME_COLORS.danger} />
      ) : (
        <AlertCircle size={22} color={THEME_COLORS.danger} />
      )}
    </View>

    <View className="items-center gap-1 max-w-sm">
      <Text className="text-white text-base font-semibold">{title}</Text>
      <Text className="text-slate-400 text-xs text-center leading-relaxed">
        {message}
      </Text>
    </View>

    {onRetry && (
      <Pressable
        onPress={onRetry}
        accessibilityRole="button"
        accessibilityLabel="Retry failed request"
        className="bg-blue-600 active:bg-blue-700 px-5 py-2.5 rounded-xl flex-row items-center gap-2 mt-1 shadow-sm"
      >
        <RefreshCw size={13} color={THEME_COLORS.onPrimary} />
        <Text className="text-white text-xs font-bold">Retry</Text>
      </Pressable>
    )}
  </View>
);
