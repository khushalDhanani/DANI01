import React from "react";
import { Text, View } from "react-native";
import type { AnalysisRunStatus } from "@/types/analysis.types";

interface StatusBadgeProps {
  status: AnalysisRunStatus | "COMPLETED" | "SKIPPED" | "FAILED" | string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const getColors = () => {
    switch (status) {
      case "COMPLETED":
        return { bg: "bg-emerald-950/60", border: "border-emerald-500/40", text: "text-emerald-400" };
      case "RUNNING":
        return { bg: "bg-blue-950/60", border: "border-blue-500/40", text: "text-blue-400" };
      case "QUEUED":
        return { bg: "bg-amber-950/60", border: "border-amber-500/40", text: "text-amber-400" };
      case "COMPLETED_WITH_ERRORS":
        return { bg: "bg-orange-950/60", border: "border-orange-500/40", text: "text-orange-400" };
      case "FAILED":
        return { bg: "bg-rose-950/60", border: "border-rose-500/40", text: "text-rose-400" };
      case "SKIPPED":
        return { bg: "bg-slate-800/60", border: "border-slate-600/40", text: "text-slate-400" };
      case "CANCELLING":
      case "CANCELLED":
        return { bg: "bg-zinc-800/60", border: "border-zinc-500/40", text: "text-zinc-400" };
      default:
        return { bg: "bg-slate-800", border: "border-slate-700", text: "text-slate-300" };
    }
  };

  const colors = getColors();

  return (
    <View
      className={`px-2.5 py-1 rounded-full border flex-row items-center gap-1.5 ${colors.bg} ${colors.border}`}
    >
      <View
        className={`w-1.5 h-1.5 rounded-full ${
          status === "RUNNING" ? "bg-blue-400 animate-pulse" : colors.text.replace("text-", "bg-")
        }`}
      />
      <Text className={`text-[11px] font-bold tracking-wider uppercase ${colors.text}`}>
        {status.replace(/_/g, " ")}
      </Text>
    </View>
  );
};
