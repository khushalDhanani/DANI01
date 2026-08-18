import React, { useState } from "react";
import { ActivityIndicator, Text, TouchableOpacity, View } from "react-native";
import {
  Award,
  ChevronDown,
  ChevronRight,
  Crown,
  Network,
  ShieldCheck,
  UserCheck,
  Users,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import type { OrgReportingNode, OrgReportingTreeResponse } from "@/types/organization.types";

interface OrgReportingTabProps {
  reporting?: OrgReportingTreeResponse;
  isLoading: boolean;
}

export const OrgReportingTab: React.FC<OrgReportingTabProps> = ({
  reporting,
  isLoading,
}) => {
  const [expandedNodes, setExpandedNodes] = useState<Record<number, boolean>>({
    170: true, // Expand Managing Director by default
  });

  if (isLoading || !reporting) {
    return (
      <View className="py-12 items-center justify-center">
        <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
        <Text className="text-sm text-slate-400 mt-3 font-medium">Constructing Executive Reporting Lines...</Text>
      </View>
    );
  }

  const toggleNode = (empId: number) => {
    setExpandedNodes((prev) => ({
      ...prev,
      [empId]: !prev[empId],
    }));
  };

  const getRoleBadge = (roleType: string) => {
    switch (roleType) {
      case "EXECUTIVE":
        return (
          <View className="flex-row items-center gap-1 bg-amber-950/70 border border-amber-500/40 px-2 py-0.5 rounded">
            <Crown size={10} color="#fbbf24" />
            <Text className="text-[9px] font-bold text-amber-400">EXECUTIVE</Text>
          </View>
        );
      case "DIRECTOR":
        return (
          <View className="flex-row items-center gap-1 bg-purple-950/70 border border-purple-500/40 px-2 py-0.5 rounded">
            <Award size={10} color="#c084fc" />
            <Text className="text-[9px] font-bold text-purple-400">DIRECTOR</Text>
          </View>
        );
      case "HOD":
        return (
          <View className="flex-row items-center gap-1 bg-blue-950/70 border border-blue-500/40 px-2 py-0.5 rounded">
            <ShieldCheck size={10} color="#60a5fa" />
            <Text className="text-[9px] font-bold text-blue-400">HOD / LEAD</Text>
          </View>
        );
      default:
        return (
          <View className="bg-slate-800 px-1.5 py-0.5 rounded">
            <Text className="text-[9px] text-slate-400">STAFF</Text>
          </View>
        );
    }
  };

  const renderReportingNode = (node: OrgReportingNode, depth: number = 0) => {
    const hasSubordinates = node.subordinates && node.subordinates.length > 0;
    const isExpanded = Boolean(expandedNodes[node.emp_id]);
    const paddingLeft = Math.min(depth * 20, 80);

    return (
      <View key={node.emp_id} className="gap-1">
        <TouchableOpacity
          onPress={() => hasSubordinates && toggleNode(node.emp_id)}
          activeOpacity={hasSubordinates ? 0.7 : 1}
          className={`flex-row items-center justify-between p-3 rounded-xl border ${
            depth === 0
              ? "bg-gradient-to-r from-amber-950/20 via-dark-card to-dark-card border-amber-500/30 shadow-sm"
              : depth === 1
              ? "bg-dark-bg border-purple-500/20"
              : "bg-slate-950/60 border-dark-border"
          }`}
          style={{ marginLeft: paddingLeft }}
        >
          <View className="flex-row items-center gap-2.5 flex-1">
            {hasSubordinates ? (
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

            <View className="flex-1">
              <View className="flex-row items-center gap-2 mb-0.5">
                <Text
                  className={`text-xs font-mono ${
                    depth === 0 ? "font-bold text-white text-sm" : "font-semibold text-slate-200"
                  }`}
                >
                  {node.full_name}
                </Text>
                {node.emp_code && (
                  <View className="bg-slate-900 border border-slate-700 px-1.5 py-0.2 rounded">
                    <Text className="text-[9px] font-mono text-slate-400">#{node.emp_code}</Text>
                  </View>
                )}
                {getRoleBadge(node.role_type)}
              </View>

              <View className="flex-row items-center gap-2">
                <Text className="text-[11px] text-slate-400 font-medium">
                  {node.designation || "No Designation"}
                </Text>
                {node.department && (
                  <Text className="text-[11px] text-slate-500">• {node.department}</Text>
                )}
                {node.location && (
                  <Text className="text-[10px] text-slate-600">[{node.location}]</Text>
                )}
              </View>
            </View>
          </View>

          {node.direct_reports_count > 0 && (
            <View className="bg-dark-bg border border-dark-border px-2.5 py-1 rounded-lg flex-row items-center gap-1.5">
              <Users size={12} color="#60a5fa" />
              <Text className="text-[11px] font-mono font-bold text-blue-400">
                {node.direct_reports_count} {node.direct_reports_count === 1 ? "report" : "reports"}
              </Text>
            </View>
          )}
        </TouchableOpacity>

        {hasSubordinates && isExpanded && (
          <View className="gap-1 mt-0.5">
            {node.subordinates.map((sub) => renderReportingNode(sub, depth + 1))}
          </View>
        )}
      </View>
    );
  };

  return (
    <View className="gap-4">
      {/* ── Reporting Summary Header ───────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 flex-col sm:flex-row sm:items-center justify-between gap-3">
        <View className="flex-1">
          <View className="flex-row items-center gap-2 mb-1">
            <Network size={15} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-bold text-white uppercase tracking-wider">
              Executive Leadership &amp; Reporting Lines
            </Text>
          </View>
          <Text className="text-[11px] text-slate-400">
            Hierarchical chain of command discovered via functional manager assignments in <Text className="font-mono text-slate-300">EmployeeReportingDet</Text>.
          </Text>
        </View>

        <View className="bg-dark-bg border border-dark-border px-3 py-2 rounded-lg flex-row items-center gap-2">
          <UserCheck size={14} color={THEME_COLORS.success} />
          <View>
            <Text className="text-[9px] uppercase font-bold text-slate-400">Assigned Managers</Text>
            <Text className="text-xs font-mono font-bold text-emerald-400">
              {reporting.total_assigned_managers} Active Leads
            </Text>
          </View>
        </View>
      </View>

      {/* ── Tree View Container ─────────────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-2">
        {reporting.roots.map((root) => renderReportingNode(root))}
      </View>
    </View>
  );
};
