import React from "react";
import { Text, View } from "react-native";

interface DistributionSegment {
  label: string;
  percent: number;
  color: string;
}

interface DistributionBarProps {
  segments: DistributionSegment[];
}

export const DistributionBar: React.FC<DistributionBarProps> = ({
  segments,
}) => {
  return (
    <View className="w-full">
      <View className="h-3 w-full bg-slate-800 rounded-full overflow-hidden flex-row border border-slate-700/50">
        {segments.map((seg, idx) => (
          <View
            key={idx}
            style={{ width: `${Math.max(0, Math.min(100, seg.percent))}%` }}
            className={`h-full ${seg.color}`}
          />
        ))}
      </View>
      <View className="flex-row items-center gap-4 mt-2 flex-wrap">
        {segments.map((seg, idx) => (
          <View key={idx} className="flex-row items-center gap-1.5">
            <View className={`w-2 h-2 rounded-full ${seg.color}`} />
            <Text className="text-[11px] text-slate-400">
              {seg.label} ({seg.percent.toFixed(1)}%)
            </Text>
          </View>
        ))}
      </View>
    </View>
  );
};
