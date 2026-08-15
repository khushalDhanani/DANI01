import React from "react";
import { Text, View } from "react-native";
import { ShieldCheck, Sparkles } from "lucide-react-native";
import type { ColumnClassification } from "@/types/classification.types";
import { DistributionBar, type DistributionSegment } from "@/components/visualizations/DistributionBar";
import { THEME_COLORS } from "@/constants/theme";

interface ClassificationSummaryCardProps {
  classifications: ColumnClassification[];
}

export const ClassificationSummaryCard: React.FC<ClassificationSummaryCardProps> = ({
  classifications,
}) => {
  const total = classifications.length;
  if (total === 0) return null;

  // 1. Group by Sensitivity
  const sensitivityCounts: Record<string, number> = {};
  classifications.forEach((c) => {
    const s = c.sensitivity?.toUpperCase() || "INTERNAL";
    sensitivityCounts[s] = (sensitivityCounts[s] || 0) + 1;
  });

  const getSensitivityColor = (sens: string) => {
    switch (sens) {
      case "PII":
        return { color: "bg-rose-500", text: "text-rose-400" };
      case "CONFIDENTIAL":
      case "RESTRICTED":
      case "SENSITIVE":
        return { color: "bg-purple-500", text: "text-purple-400" };
      case "PUBLIC":
        return { color: "bg-emerald-500", text: "text-emerald-400" };
      case "INTERNAL":
      default:
        return { color: "bg-blue-500", text: "text-blue-400" };
    }
  };

  const sensitivitySegments: DistributionSegment[] = Object.entries(
    sensitivityCounts
  ).map(([key, count]) => {
    const style = getSensitivityColor(key);
    return {
      label: key,
      count,
      percent: (count / total) * 100,
      color: style.color,
      textColor: style.text,
    };
  });

  // 2. Group by Semantic Type (Top 4 + Others)
  const semanticCounts: Record<string, number> = {};
  let totalConfidence = 0;
  classifications.forEach((c) => {
    const st = c.semantic_type?.toUpperCase() || "UNKNOWN";
    semanticCounts[st] = (semanticCounts[st] || 0) + 1;
    totalConfidence += c.confidence || 0;
  });

  const avgConfidence = Math.round((totalConfidence / total) * 100);

  const semanticPalette = [
    { color: "bg-amber-400", text: "text-amber-400" },
    { color: "bg-cyan-400", text: "text-cyan-400" },
    { color: "bg-emerald-400", text: "text-emerald-400" },
    { color: "bg-purple-400", text: "text-purple-400" },
    { color: "bg-blue-400", text: "text-blue-400" },
  ];

  const sortedSemantics = Object.entries(semanticCounts).sort(
    (a, b) => b[1] - a[1]
  );
  const semanticSegments: DistributionSegment[] = sortedSemantics
    .slice(0, 4)
    .map(([key, count], idx) => {
      const p = semanticPalette[idx % semanticPalette.length];
      return {
        label: key,
        count,
        percent: (count / total) * 100,
        color: p.color,
        textColor: p.text,
      };
    });

  const otherCount = sortedSemantics
    .slice(4)
    .reduce((acc, [, c]) => acc + c, 0);
  if (otherCount > 0) {
    semanticSegments.push({
      label: "OTHER",
      count: otherCount,
      percent: (otherCount / total) * 100,
      color: "bg-slate-500",
      textColor: "text-slate-400",
    });
  }

  return (
    <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-4">
      {/* Header with Average Confidence */}
      <View className="flex-row items-center justify-between flex-wrap gap-2">
        <View className="flex-row items-center gap-2">
          <Sparkles size={15} color={THEME_COLORS.accentIcon} />
          <Text className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Semantic Classification Intelligence
          </Text>
        </View>

        <View className="flex-row items-center gap-1.5 bg-slate-900 px-2.5 py-1 rounded-md border border-slate-800">
          <ShieldCheck size={12} color={THEME_COLORS.successIcon} />
          <Text className="text-[10px] text-slate-400 font-medium">
            Avg Confidence:{" "}
            <Text className="font-mono font-bold text-emerald-400">
              {avgConfidence}%
            </Text>
          </Text>
        </View>
      </View>

      {/* ── 1. Sensitivity Level Distribution ────────────── */}
      <View className="gap-1.5">
        <Text className="text-[10px] uppercase font-bold text-slate-400">
          Sensitivity Level Distribution
        </Text>
        <DistributionBar segments={sensitivitySegments} totalCount={total} totalLabel="Columns" />
      </View>

      {/* ── 2. Semantic Type Proportions ─────────────────── */}
      <View className="gap-1.5 pt-2 border-t border-slate-800/80">
        <Text className="text-[10px] uppercase font-bold text-slate-400">
          Semantic Categories
        </Text>
        <DistributionBar segments={semanticSegments} totalCount={total} totalLabel="Categorized" />
      </View>
    </View>
  );
};
