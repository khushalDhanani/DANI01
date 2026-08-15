import React from "react";
import { Text, View } from "react-native";
import type { ColumnClassification } from "../../types/classification.types";
import { SensitivityBadge } from "../../components/ui/SensitivityBadge";

interface SemanticClassificationListProps {
  classifications: ColumnClassification[];
}

export const SemanticClassificationList: React.FC<
  SemanticClassificationListProps
> = ({ classifications }) => {
  return (
    <View className="divide-y divide-dark-border">
      {classifications.map((cls) => (
        <View
          key={cls.column_name}
          className="py-3.5 px-2 flex-row items-center justify-between gap-4"
        >
          <View className="flex-1">
            <Text className="text-sm font-bold text-white mb-1">
              {cls.column_name}
            </Text>
            <View className="flex-row items-center gap-2">
              <View className="bg-purple-950/80 px-2 py-0.5 rounded border border-purple-600/40">
                <Text className="text-[10px] font-bold text-purple-300">
                  {cls.semantic_type}
                </Text>
              </View>
              <Text className="text-xs text-slate-400">
                Confidence: {(cls.confidence * 100).toFixed(0)}%
              </Text>
            </View>
          </View>

          <SensitivityBadge sensitivity={cls.sensitivity} />
        </View>
      ))}
    </View>
  );
};
