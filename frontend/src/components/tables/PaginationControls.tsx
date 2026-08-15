import React from "react";
import { Pressable, Text, View } from "react-native";
import { ChevronLeft, ChevronRight } from "lucide-react-native";
import { formatNumber } from "@/utils/formatters";
import { THEME_COLORS } from "@/constants/theme";

interface PaginationControlsProps {
  page: number;
  limit: number;
  total: number;
  onPageChange: (newPage: number) => void;
  isFetching?: boolean;
}

export const PaginationControls: React.FC<PaginationControlsProps> = ({
  page,
  limit,
  total,
  onPageChange,
  isFetching = false,
}) => {
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const currentPage = page + 1;
  const startItem = total === 0 ? 0 : page * limit + 1;
  const endItem = Math.min((page + 1) * limit, total);

  const canGoPrevious = page > 0;
  const canGoNext = page < totalPages - 1;

  return (
    <View className="flex-row items-center justify-between py-2 border-t border-dark-border mt-2">
      {/* Range Info */}
      <Text className="text-xs text-slate-400">
        Showing <Text className="font-mono font-bold text-white">{startItem}–{endItem}</Text> of{" "}
        <Text className="font-mono font-bold text-white">{formatNumber(total)}</Text> tables
        {isFetching && <Text className="text-blue-400 text-[11px] ml-1"> (updating…)</Text>}
      </Text>

      {/* Page Navigation Controls */}
      <View className="flex-row items-center gap-2">
        <Text className="text-xs text-slate-500 mr-1 font-mono">
          Page {currentPage} of {totalPages}
        </Text>

        <Pressable
          onPress={() => canGoPrevious && onPageChange(page - 1)}
          disabled={!canGoPrevious}
          className={`p-1.5 rounded-lg border flex-row items-center ${
            canGoPrevious
              ? "bg-slate-900 border-dark-border active:bg-slate-800"
              : "opacity-40 border-transparent"
          }`}
          accessibilityLabel="Previous page"
          accessibilityRole="button"
        >
          <ChevronLeft size={14} color={canGoPrevious ? THEME_COLORS.onPrimary : THEME_COLORS.textDark} />
        </Pressable>

        <Pressable
          onPress={() => canGoNext && onPageChange(page + 1)}
          disabled={!canGoNext}
          className={`p-1.5 rounded-lg border flex-row items-center ${
            canGoNext
              ? "bg-slate-900 border-dark-border active:bg-slate-800"
              : "opacity-40 border-transparent"
          }`}
          accessibilityLabel="Next page"
          accessibilityRole="button"
        >
          <ChevronRight size={14} color={canGoNext ? THEME_COLORS.onPrimary : THEME_COLORS.textDark} />
        </Pressable>
      </View>
    </View>
  );
};
