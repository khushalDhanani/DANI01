import React from "react";
import { Text, View } from "react-native";

interface FieldRowProps {
  label: string;
  value: string | number | boolean | null | undefined;
  type?: "text" | "number" | "boolean" | "date" | "code" | "badge";
  badgeColor?: "blue" | "emerald" | "amber" | "purple" | "rose" | "indigo" | "slate";
  columnName?: string;
}

export const FieldRow: React.FC<FieldRowProps> = ({
  label,
  value,
  type = "text",
  badgeColor = "blue",
  columnName,
}) => {
  const isNull = value === null || value === undefined || value === "";

  const renderValue = () => {
    if (isNull) {
      return (
        <View className="bg-slate-900/80 px-1.5 py-0.2 rounded border border-slate-800 self-start">
          <Text className="text-[10px] text-slate-500 font-mono italic">NULL</Text>
        </View>
      );
    }

    if (type === "boolean" || typeof value === "boolean") {
      return (
        <View
          className={`px-2 py-0.5 rounded border self-start ${
            value
              ? "bg-emerald-950/60 border-emerald-800/60"
              : "bg-rose-950/60 border-rose-800/60"
          }`}
        >
          <Text
            className={`text-[10px] font-mono font-bold ${
              value ? "text-emerald-300" : "text-rose-300"
            }`}
          >
            {value ? "TRUE" : "FALSE"}
          </Text>
        </View>
      );
    }

    if (type === "date") {
      try {
        const d = new Date(String(value));
        const formatted = d.toLocaleString();
        return (
          <Text className="text-xs font-mono text-slate-300" numberOfLines={1}>
            {formatted}
          </Text>
        );
      } catch {
        return (
          <Text className="text-xs font-mono text-slate-300" numberOfLines={1}>
            {String(value)}
          </Text>
        );
      }
    }

    if (type === "badge") {
      const colorMap = {
        blue: "bg-blue-950/60 border-blue-800/60 text-blue-300",
        emerald: "bg-emerald-950/60 border-emerald-800/60 text-emerald-300",
        amber: "bg-amber-950/60 border-amber-800/60 text-amber-300",
        purple: "bg-purple-950/60 border-purple-800/60 text-purple-300",
        rose: "bg-rose-950/60 border-rose-800/60 text-rose-300",
        indigo: "bg-indigo-950/60 border-indigo-800/60 text-indigo-300",
        slate: "bg-slate-900 border-slate-700 text-slate-300",
      };
      return (
        <View className={`px-2 py-0.5 rounded border self-start ${colorMap[badgeColor]}`}>
          <Text className={`text-[10px] font-bold ${colorMap[badgeColor].split(" ").pop()}`}>
            {String(value)}
          </Text>
        </View>
      );
    }

    return (
      <Text
        className={`text-xs text-slate-200 ${type === "code" ? "font-mono" : "font-normal"}`}
        numberOfLines={2}
      >
        {String(value)}
      </Text>
    );
  };

  return (
    <View className="flex-col py-1.5 px-2.5 rounded-lg bg-dark-bg/40 border border-dark-border/40 hover:border-dark-border">
      <View className="flex-row items-center justify-between gap-1 mb-0.5">
        <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
          {label}
        </Text>
        {columnName ? (
          <Text className="text-[9px] text-slate-600 font-mono">{columnName}</Text>
        ) : null}
      </View>
      <View className="mt-0.5">{renderValue()}</View>
    </View>
  );
};
