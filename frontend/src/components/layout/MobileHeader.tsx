import React from "react";
import { Pressable, Text, View } from "react-native";
import { Menu, Database } from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";

interface MobileHeaderProps {
  onMenuPress: () => void;
}

/**
 * Compact mobile header (< lg breakpoint).
 */
export const MobileHeader: React.FC<MobileHeaderProps> = ({ onMenuPress }) => {
  return (
    <View className="bg-dark-card border-b border-dark-border px-3 py-2 flex-row items-center justify-between z-10">
      {/* Brand */}
      <View className="flex-row items-center gap-2">
        <View className="w-7 h-7 rounded-lg bg-blue-600 items-center justify-center">
          <Database size={15} color={THEME_COLORS.onPrimary} />
        </View>
        <View>
          <Text className="text-xs font-black text-white tracking-tight">
            AIRIS <Text className="text-blue-400">INSIGHTS</Text>
          </Text>
          <Text className="text-[8px] uppercase font-bold text-slate-500 tracking-wider">
            DB Intelligence
          </Text>
        </View>
      </View>

      {/* Hamburger */}
      <Pressable
        onPress={onMenuPress}
        className="p-1.5 rounded-lg active:bg-slate-800"
        accessibilityLabel="Open navigation menu"
        accessibilityRole="button"
      >
        <Menu size={18} color={THEME_COLORS.textMuted} />
      </Pressable>
    </View>
  );
};
