import React from "react";
import { Text, View } from "react-native";

interface ConfidenceIndicatorProps {
  confidence: number;
}

export const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
  confidence,
}) => {
  // Normalize confidence (whether 0.0-1.0 or 0-100)
  const percent =
    confidence <= 1.0 ? Math.round(confidence * 100) : Math.round(confidence);

  const getColor = () => {
    if (percent >= 90) return "bg-emerald-400";
    if (percent >= 70) return "bg-blue-400";
    if (percent >= 50) return "bg-amber-400";
    return "bg-rose-400";
  };

  const getTextColor = () => {
    if (percent >= 90) return "text-emerald-400";
    if (percent >= 70) return "text-blue-400";
    if (percent >= 50) return "text-amber-400";
    return "text-rose-400";
  };

  return (
    <View className="flex-row items-center gap-1.5">
      <View className="w-10 h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <View
          style={{ width: `${percent}%` }}
          className={`h-full rounded-full ${getColor()}`}
        />
      </View>
      <Text className={`text-[10px] font-mono font-bold ${getTextColor()}`}>
        {percent}%
      </Text>
    </View>
  );
};
