import React from "react";
import { Text, View } from "react-native";

interface ProgressBarProps {
  progress: number;
  label?: string;
  showPercent?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  label,
  showPercent = true,
}) => {
  const clamped = Math.min(100, Math.max(0, progress));

  return (
    <View className="w-full">
      {(label || showPercent) && (
        <View className="flex-row justify-between items-center mb-1.5">
          {label && (
            <Text className="text-xs font-semibold text-slate-300">{label}</Text>
          )}
          {showPercent && (
            <Text className="text-xs font-bold text-blue-400">
              {clamped.toFixed(1)}%
            </Text>
          )}
        </View>
      )}
      <View className="h-2.5 w-full bg-slate-800 rounded-full overflow-hidden border border-slate-700/50">
        <View
          className="h-full bg-blue-500 rounded-full"
          style={{ width: `${clamped}%` }}
        />
      </View>
    </View>
  );
};
