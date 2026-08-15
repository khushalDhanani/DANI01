import React from "react";
import { Text, View } from "react-native";
import {
  AlertCircle,
  Calendar,
  CheckCircle2,
  Clock,
  Gift,
  Info,
  MapPin,
  PackageCheck,
  ShieldCheck,
  UserCheck,
  XCircle,
} from "lucide-react-native";
import { CoverageBar } from "../../components/CoverageBar";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { THEME_COLORS } from "@/constants/theme";
import type { PRCampaignDetail } from "@/types/campaign.types";

interface PRCampaignOverviewTabProps {
  campaign: PRCampaignDetail | undefined;
  isLoading: boolean;
}

export const PRCampaignOverviewTab: React.FC<PRCampaignOverviewTabProps> = ({
  campaign,
  isLoading,
}) => {
  if (isLoading) {
    return (
      <View className="gap-4">
        <LoadingSkeleton height={140} borderRadius={12} />
        <LoadingSkeleton height={180} borderRadius={12} />
        <LoadingSkeleton height={200} borderRadius={12} />
      </View>
    );
  }

  if (!campaign) {
    return (
      <View className="bg-dark-card border border-dark-border rounded-xl p-8 items-center justify-center gap-2">
        <AlertCircle size={32} color={THEME_COLORS.warningIcon} />
        <Text className="text-sm font-bold text-white">No Campaign Selected</Text>
        <Text className="text-xs text-slate-400 text-center">
          Select a PR Campaign above to inspect its metrics, timeline, item grade allocations, and event schedule.
        </Text>
      </View>
    );
  }

  const total = campaign.TotalTransactions || 1;
  const approvedPct = (campaign.ApprovedCount / total) * 100;
  const deliveredPct = (campaign.DeliveredCount / total) * 100;
  const pendingPct = (campaign.PendingReviewCount / total) * 100;
  const rejectedPct = (campaign.RejectedCount / total) * 100;

  return (
    <View className="gap-6">
      {/* ── Key Scale Indicators Grid ─────────────────────────── */}
      <View className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
        {/* Total Target Recipients */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-4 shadow-sm">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
              Total Target Recipients
            </Text>
            <UserCheck size={16} color={THEME_COLORS.primaryIcon} />
          </View>
          <Text className="text-2xl font-black text-white font-mono">
            {campaign.TotalTransactions.toLocaleString()}
          </Text>
          <Text className="text-[10px] text-slate-500 mt-1 font-mono">
            dbo.PRTransactionDetails
          </Text>
        </View>

        {/* Approved Count */}
        <View className="bg-dark-card border border-emerald-800/40 rounded-xl p-4 shadow-sm">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] uppercase font-bold text-emerald-400/90 tracking-wider">
              Approved
            </Text>
            <CheckCircle2 size={16} color={THEME_COLORS.successIcon} />
          </View>
          <Text className="text-2xl font-black text-white font-mono">
            {campaign.ApprovedCount.toLocaleString()}
          </Text>
          <Text className="text-[10px] text-emerald-400/80 mt-1 font-medium">
            {approvedPct.toFixed(1)}% of total target
          </Text>
        </View>

        {/* Delivered Count */}
        <View className="bg-dark-card border border-violet-800/40 rounded-xl p-4 shadow-sm">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] uppercase font-bold text-violet-400/90 tracking-wider">
              Delivered
            </Text>
            <PackageCheck size={16} color={THEME_COLORS.accentIcon} />
          </View>
          <Text className="text-2xl font-black text-white font-mono">
            {campaign.DeliveredCount.toLocaleString()}
          </Text>
          <Text className="text-[10px] text-violet-400/80 mt-1 font-medium">
            {deliveredPct.toFixed(1)}% completed
          </Text>
        </View>

        {/* Pending Review Count */}
        <View className="bg-dark-card border border-amber-800/40 rounded-xl p-4 shadow-sm">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] uppercase font-bold text-amber-400/90 tracking-wider">
              Pending Review
            </Text>
            <Clock size={16} color={THEME_COLORS.warningIcon} />
          </View>
          <Text className="text-2xl font-black text-white font-mono">
            {campaign.PendingReviewCount.toLocaleString()}
          </Text>
          <Text className="text-[10px] text-amber-400/80 mt-1 font-medium">
            {pendingPct.toFixed(1)}% awaiting review
          </Text>
        </View>

        {/* Rejected Count */}
        <View className="bg-dark-card border border-rose-900/40 rounded-xl p-4 shadow-sm">
          <View className="flex-row items-center justify-between mb-1.5">
            <Text className="text-[10px] uppercase font-bold text-rose-400/90 tracking-wider">
              Rejected / Declined
            </Text>
            <XCircle size={16} color={THEME_COLORS.dangerIcon} />
          </View>
          <Text className="text-2xl font-black text-white font-mono">
            {campaign.RejectedCount.toLocaleString()}
          </Text>
          <Text className="text-[10px] text-rose-400/80 mt-1 font-medium">
            {rejectedPct.toFixed(1)}% rejected
          </Text>
        </View>
      </View>

      {/* ── Campaign Progress Breakdown ───────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-sm">
        <View className="flex-row items-center justify-between mb-4 pb-3 border-b border-dark-border">
          <View>
            <Text className="text-xs font-bold text-white uppercase tracking-wider">
              Campaign Lifecycle Progress
            </Text>
            <Text className="text-[11px] text-slate-400 mt-0.5">
              Live status breakdown for {campaign.CampName}
            </Text>
          </View>
          <View className="flex-row items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 border border-slate-700">
            <ShieldCheck size={13} color={THEME_COLORS.successIcon} />
            <Text className="text-[10px] font-mono font-semibold text-emerald-400">
              {campaign.CampStatus || "Active"}
            </Text>
          </View>
        </View>

        <View className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2">
          <CoverageBar
            label="Review Approval Rate"
            percent={approvedPct}
            count={campaign.ApprovedCount}
            total={campaign.TotalTransactions}
            colorScheme="emerald"
          />
          <CoverageBar
            label="Fulfillment Delivery Rate"
            percent={deliveredPct}
            count={campaign.DeliveredCount}
            total={campaign.TotalTransactions}
            colorScheme="purple"
          />
          <CoverageBar
            label="Pending Review Rate"
            percent={pendingPct}
            count={campaign.PendingReviewCount}
            total={campaign.TotalTransactions}
            colorScheme="amber"
          />
          <CoverageBar
            label="Rejection Rate"
            percent={rejectedPct}
            count={campaign.RejectedCount}
            total={campaign.TotalTransactions}
            colorScheme="rose"
          />
        </View>
      </View>

      {/* ── Key Campaign Dates & Item Configurations Grid ─────── */}
      <View className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Timeline Key Dates */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-sm gap-3.5">
          <View className="flex-row items-center gap-2 pb-3 border-b border-dark-border">
            <Calendar size={15} color={THEME_COLORS.primaryIcon} />
            <Text className="text-xs font-bold text-white uppercase tracking-wider">
              Campaign Schedule & Cut-Off Dates
            </Text>
          </View>

          <View className="gap-2.5">
            <View className="flex-row items-center justify-between p-2.5 rounded-lg bg-dark-bg/60 border border-dark-border/60">
              <Text className="text-xs font-medium text-slate-300">Campaign Start Date</Text>
              <Text className="text-xs font-mono font-bold text-white">
                {campaign.CampStartDate ? new Date(campaign.CampStartDate).toLocaleDateString() : "—"}
              </Text>
            </View>

            <View className="flex-row items-center justify-between p-2.5 rounded-lg bg-dark-bg/60 border border-dark-border/60">
              <Text className="text-xs font-medium text-slate-300">Review Cut-Off Date</Text>
              <Text className="text-xs font-mono font-bold text-amber-400">
                {campaign.CampReviewCutOfDate ? new Date(campaign.CampReviewCutOfDate).toLocaleDateString() : "—"}
              </Text>
            </View>

            <View className="flex-row items-center justify-between p-2.5 rounded-lg bg-dark-bg/60 border border-dark-border/60">
              <Text className="text-xs font-medium text-slate-300">Delivery Reminder Date</Text>
              <Text className="text-xs font-mono font-bold text-blue-400">
                {campaign.CampDelReminderDate ? new Date(campaign.CampDelReminderDate).toLocaleDateString() : "—"}
              </Text>
            </View>

            <View className="flex-row items-center justify-between p-2.5 rounded-lg bg-dark-bg/60 border border-dark-border/60">
              <Text className="text-xs font-medium text-slate-300">Transaction Cut-Off Date</Text>
              <Text className="text-xs font-mono font-bold text-purple-400">
                {campaign.TransCutOffDate ? new Date(campaign.TransCutOffDate).toLocaleDateString() : "—"}
              </Text>
            </View>

            <View className="flex-row items-center justify-between p-2.5 rounded-lg bg-dark-bg/60 border border-dark-border/60">
              <Text className="text-xs font-medium text-slate-300">Campaign Close Date</Text>
              <Text className="text-xs font-mono font-bold text-emerald-400">
                {campaign.CampCloseDate ? new Date(campaign.CampCloseDate).toLocaleDateString() : "—"}
              </Text>
            </View>
          </View>
        </View>

        {/* Configured Gift Items per PR Grade */}
        <View className="bg-dark-card border border-dark-border rounded-xl p-5 shadow-sm gap-3.5">
          <View className="flex-row items-center justify-between pb-3 border-b border-dark-border">
            <View className="flex-row items-center gap-2">
              <Gift size={15} color={THEME_COLORS.accentIcon} />
              <Text className="text-xs font-bold text-white uppercase tracking-wider">
                Configured Gift Items per PR Grade
              </Text>
            </View>
            <Text className="text-[10px] font-mono text-slate-400">
              dbo.PRCampaignDet
            </Text>
          </View>

          {campaign.Items && campaign.Items.length > 0 ? (
            <View className="gap-2">
              {campaign.Items.map((item, idx) => (
                <View
                  key={`${item.CampDetID}-${item.PRClassID}-${idx}`}
                  className="flex-row items-center justify-between p-3 rounded-lg bg-dark-bg/60 border border-dark-border/80"
                >
                  <View className="flex-row items-center gap-2.5">
                    <View className="px-2 py-0.5 rounded bg-violet-950/80 border border-violet-800/60">
                      <Text className="text-[10px] font-bold text-violet-300">
                        {item.PRClassName || `Grade #${item.PRClassID}`}
                      </Text>
                    </View>
                    <Text className="text-xs font-bold text-white">
                      {item.ItemName || `Item Ref #${item.ItemRefID}`}
                    </Text>
                  </View>

                  <View className="flex-row items-center gap-2">
                    {item.AdHocLimit != null && (
                      <Text className="text-[10px] font-mono text-slate-400">
                        Quota: <Text className="font-bold text-amber-400">{item.AdHocLimit}</Text>
                      </Text>
                    )}
                    <Text className="text-[10px] font-mono text-slate-500">
                      ID #{item.ItemRefID || "—"}
                    </Text>
                  </View>
                </View>
              ))}
            </View>
          ) : (
            <View className="p-4 items-center justify-center">
              <Text className="text-xs text-slate-400 italic">
                No specific items configured in dbo.PRCampaignDet for this campaign.
              </Text>
            </View>
          )}

          {/* Event Mappings */}
          {campaign.Events && campaign.Events.length > 0 && (
            <View className="mt-2 pt-3 border-t border-dark-border gap-2">
              <View className="flex-row items-center gap-1.5 mb-1">
                <MapPin size={13} color={THEME_COLORS.warningIcon} />
                <Text className="text-[11px] font-bold text-slate-300 uppercase tracking-wider">
                  Linked Calendar Events (dbo.PRCampaignEventMap)
                </Text>
              </View>
              {campaign.Events.map((ev) => (
                <View key={ev.ID} className="flex-row items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800">
                  <Text className="text-xs font-medium text-slate-200">
                    {ev.EventSubject || `Daylite Event #${ev.DLEventID}`} (Location #{ev.LocID || "—"})
                  </Text>
                  <Text className="text-[10px] font-mono text-slate-400">
                    {ev.EventFromDate ? new Date(ev.EventFromDate).toLocaleDateString() : "—"}
                  </Text>
                </View>
              ))}
            </View>
          )}
        </View>
      </View>

      {/* Data Integrity Alert Banner */}
      <View className="bg-blue-950/20 border border-blue-800/40 rounded-xl p-4 flex-row items-start gap-3">
        <Info size={16} color={THEME_COLORS.primaryIcon} className="mt-0.5" />
        <View className="flex-1">
          <Text className="text-xs font-bold text-blue-300">
            Source MSSQL Schema & Read-Only Audit Policy
          </Text>
          <Text className="text-[11px] text-slate-300 mt-1 leading-relaxed">
            All campaign totals, review counts, and recipient entries are compiled dynamically from live MSSQL queries (`dbo.PRCampaignMst`, `dbo.PRTransactionDetails`, `dbo.PRClassMst`). PR Owner names are safely joined via `PROwnerEmpID = DLPersonMst.EmpID`.
          </Text>
        </View>
      </View>
    </View>
  );
};
