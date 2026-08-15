import React from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import type { SchemaInfo } from "@/types/database.types";

interface SchemaFilterProps {
  schemas?: SchemaInfo[];
  selectedSchema: string | null;
  onSelectSchema: (schema: string | null) => void;
  totalTables?: number;
}

export const SchemaFilter: React.FC<SchemaFilterProps> = ({
  schemas,
  selectedSchema,
  onSelectSchema,
  totalTables,
}) => {
  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      contentContainerStyle={{ gap: 6, alignItems: "center" }}
      style={{ flexGrow: 0 }}
    >
      {/* All Schemas Option */}
      <Pressable
        onPress={() => onSelectSchema(null)}
        className={`px-2.5 py-1 rounded-lg border flex-row items-center gap-1.5 ${
          selectedSchema === null
            ? "bg-blue-600 border-blue-500"
            : "bg-slate-900/80 border-dark-border active:bg-slate-800"
        }`}
      >
        <Text
          className={`text-xs font-semibold ${
            selectedSchema === null ? "text-white" : "text-slate-300"
          }`}
        >
          All
        </Text>
        {totalTables !== undefined && (
          <View
            className={`px-1.5 py-0.2 rounded text-[10px] ${
              selectedSchema === null
                ? "bg-blue-700/80"
                : "bg-slate-800"
            }`}
          >
            <Text
              className={`text-[10px] font-mono ${
                selectedSchema === null ? "text-blue-100" : "text-slate-400"
              }`}
            >
              {totalTables}
            </Text>
          </View>
        )}
      </Pressable>

      {/* Individual Schemas */}
      {schemas?.map((s) => {
        const isSelected = selectedSchema === s.name;
        return (
          <Pressable
            key={s.name}
            onPress={() => onSelectSchema(s.name)}
            className={`px-2.5 py-1 rounded-lg border flex-row items-center gap-1.5 ${
              isSelected
                ? "bg-blue-600 border-blue-500"
                : "bg-slate-900/80 border-dark-border active:bg-slate-800"
            }`}
          >
            <Text
              className={`text-xs font-semibold ${
                isSelected ? "text-white" : "text-slate-300"
              }`}
            >
              {s.name}
            </Text>
            <View
              className={`px-1.5 py-0.2 rounded ${
                isSelected ? "bg-blue-700/80" : "bg-slate-800"
              }`}
            >
              <Text
                className={`text-[10px] font-mono ${
                  isSelected ? "text-blue-100" : "text-slate-400"
                }`}
              >
                {s.table_count}
              </Text>
            </View>
          </Pressable>
        );
      })}
    </ScrollView>
  );
};
