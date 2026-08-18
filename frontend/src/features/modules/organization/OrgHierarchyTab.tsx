import React, { useState } from "react";
import { ActivityIndicator, Text, TextInput, TouchableOpacity, View } from "react-native";
import {
  Building2,
  ChevronDown,
  ChevronRight,
  Factory,
  GitBranch,
  MapPin,
  Search,
  Users,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import type { OrgHierarchyNode, OrgHierarchyResponse } from "@/types/organization.types";

interface OrgHierarchyTabProps {
  hierarchy?: OrgHierarchyResponse;
  isLoading: boolean;
}

export const OrgHierarchyTab: React.FC<OrgHierarchyTabProps> = ({
  hierarchy,
  isLoading,
}) => {
  const [search, setSearch] = useState("");
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({
    "1": true, // Expand CompID 1 by default
    "1_1": true, // Expand Catalyst Site 1 by default
  });

  if (isLoading || !hierarchy) {
    return (
      <View className="py-12 items-center justify-center">
        <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
        <Text className="text-sm text-slate-400 mt-3 font-medium">Building Organization Hierarchy Tree...</Text>
      </View>
    );
  }

  const toggleNode = (nodeKey: string) => {
    setExpandedNodes((prev) => ({
      ...prev,
      [nodeKey]: !prev[nodeKey],
    }));
  };

  const expandAll = () => {
    const allExpanded: Record<string, boolean> = {};
    const traverse = (node: OrgHierarchyNode, parentKey: string = "") => {
      const key = parentKey ? `${parentKey}_${node.id}` : `${node.id}`;
      allExpanded[key] = true;
      node.children?.forEach((c) => traverse(c, key));
    };
    hierarchy.companies.forEach((c) => traverse(c));
    setExpandedNodes(allExpanded);
  };

  const collapseAll = () => {
    setExpandedNodes({});
  };

  const renderLevelIcon = (level: string) => {
    switch (level) {
      case "COMPANY":
        return <Building2 size={13} color="#60a5fa" />;
      case "LOCATION":
        return <MapPin size={13} color="#34d399" />;
      case "DEPARTMENT":
        return <Factory size={13} color="#22d3ee" />;
      case "DESIGNATION":
        return <Users size={12} color="#fbbf24" />;
      default:
        return <GitBranch size={12} color="#94a3b8" />;
    }
  };

  const renderNode = (
    node: OrgHierarchyNode,
    parentKey: string = "",
    depth: number = 0
  ) => {
    const key = parentKey ? `${parentKey}_${node.id}` : `${node.id}`;
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = Boolean(expandedNodes[key]) || Boolean(search);

    // If search is present, check match on this node or any descendants
    if (search) {
      const matchesSelf =
        node.name.toLowerCase().includes(search.toLowerCase()) ||
        (node.code && node.code.toLowerCase().includes(search.toLowerCase())) ||
        (node.head_name && node.head_name.toLowerCase().includes(search.toLowerCase()));

      const hasMatchingChild = (n: OrgHierarchyNode): boolean =>
        (n.name.toLowerCase().includes(search.toLowerCase()) ||
          (n.code && n.code.toLowerCase().includes(search.toLowerCase())) ||
          (n.head_name && n.head_name.toLowerCase().includes(search.toLowerCase()))) ||
        Boolean(n.children?.some(hasMatchingChild));

      if (!matchesSelf && !hasMatchingChild(node)) {
        return null;
      }
    }

    const paddingLeft = Math.min(depth * 16, 64);

    return (
      <View key={key} className="gap-1">
        <TouchableOpacity
          onPress={() => hasChildren && toggleNode(key)}
          activeOpacity={hasChildren ? 0.7 : 1}
          className={`flex-row items-center justify-between p-2.5 rounded-lg border ${
            depth === 0
              ? "bg-dark-card border-blue-500/30"
              : depth === 1
              ? "bg-dark-bg border-dark-border"
              : "bg-slate-950/60 border-dark-border/60"
          }`}
          style={{ marginLeft: paddingLeft }}
        >
          <View className="flex-row items-center gap-2 flex-1">
            {hasChildren ? (
              <View className="p-0.5">
                {isExpanded ? (
                  <ChevronDown size={14} color="#94a3b8" />
                ) : (
                  <ChevronRight size={14} color="#94a3b8" />
                )}
              </View>
            ) : (
              <View className="w-3.5" />
            )}

            {renderLevelIcon(node.level)}

            <View className="flex-1 flex-row flex-wrap items-center gap-1.5">
              <Text
                className={`font-mono text-xs ${
                  depth === 0 ? "font-bold text-white text-sm" : "font-medium text-slate-200"
                }`}
              >
                {node.name}
              </Text>

              {node.code && (
                <View className="bg-slate-800 px-1.5 py-0.2 rounded">
                  <Text className="text-[9px] font-mono text-slate-400">{node.code}</Text>
                </View>
              )}

              {node.head_name && (
                <View className="bg-emerald-950/50 border border-emerald-800/40 px-1.5 py-0.2 rounded flex-row items-center gap-1">
                  <Text className="text-[9px] text-emerald-400 font-medium">
                    Leader: {node.head_name}
                  </Text>
                  {node.head_code && (
                    <Text className="text-[8px] font-mono text-emerald-500">({node.head_code})</Text>
                  )}
                </View>
              )}
            </View>
          </View>

          <View className="flex-row items-center gap-2">
            <View className="bg-dark-card border border-dark-border px-2 py-0.5 rounded">
              <Text className="text-[10px] font-mono font-bold text-blue-400">
                {node.headcount.toLocaleString()} {node.headcount === 1 ? "staff" : "staff"}
              </Text>
            </View>
            <View className="bg-slate-900 px-1.5 py-0.5 rounded">
              <Text className="text-[8px] uppercase font-bold text-slate-400">{node.level}</Text>
            </View>
          </View>
        </TouchableOpacity>

        {hasChildren && isExpanded && (
          <View className="gap-1 mt-0.5">
            {node.children.map((child) => renderNode(child, key, depth + 1))}
          </View>
        )}
      </View>
    );
  };

  return (
    <View className="gap-4">
      {/* ── Hierarchy Tree Header & Controls ────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4">
        <View className="flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
          <View className="flex-1">
            <View className="flex-row items-center gap-2 mb-1">
              <GitBranch size={15} color={THEME_COLORS.primaryIcon} />
              <Text className="text-xs font-bold text-white uppercase tracking-wider">
                Multi-Tier Corporate Relationship Map
              </Text>
            </View>
            <Text className="text-[11px] text-slate-400">
              Traverse Company → Location → Department → Designation mappings with live employee headcounts and leadership linkages.
            </Text>
          </View>

          <View className="flex-row items-center gap-2 self-start md:self-auto">
            <TouchableOpacity
              onPress={expandAll}
              className="bg-dark-bg border border-dark-border px-3 py-1.5 rounded-lg active:bg-slate-800"
            >
              <Text className="text-[11px] font-bold text-slate-300">Expand All</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={collapseAll}
              className="bg-dark-bg border border-dark-border px-3 py-1.5 rounded-lg active:bg-slate-800"
            >
              <Text className="text-[11px] font-bold text-slate-300">Collapse All</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Search Bar */}
        <View className="flex-row items-center bg-dark-bg border border-dark-border rounded-lg px-3 py-2">
          <Search size={14} color="#64748b" />
          <TextInput
            value={search}
            onChangeText={setSearch}
            placeholder="Search hierarchy by entity name, short code, or leader name..."
            placeholderTextColor="#64748b"
            className="flex-1 text-xs text-white ml-2"
          />
        </View>
      </View>

      {/* ── Tree View Nodes Container ───────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-2">
        {hierarchy.companies.map((company) => renderNode(company))}
      </View>
    </View>
  );
};
