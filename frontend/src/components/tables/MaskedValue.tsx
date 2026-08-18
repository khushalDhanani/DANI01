import React from "react";
import { Text, View } from "react-native";
import { Lock } from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import { formatDate, formatDateTime } from "@/utils/formatters";

interface MaskedValueProps {
  value: unknown;
  isMasked?: boolean;
}

export const MaskedValue: React.FC<MaskedValueProps> = ({
  value,
  isMasked = false,
}) => {
  if (isMasked) {
    return (
      <View className="flex-row items-center gap-1 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
        <Lock size={10} color={THEME_COLORS.textMuted} />
        <Text className="text-xs font-mono text-slate-500 tracking-widest">
          ••••••••
        </Text>
      </View>
    );
  }

  if (value === null || value === undefined) {
    return (
      <Text className="text-xs font-mono italic text-amber-500/80">
        NULL
      </Text>
    );
  }

  if (typeof value === "boolean") {
    return (
      <View
        className={`px-1.5 py-0.2 rounded ${
          value ? "bg-emerald-950/70" : "bg-rose-950/70"
        }`}
      >
        <Text
          className={`text-[10px] font-mono font-bold ${
            value ? "text-emerald-400" : "text-rose-400"
          }`}
        >
          {value ? "TRUE" : "FALSE"}
        </Text>
      </View>
    );
  }

  const strVal = String(value);
  if (/^\d{4}-\d{2}-\d{2}(T|\s|$)/.test(strVal)) {
    const formatted = strVal.includes("T") || strVal.includes(":")
      ? formatDateTime(strVal)
      : formatDate(strVal);
    return (
      <Text className="text-xs font-mono text-slate-200" numberOfLines={1}>
        {formatted}
      </Text>
    );
  }

  return (
    <Text className="text-xs font-mono text-slate-200" numberOfLines={1}>
      {strVal}
    </Text>
  );
};
