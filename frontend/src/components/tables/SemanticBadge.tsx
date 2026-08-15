import React from "react";
import { Text, View } from "react-native";

interface SemanticBadgeProps {
  type: string;
}

export const SemanticBadge: React.FC<SemanticBadgeProps> = ({ type }) => {
  const normalized = type.toUpperCase();

  const getColors = () => {
    switch (normalized) {
      case "EMAIL":
      case "PHONE":
      case "SSN":
      case "IP_ADDRESS":
        return { bg: "bg-rose-950/70", border: "border-rose-600/40", text: "text-rose-400" };
      case "NAME":
      case "FIRST_NAME":
      case "LAST_NAME":
      case "PERSON":
        return { bg: "bg-purple-950/70", border: "border-purple-600/40", text: "text-purple-400" };
      case "STREET":
      case "CITY":
      case "STATE":
      case "COUNTRY":
      case "POSTAL_CODE":
      case "ADDRESS":
        return { bg: "bg-blue-950/70", border: "border-blue-600/40", text: "text-blue-400" };
      case "IDENTIFIER":
      case "ID":
      case "UUID":
        return { bg: "bg-amber-950/70", border: "border-amber-600/40", text: "text-amber-400" };
      case "DATE":
      case "DATETIME":
      case "TIMESTAMP":
        return { bg: "bg-cyan-950/70", border: "border-cyan-600/40", text: "text-cyan-400" };
      case "CURRENCY":
      case "AMOUNT":
      case "PRICE":
        return { bg: "bg-emerald-950/70", border: "border-emerald-600/40", text: "text-emerald-400" };
      case "FLAG":
      case "BOOLEAN":
      case "STATUS":
        return { bg: "bg-indigo-950/70", border: "border-indigo-600/40", text: "text-indigo-400" };
      default:
        return { bg: "bg-slate-900", border: "border-slate-800", text: "text-slate-300" };
    }
  };

  const colors = getColors();

  return (
    <View
      className={`px-1.5 py-0.5 rounded border self-start ${colors.bg} ${colors.border}`}
    >
      <Text
        className={`text-[9px] font-mono font-bold uppercase tracking-wide ${colors.text}`}
      >
        {normalized}
      </Text>
    </View>
  );
};
