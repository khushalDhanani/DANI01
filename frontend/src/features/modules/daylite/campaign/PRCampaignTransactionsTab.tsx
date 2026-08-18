import React, { useState } from "react";
import { Pressable, Text, TextInput, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import {
  AlertCircle,
  ExternalLink,
  Search,
  User,
} from "lucide-react-native";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { THEME_COLORS } from "@/constants/theme";
import { usePRTransactions } from "@/hooks/useCampaigns";
import { PaginationBar } from "./PaginationBar";
import { formatDateTime } from "@/utils/formatters";

interface PRCampaignTransactionsTabProps {
  campId?: number;
}

export const PRCampaignTransactionsTab: React.FC<PRCampaignTransactionsTabProps> = ({
  campId,
}) => {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [reviewStatusFilter, setReviewStatusFilter] = useState<number | undefined>(undefined);
  const [deliveryStatusFilter, setDeliveryStatusFilter] = useState<number | undefined>(undefined);
  const [page, setPage] = useState(1);
  const limit = 25;
  const offset = (page - 1) * limit;

  const { data, isLoading, isError, refetch } = usePRTransactions({
    camp_id: campId,
    review_status_id: reviewStatusFilter,
    delivery_status_id: deliveryStatusFilter,
    search: search ? search.trim() : undefined,
    limit,
    offset,
  });

  const total = data?.total ?? 0;
  const totalPages = Math.ceil(total / limit) || 1;
  const items = data?.items ?? [];

  const handleReviewFilterChange = (statusId: number | undefined) => {
    setReviewStatusFilter(statusId);
    setPage(1);
  };

  const handleDeliveryFilterChange = (statusId: number | undefined) => {
    setDeliveryStatusFilter(statusId);
    setPage(1);
  };

  const getReviewBadgeStyle = (statusId: number | null | undefined, name?: string | null) => {
    if (statusId === 550) {
      return { bg: "bg-emerald-950/60", border: "border-emerald-800/80", text: "text-emerald-300", label: "Approved" };
    }
    if (statusId === 551) {
      return { bg: "bg-rose-950/60", border: "border-rose-800/80", text: "text-rose-300", label: "Rejected" };
    }
    if (statusId === 548) {
      return { bg: "bg-amber-950/60", border: "border-amber-800/80", text: "text-amber-300", label: "Pending" };
    }
    return { bg: "bg-slate-800", border: "border-slate-700", text: "text-slate-300", label: name || "Unknown" };
  };

  const getDeliveryBadgeStyle = (statusId: number | null | undefined, name?: string | null) => {
    if (statusId === 555) {
      return { bg: "bg-violet-950/60", border: "border-violet-800/80", text: "text-violet-300", label: "Delivered" };
    }
    if (statusId === 559) {
      return { bg: "bg-rose-950/60", border: "border-rose-800/80", text: "text-rose-300", label: "Decline" };
    }
    if (statusId === 596) {
      return { bg: "bg-blue-950/60", border: "border-blue-800/80", text: "text-blue-300", label: "Reattempt" };
    }
    return { bg: "bg-slate-800", border: "border-slate-700", text: "text-slate-400", label: name || "Pending Delivery" };
  };

  return (
    <View className="gap-4">
      {/* ── Search & Status Filters Bar ───────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
        <View className="flex-col md:flex-row md:items-center justify-between gap-3">
          {/* Search Box */}
          <View className="flex-1 flex-row items-center bg-dark-bg/80 border border-dark-border px-3 py-2 rounded-lg">
            <Search size={14} color={THEME_COLORS.textMuted} />
            <TextInput
              value={search}
              onChangeText={(text) => {
                setSearch(text);
                setPage(1);
              }}
              placeholder="Search recipient name, PR owner name, department..."
              placeholderTextColor="#64748B"
              className="flex-1 ml-2 text-xs text-white outline-none"
            />
            {search.length > 0 && (
              <Pressable onPress={() => setSearch("")}>
                <Text className="text-xs text-slate-400 font-bold px-1">✕</Text>
              </Pressable>
            )}
          </View>

          {/* Quick Review Filter Pills */}
          <View className="flex-row items-center gap-1.5 flex-wrap">
            <Pressable
              onPress={() => handleReviewFilterChange(undefined)}
              className={`px-2.5 py-1 rounded-lg border transition-all ${
                reviewStatusFilter === undefined
                  ? "bg-blue-600 border-blue-500"
                  : "bg-slate-800 border-slate-700"
              }`}
            >
              <Text
                className={`text-[11px] font-bold ${
                  reviewStatusFilter === undefined ? "text-white" : "text-slate-400"
                }`}
              >
                All Status
              </Text>
            </Pressable>

            <Pressable
              onPress={() => handleReviewFilterChange(550)}
              className={`px-2.5 py-1 rounded-lg border transition-all ${
                reviewStatusFilter === 550
                  ? "bg-emerald-600 border-emerald-500"
                  : "bg-slate-800 border-slate-700"
              }`}
            >
              <Text
                className={`text-[11px] font-bold ${
                  reviewStatusFilter === 550 ? "text-white" : "text-emerald-400"
                }`}
              >
                Approved (550)
              </Text>
            </Pressable>

            <Pressable
              onPress={() => handleReviewFilterChange(548)}
              className={`px-2.5 py-1 rounded-lg border transition-all ${
                reviewStatusFilter === 548
                  ? "bg-amber-600 border-amber-500"
                  : "bg-slate-800 border-slate-700"
              }`}
            >
              <Text
                className={`text-[11px] font-bold ${
                  reviewStatusFilter === 548 ? "text-white" : "text-amber-400"
                }`}
              >
                Pending (548)
              </Text>
            </Pressable>

            <Pressable
              onPress={() => handleReviewFilterChange(551)}
              className={`px-2.5 py-1 rounded-lg border transition-all ${
                reviewStatusFilter === 551
                  ? "bg-rose-600 border-rose-500"
                  : "bg-slate-800 border-slate-700"
              }`}
            >
              <Text
                className={`text-[11px] font-bold ${
                  reviewStatusFilter === 551 ? "text-white" : "text-rose-400"
                }`}
              >
                Rejected (551)
              </Text>
            </Pressable>
          </View>
        </View>

        {/* Sub Delivery Filters */}
        <View className="flex-row items-center gap-2 pt-2 border-t border-dark-border/60">
          <Text className="text-[11px] font-bold text-slate-400">Delivery Status:</Text>

          <Pressable
            onPress={() => handleDeliveryFilterChange(undefined)}
            className={`px-2 py-0.5 rounded border ${
              deliveryStatusFilter === undefined
                ? "bg-slate-700 border-slate-500"
                : "bg-slate-900 border-slate-800"
            }`}
          >
            <Text className="text-[10px] text-slate-300 font-medium">Any Delivery</Text>
          </Pressable>

          <Pressable
            onPress={() => handleDeliveryFilterChange(555)}
            className={`px-2 py-0.5 rounded border ${
              deliveryStatusFilter === 555
                ? "bg-violet-900 border-violet-600"
                : "bg-slate-900 border-slate-800"
            }`}
          >
            <Text className="text-[10px] text-violet-300 font-medium">Delivered (555)</Text>
          </Pressable>

          <Pressable
            onPress={() => handleDeliveryFilterChange(554)}
            className={`px-2 py-0.5 rounded border ${
              deliveryStatusFilter === 554
                ? "bg-amber-900 border-amber-600"
                : "bg-slate-900 border-slate-800"
            }`}
          >
            <Text className="text-[10px] text-amber-300 font-medium">Pending Delivery (554)</Text>
          </Pressable>
        </View>
      </View>

      {/* ── Transaction List Header Bar ────────────────────────── */}
      <View className="flex-row items-center justify-between px-1">
        <Text className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          Target Recipients ({total.toLocaleString()} records found)
        </Text>
        <Text className="text-[11px] font-mono text-slate-400">
          Page {page} of {totalPages}
        </Text>
      </View>

      {/* ── Recipient Cards Stream / Table ─────────────────────── */}
      {isLoading ? (
        <View className="gap-3">
          <LoadingSkeleton height={85} borderRadius={10} />
          <LoadingSkeleton height={85} borderRadius={10} />
          <LoadingSkeleton height={85} borderRadius={10} />
        </View>
      ) : isError ? (
        <View className="bg-dark-card border border-rose-900/50 rounded-xl p-4 items-center justify-center gap-2">
          <AlertCircle size={28} color={THEME_COLORS.dangerIcon} />
          <Text className="text-sm font-bold text-rose-300">Failed to load PR Transactions</Text>
          <Pressable
            onPress={() => refetch()}
            className="px-3 py-1.5 bg-rose-900/40 border border-rose-700 rounded-lg mt-2"
          >
            <Text className="text-xs font-bold text-white">Retry Request</Text>
          </Pressable>
        </View>
      ) : items.length === 0 ? (
        <View className="bg-dark-card border border-dark-border rounded-xl p-4 items-center justify-center gap-2">
          <User size={32} color={THEME_COLORS.textMuted} />
          <Text className="text-sm font-bold text-white">No PR Transactions Found</Text>
          <Text className="text-xs text-slate-400 text-center">
            No recipient transactions match the active search or filter criteria.
          </Text>
        </View>
      ) : (
        <View className="gap-2.5">
          {items.map((t) => {
            const revBadge = getReviewBadgeStyle(t.CampReviewStatusID, t.ReviewStatusName);
            const delBadge = getDeliveryBadgeStyle(t.DeliveryStatusID, t.DeliveryStatusName);

            return (
              <View
                key={t.PRID}
                className="bg-dark-card border border-dark-border hover:border-slate-700 rounded-xl p-4 gap-3 shadow-sm transition-all"
              >
                {/* Header Row */}
                <View className="flex-row items-center justify-between flex-wrap gap-2">
                  <View className="flex-row items-center gap-2 flex-wrap">
                    {/* Recipient Name Link */}
                    <Pressable
                      onPress={() => router.push(`/daylite/person/${t.PersonID}` as Href)}
                      className="flex-row items-center gap-1.5 hover:underline"
                    >
                      <Text className="text-sm font-bold text-white hover:text-blue-400">
                        {t.RecipientName}
                      </Text>
                      <ExternalLink size={12} color={THEME_COLORS.primaryIcon} />
                    </Pressable>

                    <Text className="text-[10px] font-mono text-slate-400">
                      (Person #{t.PersonID})
                    </Text>

                    {/* PR Grade Badge */}
                    {t.PRClassName && (
                      <View className="px-2 py-0.5 rounded bg-violet-950/80 border border-violet-800/60">
                        <Text className="text-[10px] font-bold text-violet-300">
                          {t.PRClassName}
                        </Text>
                      </View>
                    )}

                    {/* Campaign Type */}
                    <View className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                      <Text className="text-[10px] font-mono font-medium text-slate-300">
                        {t.PRTypeName || "Campaign"}
                      </Text>
                    </View>
                  </View>

                  {/* Status Badges */}
                  <View className="flex-row items-center gap-2">
                    {/* Review Status Badge */}
                    <View className={`px-2.5 py-1 rounded-md border ${revBadge.bg} ${revBadge.border}`}>
                      <Text className={`text-[10px] font-bold ${revBadge.text}`}>
                        Review: {revBadge.label}
                      </Text>
                    </View>

                    {/* Delivery Status Badge */}
                    <View className={`px-2.5 py-1 rounded-md border ${delBadge.bg} ${delBadge.border}`}>
                      <Text className={`text-[10px] font-bold ${delBadge.text}`}>
                        Delivery: {delBadge.label}
                      </Text>
                    </View>
                  </View>
                </View>

                {/* Sub details grid */}
                <View className="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-4 gap-2 pt-2 border-t border-dark-border/40">
                  {/* Department & Title */}
                  <View>
                    <Text className="text-[10px] uppercase font-bold text-slate-400">Department / Role</Text>
                    <Text className="text-xs font-medium text-slate-200" numberOfLines={1}>
                      {[t.PersonDepartment, t.PersonTitle].filter(Boolean).join(" • ") || "—"}
                    </Text>
                  </View>

                  {/* Assigned PR Owner */}
                  <View>
                    <Text className="text-[10px] uppercase font-bold text-slate-400">Assigned PR Owner</Text>
                    <Text className="text-xs font-semibold text-indigo-300" numberOfLines={1}>
                      {t.OwnerName ? t.OwnerName : "Unassigned PR Owner"}
                    </Text>
                  </View>

                  {/* Delivery Mode */}
                  <View>
                    <Text className="text-[10px] uppercase font-bold text-slate-400">Delivery Mode</Text>
                    <Text className="text-xs font-mono font-medium text-slate-300">
                      {t.DeliveryTypeName || "Unassigned Delivery Method"}
                    </Text>
                  </View>

                  {/* Gift Ordered Date */}
                  <View>
                    <Text className="text-[10px] uppercase font-bold text-slate-400">Gift Order Date</Text>
                    <Text className="text-xs font-mono text-slate-300">
                      {t.GiftOrderedDt ? formatDateTime(t.GiftOrderedDt) : "Not Ordered"}
                    </Text>
                  </View>
                </View>
              </View>
            );
          })}
        </View>
      )}

      {/* ── Pagination Controls Bar ────────────────────────────── */}
      <PaginationBar
        page={page}
        totalPages={totalPages}
        total={total}
        limit={limit}
        label="records"
        onPageChange={setPage}
      />
    </View>
  );
};
