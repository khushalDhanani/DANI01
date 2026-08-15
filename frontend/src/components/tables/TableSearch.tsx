import React, { useEffect, useState } from "react";
import { Pressable, TextInput, View } from "react-native";
import { Search, X } from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";

interface TableSearchProps {
  value: string;
  onSearch: (value: string) => void;
  placeholder?: string;
}

export const TableSearch: React.FC<TableSearchProps> = ({
  value,
  onSearch,
  placeholder = "Search 970+ tables…",
}) => {
  const [internalValue, setInternalValue] = useState(value);

  // Sync internal state if external value changes (e.g. reset)
  useEffect(() => {
    setInternalValue(value);
  }, [value]);

  // Debounce search by 300ms
  useEffect(() => {
    const handler = setTimeout(() => {
      if (internalValue !== value) {
        onSearch(internalValue);
      }
    }, 300);

    return () => clearTimeout(handler);
  }, [internalValue, value, onSearch]);

  const handleClear = () => {
    setInternalValue("");
    onSearch("");
  };

  return (
    <View className="flex-row items-center bg-slate-900 border border-dark-border rounded-lg px-2.5 py-1.5 flex-1 min-w-[200px]">
      <Search size={14} color={THEME_COLORS.textMuted} />
      <TextInput
        value={internalValue}
        onChangeText={setInternalValue}
        placeholder={placeholder}
        placeholderTextColor={THEME_COLORS.textDark}
        className="flex-1 text-xs text-white px-2 py-0"
        autoCapitalize="none"
        autoCorrect={false}
      />
      {internalValue.length > 0 && (
        <Pressable
          onPress={handleClear}
          className="p-1 rounded hover:bg-slate-800 active:bg-slate-700"
          accessibilityLabel="Clear search"
          accessibilityRole="button"
        >
          <X size={12} color={THEME_COLORS.textMuted} />
        </Pressable>
      )}
    </View>
  );
};
