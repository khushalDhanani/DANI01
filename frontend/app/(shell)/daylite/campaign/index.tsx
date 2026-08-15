import React, { useState } from "react";
import { Pressable, Text, View } from "react-native";
import {
  BarChart3,
  Clock,
  Gift,
  RefreshCw,
  Sparkles,
  Users,
} from "lucide-react-native";
import { PageContainer } from "@/components/layout/PageContainer";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { PRCampaignAuditLogTab } from "@/features/modules/daylite/campaign/PRCampaignAuditLogTab";
import { PRCampaignOverviewTab } from "@/features/modules/daylite/campaign/PRCampaignOverviewTab";
import { PRCampaignTransactionsTab } from "@/features/modules/daylite/campaign/PRCampaignTransactionsTab";
import { useCampaignDetail, useCampaigns } from "@/hooks/useCampaigns";
import { THEME_COLORS } from "@/constants/theme";

type CampaignTab = "overview" | "transactions" | "audit";

export default function PRCampaignScreen() {
  const [selectedCampId, setSelectedCampId] = useState<number | undefined>(undefined);
  const [activeTab, setActiveTab] = useState<CampaignTab>("overview");

  // Query all campaigns overview list
  const {
    data: campaigns,
    isLoading: isLoadingList,
    isError: isErrorList,
    error: errorList,
    refetch: refetchList,
    isRefetching: isRefetchingList,
  } = useCampaigns();

  // Active campaign ID (default to first campaign if none selected)
  const activeCampId = selectedCampId ?? (campaigns && campaigns.length > 0 ? campaigns[0].CampID : undefined);

  // Query active campaign detailed profile
  const {
    data: campaignDetail,
    isLoading: isLoadingDetail,
    refetch: refetchDetail,
  } = useCampaignDetail(activeCampId);

  const handleRefresh = () => {
    refetchList();
    if (activeCampId) refetchDetail();
  };

  if (isErrorList && !campaigns) {
    return (
      <PageContainer>
        <ErrorState
          message={errorList?.message || "Failed to query PR Campaigns from MSSQL."}
          onRetry={handleRefresh}
          title="Failed to Load PR Campaigns"
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      {/* ── Top Header Banner ───────────────────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-sm mb-4">
        <View className="flex-col md:flex-row md:items-center justify-between gap-4">
          <View className="flex-1">
            <View className="flex-row items-center gap-2 mb-1.5">
              <Sparkles size={16} color={THEME_COLORS.primaryIcon} />
              <Text className="text-xs uppercase font-bold text-blue-400 tracking-wider">
                Daylite Domain Operations
              </Text>
            </View>
            <Text className="text-2xl font-black text-white tracking-tight">
              PR Campaign Intelligence & Fulfillment Hub
            </Text>
            <Text className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
              Read-only campaign lifecycle analytics across target recipient directory, gift item grade rules, review approvals, and delivery fulfillment status.
            </Text>
          </View>

          {/* Refresh Action */}
          <Pressable
            onPress={handleRefresh}
            disabled={isLoadingList || isRefetchingList}
            accessibilityRole="button"
            accessibilityLabel="Refresh PR Campaign data"
            className="flex-row items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 active:bg-slate-900 border border-slate-700 transition-all self-start md:self-auto"
          >
            <RefreshCw
              size={13}
              color={THEME_COLORS.textMuted}
              className={isRefetchingList ? "animate-spin" : ""}
            />
            <Text className="text-xs font-semibold text-slate-200">
              {isRefetchingList ? "Syncing..." : "Refresh Live Data"}
            </Text>
          </Pressable>
        </View>

        {/* ── Campaign Selector Bar ───────────────────────────────── */}
        {isLoadingList ? (
          <View className="mt-4">
            <LoadingSkeleton height={42} borderRadius={8} />
          </View>
        ) : campaigns && campaigns.length > 0 ? (
          <View className="mt-4 pt-3 border-t border-dark-border flex-row items-center gap-2 flex-wrap">
            <Text className="text-xs font-bold text-slate-400 uppercase tracking-wider mr-1">
              Select Campaign:
            </Text>
            {campaigns.map((c) => {
              const selected = activeCampId === c.CampID;
              return (
                <Pressable
                  key={c.CampID}
                  onPress={() => setSelectedCampId(c.CampID)}
                  className={`flex-row items-center gap-2 px-3 py-1.5 rounded-lg border transition-all ${
                    selected
                      ? "bg-blue-600 border-blue-500 shadow-sm"
                      : "bg-slate-800/80 hover:bg-slate-800 border-slate-700"
                  }`}
                >
                  <Gift size={13} color={selected ? THEME_COLORS.onPrimary : THEME_COLORS.accentIcon} />
                  <Text className={`text-xs font-bold ${selected ? "text-white" : "text-slate-300"}`}>
                    {c.CampName}
                  </Text>
                  <View className={`px-1.5 py-0.2 rounded text-[9px] font-mono ${selected ? "bg-blue-900/80 text-blue-200" : "bg-slate-900 text-slate-400"}`}>
                    <Text className={`text-[9px] font-mono font-bold ${selected ? "text-blue-100" : "text-slate-400"}`}>
                      {c.TotalTransactions} Recs
                    </Text>
                  </View>
                </Pressable>
              );
            })}
          </View>
        ) : null}
      </View>

      {/* ── Main Navigation Tabs Bar ────────────────────────────── */}
      <View className="flex-row items-center border-b border-dark-border mb-4 gap-1">
        {/* Overview Tab */}
        <Pressable
          onPress={() => setActiveTab("overview")}
          accessibilityRole="tab"
          accessibilityState={{ selected: activeTab === "overview" }}
          className={`flex-row items-center gap-1.5 px-4 py-2.5 border-b-2 transition-all ${
            activeTab === "overview"
              ? "border-blue-500 bg-blue-500/10"
              : "border-transparent hover:bg-slate-800/40"
          }`}
        >
          <BarChart3
            size={15}
            color={activeTab === "overview" ? THEME_COLORS.primaryIcon : THEME_COLORS.textMuted}
          />
          <Text
            className={`text-xs font-bold ${
              activeTab === "overview" ? "text-white" : "text-slate-400"
            }`}
          >
            Campaign Overview & Metrics
          </Text>
        </Pressable>

        {/* Transactions Tab */}
        <Pressable
          onPress={() => setActiveTab("transactions")}
          accessibilityRole="tab"
          accessibilityState={{ selected: activeTab === "transactions" }}
          className={`flex-row items-center gap-1.5 px-4 py-2.5 border-b-2 transition-all ${
            activeTab === "transactions"
              ? "border-blue-500 bg-blue-500/10"
              : "border-transparent hover:bg-slate-800/40"
          }`}
        >
          <Users
            size={15}
            color={activeTab === "transactions" ? THEME_COLORS.primaryIcon : THEME_COLORS.textMuted}
          />
          <Text
            className={`text-xs font-bold ${
              activeTab === "transactions" ? "text-white" : "text-slate-400"
            }`}
          >
            PR Recipient Directory
          </Text>
          {campaignDetail && (
            <View className="bg-slate-800 px-1.5 py-0.2 rounded border border-slate-700">
              <Text className="text-[9px] font-mono font-bold text-slate-300">
                {campaignDetail.TotalTransactions}
              </Text>
            </View>
          )}
        </Pressable>

        {/* Audit Log Tab */}
        <Pressable
          onPress={() => setActiveTab("audit")}
          accessibilityRole="tab"
          accessibilityState={{ selected: activeTab === "audit" }}
          className={`flex-row items-center gap-1.5 px-4 py-2.5 border-b-2 transition-all ${
            activeTab === "audit"
              ? "border-blue-500 bg-blue-500/10"
              : "border-transparent hover:bg-slate-800/40"
          }`}
        >
          <Clock
            size={15}
            color={activeTab === "audit" ? THEME_COLORS.primaryIcon : THEME_COLORS.textMuted}
          />
          <Text
            className={`text-xs font-bold ${
              activeTab === "audit" ? "text-white" : "text-slate-400"
            }`}
          >
            Review Audit Log
          </Text>
        </Pressable>
      </View>

      {/* ── Active Tab Content Pane ─────────────────────────────── */}
      {activeTab === "overview" ? (
        <PRCampaignOverviewTab campaign={campaignDetail} isLoading={isLoadingDetail} />
      ) : activeTab === "transactions" ? (
        <PRCampaignTransactionsTab campId={activeCampId} />
      ) : (
        <PRCampaignAuditLogTab campId={activeCampId} />
      )}
    </PageContainer>
  );
}
