import React, { useState } from "react";
import {
  ActivityIndicator,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import {
  Award,
  Building2,
  ChevronLeft,
  ChevronRight,
  Download,
  Factory,
  Layers,
  MapPin,
  Search,
  Users,
} from "lucide-react-native";
import { downloadOrgUnitsExport } from "@/api/organization.api";
import { THEME_COLORS } from "@/constants/theme";
import { useOrgUnits } from "@/hooks/useOrganization";
import type { OrgUnitType } from "@/types/organization.types";

const UNIT_TABS: { label: string; value: OrgUnitType | "ALL" }[] = [
  { label: "All Units", value: "ALL" },
  { label: "Companies", value: "COMPANY" },
  { label: "Locations", value: "LOCATION" },
  { label: "Main Divisions", value: "MAIN_DEPT" },
  { label: "Departments", value: "DEPARTMENT" },
  { label: "Designations", value: "DESIGNATION" },
  { label: "Grades", value: "GRADE" },
];

export const OrgUnitsCatalogTab: React.FC = () => {
  const [selectedType, setSelectedType] = useState<OrgUnitType | "ALL">("ALL");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [isExporting, setIsExporting] = useState(false);
  const limit = 25;

  const currentUnitType = selectedType === "ALL" ? undefined : selectedType;

  const { data: unitsData, isLoading } = useOrgUnits(
    currentUnitType,
    search || undefined,
    undefined,
    limit,
    page * limit
  );

  const handleExport = async () => {
    try {
      setIsExporting(true);
      await downloadOrgUnitsExport(currentUnitType, search || undefined, "csv");
    } catch (err) {
      console.error("Export error:", err);
    } finally {
      setIsExporting(false);
    }
  };

  const total = unitsData?.total || 0;
  const totalPages = Math.ceil(total / limit);

  const getUnitIcon = (type: OrgUnitType) => {
    switch (type) {
      case "COMPANY":
        return <Building2 size={13} color="#60a5fa" />;
      case "LOCATION":
        return <MapPin size={13} color="#34d399" />;
      case "MAIN_DEPT":
        return <Layers size={13} color="#c084fc" />;
      case "DEPARTMENT":
        return <Factory size={13} color="#22d3ee" />;
      case "DESIGNATION":
        return <Users size={13} color="#fbbf24" />;
      case "GRADE":
        return <Award size={13} color="#f43f5e" />;
      default:
        return <Building2 size={13} color="#94a3b8" />;
    }
  };

  return (
    <View className="gap-4">
      {/* ── Filter Bar & Actions ────────────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3">
        {/* Type Filter Pills */}
        <View className="flex-row flex-wrap gap-2">
          {UNIT_TABS.map((tab) => (
            <TouchableOpacity
              key={tab.value}
              onPress={() => {
                setSelectedType(tab.value);
                setPage(0);
              }}
              className={`px-3 py-1.5 rounded-lg border ${
                selectedType === tab.value
                  ? "bg-blue-600 border-blue-400"
                  : "bg-dark-bg border-dark-border"
              }`}
            >
              <Text
                className={`text-xs font-bold ${
                  selectedType === tab.value ? "text-white" : "text-slate-400"
                }`}
              >
                {tab.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Search & Export */}
        <View className="flex-col sm:flex-row gap-2">
          <View className="flex-1 flex-row items-center bg-dark-bg border border-dark-border rounded-lg px-3 py-2">
            <Search size={14} color="#64748b" />
            <TextInput
              value={search}
              onChangeText={(txt) => {
                setSearch(txt);
                setPage(0);
              }}
              placeholder="Search by unit name, code, or parent organization..."
              placeholderTextColor="#64748b"
              className="flex-1 text-xs text-white ml-2"
            />
          </View>

          <TouchableOpacity
            onPress={handleExport}
            disabled={isExporting}
            className="bg-dark-bg border border-dark-border px-3.5 py-2 rounded-lg flex-row items-center justify-center gap-1.5"
          >
            <Download size={14} color="#94a3b8" />
            <Text className="text-xs font-bold text-slate-300">
              {isExporting ? "Exporting..." : "Export CSV"}
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* ── Unified Units Data Grid ─────────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4">
        <View className="flex-row items-center justify-between mb-3 border-b border-dark-border pb-2">
          <Text className="text-xs font-bold text-white uppercase tracking-wider">
            Organizational Master Units Catalog ({total.toLocaleString()})
          </Text>
        </View>

        {isLoading ? (
          <View className="py-12 items-center justify-center">
            <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs text-slate-400 mt-2 font-medium">Fetching organizational units...</Text>
          </View>
        ) : !unitsData || unitsData.items.length === 0 ? (
          <View className="py-12 items-center justify-center">
            <Text className="text-sm text-slate-400 font-medium">No organizational units found matching query.</Text>
          </View>
        ) : (
          <View className="gap-2">
            {unitsData.items.map((item) => (
              <View
                key={`${item.unit_type}-${item.unit_id}`}
                className="bg-dark-bg border border-dark-border p-3 rounded-lg flex-col sm:flex-row sm:items-center justify-between gap-2"
              >
                <View className="flex-1">
                  <View className="flex-row items-center gap-2 mb-1 flex-wrap">
                    <View className="flex-row items-center gap-1 bg-slate-900 border border-slate-700 px-1.5 py-0.5 rounded">
                      {getUnitIcon(item.unit_type)}
                      <Text className="text-[9px] uppercase font-bold text-slate-300">{item.unit_type}</Text>
                    </View>

                    {item.unit_code && (
                      <View className="bg-blue-950 border border-blue-800 px-1.5 py-0.2 rounded">
                        <Text className="text-[9px] font-mono font-bold text-blue-400">{item.unit_code}</Text>
                      </View>
                    )}

                    <Text className="text-xs font-bold text-white font-mono">{item.unit_name}</Text>

                    {!item.is_active && (
                      <View className="bg-rose-950 border border-rose-800 px-1.5 py-0.2 rounded">
                        <Text className="text-[8px] font-bold text-rose-400">INACTIVE</Text>
                      </View>
                    )}
                  </View>

                  <View className="flex-row items-center gap-2 text-[11px] text-slate-400">
                    {item.parent_name && (
                      <Text className="text-[11px] text-slate-400">
                        Parent: <Text className="text-slate-300 font-medium">{item.parent_name}</Text>
                      </Text>
                    )}
                    {item.head_name && (
                      <Text className="text-[11px] text-slate-400">
                        • Leader: <Text className="text-emerald-400 font-medium">{item.head_name}</Text>
                        {item.head_code && <Text className="text-slate-500"> ({item.head_code})</Text>}
                      </Text>
                    )}
                  </View>
                </View>

                <View className="flex-row items-center gap-3 self-end sm:self-center">
                  <View className="items-end">
                    <Text className="text-xs font-mono font-bold text-white">
                      {item.active_headcount.toLocaleString()}
                    </Text>
                    <Text className="text-[9px] text-slate-400">active staff</Text>
                  </View>
                </View>
              </View>
            ))}
          </View>
        )}

        {/* ── Pagination Footer ───────────────────────────────── */}
        {totalPages > 1 && (
          <View className="flex-row items-center justify-between pt-4 border-t border-dark-border mt-3">
            <Text className="text-xs text-slate-400">
              Showing {page * limit + 1} - {Math.min((page + 1) * limit, total)} of {total.toLocaleString()} units
            </Text>

            <View className="flex-row items-center gap-2">
              <TouchableOpacity
                onPress={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className={`p-1.5 rounded-lg border ${
                  page === 0 ? "border-dark-border opacity-40" : "border-dark-border bg-dark-bg"
                }`}
              >
                <ChevronLeft size={16} color="#94a3b8" />
              </TouchableOpacity>

              <Text className="text-xs font-mono text-slate-300">
                {page + 1} / {totalPages}
              </Text>

              <TouchableOpacity
                onPress={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                className={`p-1.5 rounded-lg border ${
                  page >= totalPages - 1
                    ? "border-dark-border opacity-40"
                    : "border-dark-border bg-dark-bg"
                }`}
              >
                <ChevronRight size={16} color="#94a3b8" />
              </TouchableOpacity>
            </View>
          </View>
        )}
      </View>
    </View>
  );
};
