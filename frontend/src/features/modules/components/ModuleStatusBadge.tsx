import React from "react";
import { Text, View } from "react-native";
import type { ModuleValidationStatus } from "@/types/modules.types";

interface ModuleStatusBadgeProps {
  status?: ModuleValidationStatus | "ENABLED" | "DISABLED" | string;
  size?: "sm" | "md";
}

export const ModuleStatusBadge: React.FC<ModuleStatusBadgeProps> = ({
  status = "READY",
  size = "md",
}) => {
  const rawStatus = typeof status === "object" ? status.status : status;
  const normalized = (rawStatus || "READY").toUpperCase();

  let bgClass = "bg-slate-800 border-slate-700";
  let textClass = "text-slate-400";
  let dotClass = "bg-slate-500";
  let label = normalized;

  switch (normalized) {
    case "READY":
    case "ENABLED":
    case "COMPLETED":
      bgClass = "bg-emerald-950/60 border-emerald-800/60";
      textClass = "text-emerald-300";
      dotClass = "bg-emerald-400";
      label = "Ready";
      break;
    case "DEGRADED":
      bgClass = "bg-amber-950/60 border-amber-800/60";
      textClass = "text-amber-300";
      dotClass = "bg-amber-400";
      label = "Degraded";
      break;
    case "INVALID":
    case "FAILED":
      bgClass = "bg-rose-950/60 border-rose-800/60";
      textClass = "text-rose-300";
      dotClass = "bg-rose-400";
      label = "Invalid";
      break;
    case "DISABLED":
      bgClass = "bg-slate-900 border-slate-800";
      textClass = "text-slate-500";
      dotClass = "bg-slate-600";
      label = "Disabled";
      break;
  }

  const isSmall = size === "sm";

  return (
    <View
      className={`flex-row items-center gap-1.5 rounded-md border ${bgClass} ${
        isSmall ? "px-2 py-0.5" : "px-2.5 py-1"
      }`}
    >
      <View className={`rounded-full ${dotClass} ${isSmall ? "w-1.5 h-1.5" : "w-2 h-2"}`} />
      <Text
        className={`font-semibold tracking-wide uppercase ${textClass} ${
          isSmall ? "text-[10px]" : "text-xs"
        }`}
      >
        {label}
      </Text>
    </View>
  );
};
