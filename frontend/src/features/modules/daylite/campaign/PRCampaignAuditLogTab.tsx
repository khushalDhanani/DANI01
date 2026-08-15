import React, { useState } from "react";
import { Pressable, Text, View } from "react-native";
import {
  AlertCircle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock,
  FileCode,
  ShieldAlert,
  UserCheck,
  XCircle,
} from "lucide-react-native";
import { LoadingSkeleton } from "@/components/ui/LoadingSkeleton";
import { THEME_COLORS } from "@/constants/theme";
import { useCampaignAuditLog } from "@/hooks/useCampaigns";

interface PRCampaignAuditLogTabProps {
  campId?: number;
}

export const PRCampaignAuditLogTab: React.FC<PRCampaignAuditLogTabProps> = ({
  campId,
}) => {
  const [page, setPage] = useState(1);
  const limit = 25;
  const offset = (page - 1) * limit;

  const { data, isLoading, isError, refetch } = useCampaignAuditLog({
    camp_id: campId,
    limit,
    offset,
  });

  const total = data?.total ?? 0;
  const totalPages = Math.ceil(total / limit) || 1;
  const items = data?.items ?? [];

  return (
    <View className="gap-4">
      {/* Header Info */}
      <View className="flex-row items-center justify-between px-1">
        <Text className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          Review & Approval History Audit Trail ({total.toLocaleString()} log entries in dbo.PRTransactionLog)
        </Text>
        <Text className="text-[11px] font-mono text-slate-400">
          Page {page} of {totalPages}
        </Text>
      </View>

      {/* Log Items Stream */}
      {isLoading ? (
        <View className="gap-3">
          <LoadingSkeleton height={75} borderRadius={10} />
          <LoadingSkeleton height={75} borderRadius={10} />
          <LoadingSkeleton height={75} borderRadius={10} />
        </View>
      ) : isError ? (
        <View className="bg-dark-card border border-rose-900/50 rounded-xl p-6 items-center justify-center gap-2">
          <AlertCircle size={28} color={THEME_COLORS.dangerIcon} />
          <Text className="text-sm font-bold text-rose-300">Failed to load Audit Logs</Text>
          <Pressable
            onPress={() => refetch()}
            className="px-3 py-1.5 bg-rose-900/40 border border-rose-700 rounded-lg mt-2"
          >
            <Text className="text-xs font-bold text-white">Retry Request</Text>
          </Pressable>
        </View>
      ) : items.length === 0 ? (
        <View className="bg-dark-card border border-dark-border rounded-xl p-8 items-center justify-center gap-2">
          <Clock size={32} color={THEME_COLORS.textMuted} />
          <Text className="text-sm font-bold text-white">No Audit Logs Found</Text>
          <Text className="text-xs text-slate-400 text-center">
            No review status transactions recorded for the selected campaign filter.
          </Text>
        </View>
      ) : (
        <View className="gap-2.5">
          {items.map((log) => {
            const isReject =
              log.TransactionDesc === "Reject" || log.StatusName === "Reject" || log.TransactionStatusID === 551;

            return (
              <View
                key={log.TransactionID}
                className="bg-dark-card border border-dark-border rounded-xl p-4 gap-2.5 shadow-sm"
              >
                <View className="flex-row items-center justify-between flex-wrap gap-2">
                  <View className="flex-row items-center gap-2">
                    {isReject ? (
                      <XCircle size={15} color={THEME_COLORS.dangerIcon} />
                    ) : (
                      <CheckCircle2 size={15} color={THEME_COLORS.successIcon} />
                    )}

                    <Text className="text-xs font-bold text-white">
                      Action: <Text className={isReject ? "text-rose-400" : "text-emerald-400"}>{log.TransactionDesc || log.StatusName || "Status Update"}</Text>
                    </Text>

                    {log.PRID != null && (
                      <View className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                        <Text className="text-[10px] font-mono font-bold text-slate-300">
                          PR #{log.PRID}
                        </Text>
                      </View>
                    )}

                    {log.ModuleName && (
                      <Text className="text-[10px] font-mono text-slate-400">
                        ({log.ModuleName})
                      </Text>
                    )}
                  </View>

                  <Text className="text-[10px] font-mono text-slate-400">
                    {log.EntDt ? new Date(log.EntDt).toLocaleString() : "—"}
                  </Text>
                </View>

                {/* Audit user & correlation details */}
                <View className="flex-row items-center justify-between pt-1.5 border-t border-dark-border/40 flex-wrap gap-2">
                  <Text className="text-xs font-medium text-slate-300">
                    Executed By User: <Text className="font-bold text-white">{log.EntUser || "System"}</Text>
                  </Text>

                  {log.CorrelationId && (
                    <View className="flex-row items-center gap-1">
                      <FileCode size={11} color={THEME_COLORS.textMuted} />
                      <Text className="text-[10px] font-mono text-slate-400">
                        ID: {log.CorrelationId.slice(0, 8)}…
                      </Text>
                    </View>
                  )}
                </View>
              </View>
            );
          })}
        </View>
      )}

      {/* Pagination Bar */}
      {totalPages > 1 && (
        <View className="flex-row items-center justify-between bg-dark-card border border-dark-border rounded-xl p-3 shadow-sm mt-2">
          <Pressable
            disabled={page <= 1}
            onPress={() => setPage((p) => Math.max(1, p - 1))}
            className={`flex-row items-center gap-1 px-3 py-1.5 rounded-lg border transition-all ${
              page <= 1
                ? "bg-slate-900 border-slate-800 opacity-50"
                : "bg-slate-800 hover:bg-slate-700 border-slate-700"
            }`}
          >
            <ChevronLeft size={14} color={THEME_COLORS.textMuted} />
            <Text className="text-xs font-bold text-slate-300">Previous</Text>
          </Pressable>

          <Text className="text-xs font-mono text-slate-400">
            Showing logs {offset + 1} – {Math.min(offset + limit, total)} of {total}
          </Text>

          <Pressable
            disabled={page >= totalPages}
            onPress={() => setPage((p) => Math.min(totalPages, p + 1))}
            className={`flex-row items-center gap-1 px-3 py-1.5 rounded-lg border transition-all ${
              page >= totalPages
                ? "bg-slate-900 border-slate-800 opacity-50"
                : "bg-slate-800 hover:bg-slate-700 border-slate-700"
            }`}
          >
            <Text className="text-xs font-bold text-slate-300">Next</Text>
            <ChevronRight size={14} color={THEME_COLORS.textMuted} />
          </Pressable>
        </View>
      )}
    </View>
  );
};
