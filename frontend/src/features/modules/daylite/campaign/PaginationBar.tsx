import React from "react";
import { Pressable, Text, View } from "react-native";
import { ChevronLeft, ChevronRight } from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";

interface PaginationBarProps {
  page: number;
  totalPages: number;
  total: number;
  limit: number;
  label?: string;
  onPageChange: (page: number) => void;
}

export const PaginationBar: React.FC<PaginationBarProps> = ({
  page,
  totalPages,
  total,
  limit,
  label = "records",
  onPageChange,
}) => {
  if (totalPages <= 1) return null;

  const offset = (page - 1) * limit;

  return (
    <View className="flex-row items-center justify-between bg-dark-card border border-dark-border rounded-xl p-3 shadow-sm mt-2">
      <Pressable
        disabled={page <= 1}
        onPress={() => onPageChange(Math.max(1, page - 1))}
        className={`flex-row items-center gap-1 px-3 py-1.5 rounded-lg border transition-all ${
          page <= 1
            ? "bg-slate-900 border-slate-800 opacity-50"
            : "bg-slate-800 hover:bg-slate-700 border-slate-700"
        }`}
      >
        <ChevronLeft size={14} color={THEME_COLORS.textMuted} />
        <Text className="text-xs font-bold text-slate-300">Previous</Text>
      </Pressable>

      <Text className="text-xs font-mono text-slate-400">
        Showing {label} {offset + 1} – {Math.min(offset + limit, total)} of {total}
      </Text>

      <Pressable
        disabled={page >= totalPages}
        onPress={() => onPageChange(Math.min(totalPages, page + 1))}
        className={`flex-row items-center gap-1 px-3 py-1.5 rounded-lg border transition-all ${
          page >= totalPages
            ? "bg-slate-900 border-slate-800 opacity-50"
            : "bg-slate-800 hover:bg-slate-700 border-slate-700"
        }`}
      >
        <Text className="text-xs font-bold text-slate-300">Next</Text>
        <ChevronRight size={14} color={THEME_COLORS.textMuted} />
      </Pressable>
    </View>
  );
};
