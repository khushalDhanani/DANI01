import React, { useState } from "react";
import {
  FlatList,
  Pressable,
  Text,
  TextInput,
  View,
} from "react-native";
import {
  ArrowDownAZ,
  ArrowUpAZ,
  Building2,
  Calendar,
  Hash,
  Mail,
  MapPin,
  Phone,
  RotateCcw,
  Search,
  Sparkles,
  UserCheck,
  X,
} from "lucide-react-native";
import { usePersonList } from "@/hooks/useModules";
import { PersonListItemCard } from "./PersonListItemCard";
import { PaginationControls } from "@/components/tables/PaginationControls";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { THEME_COLORS } from "@/constants/theme";
import type { PersonListItem, PersonListParams } from "@/types/modules.types";

type StatusFilterType =
  | "ALL"
  | "ACTIVE"
  | "INACTIVE"
  | "VISITOR"
  | "CONTACT"
  | "PUBLIC"
  | "PRIVATE"
  | "TEMP"
  | "BLACKLIST"
  | "DELETED";

interface PersonListViewProps {
  /** When set, locks the list to PersonIsVisitor_Contact = 1 (Visitor) or 2 (Contact). */
  visitorContact?: 1 | 2;
}

export const PersonListView: React.FC<PersonListViewProps> = ({ visitorContact }) => {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilterType>("ALL");
  const [hasEmail, setHasEmail] = useState<boolean | undefined>(undefined);
  const [hasPhone, setHasPhone] = useState<boolean | undefined>(undefined);
  const [hasAddress, setHasAddress] = useState<boolean | undefined>(undefined);
  const [hasCompany, setHasCompany] = useState<boolean | undefined>(undefined);
  const [hasOwner, setHasOwner] = useState<boolean | undefined>(undefined);
  const [page, setPage] = useState(0);
  const [sortBy, setSortBy] = useState<"PersonID" | "PersonFirstName" | "PersonLastName" | "PersonEntDt">("PersonID");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const limit = 25;

  const queryParams: PersonListParams = {
    search: search.trim() || undefined,
    status: statusFilter,
    has_email: hasEmail,
    has_phone: hasPhone,
    has_address: hasAddress,
    has_company: hasCompany,
    has_owner: hasOwner,
    visitor_contact: visitorContact,
    limit,
    offset: page * limit,
    sort_by: sortBy,
    sort_order: sortOrder,
  };

  const {
    data: listData,
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = usePersonList(queryParams);

  const handleSearchChange = (text: string) => {
    setSearch(text);
    setPage(0);
  };

  const handleStatusChange = (status: StatusFilterType) => {
    setStatusFilter(status);
    setPage(0);
  };

  const handleToggleSort = (field: "PersonID" | "PersonFirstName" | "PersonEntDt") => {
    if (sortBy === field) {
      setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(field);
      setSortOrder(field === "PersonFirstName" ? "asc" : "desc");
    }
    setPage(0);
  };

  const handleResetFilters = () => {
    setSearch("");
    setStatusFilter("ALL");
    setHasEmail(undefined);
    setHasPhone(undefined);
    setHasAddress(undefined);
    setHasCompany(undefined);
    setHasOwner(undefined);
    setSortBy("PersonID");
    setSortOrder("desc");
    setPage(0);
  };

  const hasActiveFilters = Boolean(
    search ||
      statusFilter !== "ALL" ||
      hasEmail !== undefined ||
      hasPhone !== undefined ||
      hasAddress !== undefined ||
      hasCompany !== undefined ||
      hasOwner !== undefined
  );

  // Derive segment-specific title
  const directoryTitle =
    visitorContact === 1
      ? "Visitor Directory"
      : visitorContact === 2
        ? "Contact Directory"
        : "Person Directory";

  return (
    <View style={{ flex: 1, height: "100%", minHeight: 0 }} className="gap-3">
      {/* ── Top Header ────────────────────────────────────────── */}
      <View className="flex-row items-center justify-between flex-wrap gap-2">
        <View>
          <View className="flex-row items-center gap-1.5 mb-0.5">
            <Sparkles size={13} color={THEME_COLORS.primaryIcon} />
            <Text className="text-[10px] uppercase font-bold text-blue-400 tracking-wider">
              Daylite Intelligence Hub
            </Text>
          </View>
          <Text className="text-lg sm:text-xl font-black text-white tracking-tight">
            {directoryTitle} ({listData?.total !== undefined ? listData.total.toLocaleString() : "…"})
          </Text>
        </View>

        {/* Sort Selectors */}
        <View className="flex-row items-center gap-1.5 bg-dark-card border border-dark-border p-1 rounded-lg">
          <Text className="text-[10px] font-bold text-slate-500 px-1.5">Sort:</Text>

          {/* Newest ID Sort */}
          <Pressable
            onPress={() => handleToggleSort("PersonID")}
            className={`px-2 py-1 rounded flex-row items-center gap-1 ${
              sortBy === "PersonID" ? "bg-blue-600" : "bg-slate-900 active:bg-slate-800"
            }`}
          >
            <Hash size={11} color={sortBy === "PersonID" ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted} />
            <Text
              className={`text-[11px] font-semibold ${
                sortBy === "PersonID" ? "text-white" : "text-slate-300"
              }`}
            >
              ID {sortBy === "PersonID" ? (sortOrder === "desc" ? "↓" : "↑") : ""}
            </Text>
          </Pressable>

          {/* Name A-Z Sort */}
          <Pressable
            onPress={() => handleToggleSort("PersonFirstName")}
            className={`px-2 py-1 rounded flex-row items-center gap-1 ${
              sortBy === "PersonFirstName" ? "bg-blue-600" : "bg-slate-900 active:bg-slate-800"
            }`}
          >
            {sortOrder === "asc" && sortBy === "PersonFirstName" ? (
              <ArrowDownAZ size={11} color={sortBy === "PersonFirstName" ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted} />
            ) : (
              <ArrowUpAZ size={11} color={sortBy === "PersonFirstName" ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted} />
            )}
            <Text
              className={`text-[11px] font-semibold ${
                sortBy === "PersonFirstName" ? "text-white" : "text-slate-300"
              }`}
            >
              Name
            </Text>
          </Pressable>

          {/* Date Created Sort */}
          <Pressable
            onPress={() => handleToggleSort("PersonEntDt")}
            className={`px-2 py-1 rounded flex-row items-center gap-1 ${
              sortBy === "PersonEntDt" ? "bg-blue-600" : "bg-slate-900 active:bg-slate-800"
            }`}
          >
            <Calendar size={11} color={sortBy === "PersonEntDt" ? THEME_COLORS.onPrimary : THEME_COLORS.textMuted} />
            <Text
              className={`text-[11px] font-semibold ${
                sortBy === "PersonEntDt" ? "text-white" : "text-slate-300"
              }`}
            >
              Date
            </Text>
          </Pressable>
        </View>
      </View>

      {/* ── Toolbar: Search & Multi-Filters ───────────────────── */}
      <View className="bg-dark-card border border-dark-border p-2.5 rounded-xl gap-2.5 shadow-sm">
        {/* Row 1: Search Input */}
        <View className="flex-row items-center bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 gap-2">
          <Search size={14} color={THEME_COLORS.textMuted} />
          <TextInput
            value={search}
            onChangeText={handleSearchChange}
            placeholder="Search by name, owner, email, phone, city, title, or company…"
            placeholderTextColor={THEME_COLORS.textMuted}
            className="flex-1 text-xs text-white"
            autoCapitalize="none"
            autoCorrect={false}
          />
          {search ? (
            <Pressable onPress={() => handleSearchChange("")}>
              <X size={13} color={THEME_COLORS.textMuted} />
            </Pressable>
          ) : null}
        </View>

        {/* Row 2: Status Tabs & Attribute Presence Filters */}
        <View className="flex-row items-center justify-between flex-wrap gap-2">
          {/* Status & Business Mapping Tabs */}
          <View className="flex-row items-center gap-1 flex-wrap">
            {(
              [
                "ALL",
                "ACTIVE",
                "INACTIVE",
                // Hide VISITOR/CONTACT pills when the tab already locks the segment
                ...(visitorContact == null ? (["VISITOR", "CONTACT"] as StatusFilterType[]) : []),
                "PUBLIC",
                "PRIVATE",
                "TEMP",
                "DELETED",
              ] as StatusFilterType[]
            ).map((st) => {
              const active = statusFilter === st;
              return (
                <Pressable
                  key={st}
                  onPress={() => handleStatusChange(st)}
                  className={`px-2 py-1 rounded-md text-xs font-semibold transition-all ${
                    active
                      ? "bg-blue-600 shadow-sm"
                      : "bg-slate-900/80 hover:bg-slate-800 border border-slate-800"
                  }`}
                >
                  <Text
                    className={`text-[10px] font-bold uppercase tracking-wider ${
                      active ? "text-white" : "text-slate-400"
                    }`}
                  >
                    {st === "ALL" ? "All" : st.charAt(0) + st.slice(1).toLowerCase()}
                  </Text>
                </Pressable>
              );
            })}
          </View>

          {/* Presence Filters (Email, Phone, Address, Company) */}
          <View className="flex-row items-center gap-1.5 flex-wrap">
            {/* Has Email */}
            <Pressable
              onPress={() => {
                setHasEmail((prev) => (prev === true ? undefined : true));
                setPage(0);
              }}
              className={`flex-row items-center gap-1 px-2 py-0.5 rounded border transition-all ${
                hasEmail === true
                  ? "bg-blue-950 border-blue-600"
                  : "bg-slate-900 border-slate-800"
              }`}
            >
              <Mail size={10} color={hasEmail === true ? THEME_COLORS.primaryIcon : THEME_COLORS.textMuted} />
              <Text
                className={`text-[10px] font-medium ${
                  hasEmail === true ? "text-blue-300 font-bold" : "text-slate-400"
                }`}
              >
                Email
              </Text>
            </Pressable>

            {/* Has Phone */}
            <Pressable
              onPress={() => {
                setHasPhone((prev) => (prev === true ? undefined : true));
                setPage(0);
              }}
              className={`flex-row items-center gap-1 px-2 py-0.5 rounded border transition-all ${
                hasPhone === true
                  ? "bg-emerald-950 border-emerald-600"
                  : "bg-slate-900 border-slate-800"
              }`}
            >
              <Phone size={10} color={hasPhone === true ? THEME_COLORS.successIcon : THEME_COLORS.textMuted} />
              <Text
                className={`text-[10px] font-medium ${
                  hasPhone === true ? "text-emerald-300 font-bold" : "text-slate-400"
                }`}
              >
                Phone
              </Text>
            </Pressable>

            {/* Has Address */}
            <Pressable
              onPress={() => {
                setHasAddress((prev) => (prev === true ? undefined : true));
                setPage(0);
              }}
              className={`flex-row items-center gap-1 px-2 py-0.5 rounded border transition-all ${
                hasAddress === true
                  ? "bg-amber-950 border-amber-600"
                  : "bg-slate-900 border-slate-800"
              }`}
            >
              <MapPin size={10} color={hasAddress === true ? THEME_COLORS.warningIcon : THEME_COLORS.textMuted} />
              <Text
                className={`text-[10px] font-medium ${
                  hasAddress === true ? "text-amber-300 font-bold" : "text-slate-400"
                }`}
              >
                Address
              </Text>
            </Pressable>

            {/* Has Company */}
            <Pressable
              onPress={() => {
                setHasCompany((prev) => (prev === true ? undefined : true));
                setPage(0);
              }}
              className={`flex-row items-center gap-1 px-2 py-0.5 rounded border transition-all ${
                hasCompany === true
                  ? "bg-purple-950 border-purple-600"
                  : "bg-slate-900 border-slate-800"
              }`}
            >
              <Building2 size={10} color={hasCompany === true ? THEME_COLORS.companyIcon : THEME_COLORS.textMuted} />
              <Text
                className={`text-[10px] font-medium ${
                  hasCompany === true ? "text-purple-300 font-bold" : "text-slate-400"
                }`}
              >
                Company
              </Text>
            </Pressable>

            {/* Has Owner */}
            <Pressable
              onPress={() => {
                setHasOwner((prev) => (prev === true ? undefined : true));
                setPage(0);
              }}
              className={`flex-row items-center gap-1 px-2 py-0.5 rounded border transition-all ${
                hasOwner === true
                  ? "bg-indigo-950 border-indigo-600"
                  : "bg-slate-900 border-slate-800"
              }`}
            >
              <UserCheck size={10} color={hasOwner === true ? THEME_COLORS.ownerIcon : THEME_COLORS.textMuted} />
              <Text
                className={`text-[10px] font-medium ${
                  hasOwner === true ? "text-indigo-300 font-bold" : "text-slate-400"
                }`}
              >
                Owner
              </Text>
            </Pressable>

            {/* Reset Filters */}
            {hasActiveFilters ? (
              <Pressable
                onPress={handleResetFilters}
                className="p-1 rounded bg-slate-800 hover:bg-slate-700 active:bg-slate-900 ml-1"
                accessibilityLabel="Reset all filters"
              >
                <RotateCcw size={12} color={THEME_COLORS.textMuted} />
              </Pressable>
            ) : null}
          </View>
        </View>
      </View>

      {/* ── Main Content / Person List ────────────────────────── */}
      {isLoading && !listData ? (
        <LoadingState message="Querying Daylite Person master records…" />
      ) : isError ? (
        <ErrorState
          message={error?.message || "Failed to load person directory records."}
          onRetry={refetch}
        />
      ) : listData && listData.items.length === 0 ? (
        <EmptyState
          title="No person records found"
          message={
            search
              ? `No individuals matched "${search}" with current status filter.`
              : "No records found matching the active filter criteria."
          }
        />
      ) : (
        <FlatList<PersonListItem>
          data={listData?.items || []}
          renderItem={({ item }) => (
            <PersonListItemCard person={item} />
          )}
          keyExtractor={(item) => String(item.PersonID)}
          ItemSeparatorComponent={() => <View className="h-2" />}
          showsVerticalScrollIndicator={false}
          ListFooterComponent={
            listData ? (
              <PaginationControls
                page={page}
                limit={limit}
                total={listData.total}
                onPageChange={setPage}
                isFetching={isFetching}
              />
            ) : null
          }
          contentContainerStyle={{ paddingBottom: 16 }}
        />
      )}
    </View>
  );
};
