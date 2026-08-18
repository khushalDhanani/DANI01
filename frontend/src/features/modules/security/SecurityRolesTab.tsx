import React, { useState } from "react";
import {
  ActivityIndicator,
  Modal,
  Pressable,
  ScrollView,
  Text,
  View,
} from "react-native";
import {
  Check,
  KeyRound,
  Lock,
  Minus,
  Shield,
  Users,
  X,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import {
  useSecurityRolePermissions,
  useSecurityRoles,
} from "@/hooks/useSecurity";
import type { SecurityRoleItem } from "@/types/security.types";

export function SecurityRolesTab() {
  const { data: rolesData, isLoading, isError } = useSecurityRoles();
  const [selectedRole, setSelectedRole] = useState<SecurityRoleItem | null>(null);

  const {
    data: permissionsData,
    isLoading: isLoadingPermissions,
  } = useSecurityRolePermissions(
    selectedRole ? selectedRole.role_id : 0,
    Boolean(selectedRole)
  );

  if (isLoading) {
    return (
      <View className="py-8 items-center justify-center">
        <ActivityIndicator size="large" color="#a855f7" />
        <Text className="text-sm text-slate-400 mt-3 font-medium">Loading security roles catalog...</Text>
      </View>
    );
  }

  if (isError || !rolesData) {
    return (
      <View className="py-8 items-center justify-center">
        <Text className="text-sm text-red-400 font-medium">Failed to load security roles.</Text>
      </View>
    );
  }

  return (
    <View className="gap-4">
      {/* Header Banner */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 flex-row items-center justify-between">
        <View className="flex-row items-center gap-3">
          <View className="w-10 h-10 rounded-xl bg-purple-950/80 border border-purple-800/60 items-center justify-center">
            <KeyRound size={20} color="#a855f7" />
          </View>
          <View>
            <Text className="text-sm font-bold text-white">Role-Based Access Control (RBAC) Matrix</Text>
            <Text className="text-xs text-slate-400">
              {rolesData.active_roles} active roles out of {rolesData.total_roles} total roles configured in master.
            </Text>
          </View>
        </View>
      </View>

      {/* Roles Grid */}
      <View className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {rolesData.items.map((r) => {
            const isDeleted = r.is_deleted;
            return (
              <Pressable
                key={r.role_id}
                onPress={() => setSelectedRole(r)}
                className="bg-dark-card border border-dark-border hover:border-purple-500/50 rounded-xl p-4 flex-col justify-between transition-colors"
              >
                <View>
                  <View className="flex-row items-center justify-between mb-2">
                    <View className="flex-row items-center gap-1.5 flex-1 pr-2">
                      <Shield size={16} color={isDeleted ? "#ef4444" : "#a855f7"} />
                      <Text className="text-sm font-bold text-white" numberOfLines={1}>
                        {r.role_desc}
                      </Text>
                    </View>
                    <View
                      className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        isDeleted
                          ? "bg-red-950/60 border-red-800/60 text-red-400"
                          : "bg-emerald-950/60 border-emerald-800/60 text-emerald-400"
                      }`}
                    >
                      <Text
                        className={`text-[9px] font-bold ${
                          isDeleted ? "text-red-400" : "text-emerald-400"
                        }`}
                      >
                        {isDeleted ? "DELETED" : "ACTIVE"}
                      </Text>
                    </View>
                  </View>

                  <View className="flex-row items-center gap-4 my-2">
                    <View className="flex-row items-center gap-1">
                      <Users size={12} color="#94a3b8" />
                      <Text className="text-xs font-semibold text-slate-200">
                        {r.active_assigned_users} active
                      </Text>
                    </View>
                    <View className="flex-row items-center gap-1">
                      <Lock size={12} color="#94a3b8" />
                      <Text className="text-xs font-semibold text-slate-200">
                        {r.assigned_menus_count} menus
                      </Text>
                    </View>
                  </View>

                  {/* CRUD Rights Badges */}
                  <View className="flex-row items-center gap-1.5 mt-2">
                    <View className="px-1.5 py-0.5 rounded bg-blue-950/80 border border-blue-800/60">
                      <Text className="text-[9px] font-bold text-blue-400">
                        V: {r.view_perms_count}
                      </Text>
                    </View>
                    <View className="px-1.5 py-0.5 rounded bg-emerald-950/80 border border-emerald-800/60">
                      <Text className="text-[9px] font-bold text-emerald-400">
                        I: {r.insert_perms_count}
                      </Text>
                    </View>
                    <View className="px-1.5 py-0.5 rounded bg-amber-950/80 border border-amber-800/60">
                      <Text className="text-[9px] font-bold text-amber-400">
                        U: {r.update_perms_count}
                      </Text>
                    </View>
                    <View className="px-1.5 py-0.5 rounded bg-rose-950/80 border border-rose-800/60">
                      <Text className="text-[9px] font-bold text-rose-400">
                        D: {r.delete_perms_count}
                      </Text>
                    </View>
                  </View>
                </View>

                <View className="mt-3 pt-3 border-t border-dark-border/60 flex-row items-center justify-between">
                  <Text className="text-[10px] font-mono text-slate-500">Role ID: #{r.role_id}</Text>
                  <Text className="text-[11px] font-semibold text-purple-400">View Rights →</Text>
                </View>
              </Pressable>
            );
          })}
        </View>

      {/* Permissions Matrix Modal */}
      {selectedRole && (
        <Modal
          visible={Boolean(selectedRole)}
          transparent
          animationType="fade"
          onRequestClose={() => setSelectedRole(null)}
        >
          <View className="flex-1 bg-black/80 items-center justify-center p-4">
            <View className="bg-dark-card border border-dark-border rounded-xl w-full max-w-3xl max-h-[85vh] flex-col overflow-hidden shadow-2xl">
              {/* Modal Header */}
              <View className="flex-row items-center justify-between px-5 py-4 border-b border-dark-border bg-dark-bg/60">
                <View className="flex-row items-center gap-3">
                  <KeyRound size={20} color="#a855f7" />
                  <View>
                    <Text className="text-base font-bold text-white">{selectedRole.role_desc}</Text>
                    <Text className="text-xs text-slate-400">
                      Role ID: #{selectedRole.role_id} • Assigned to {selectedRole.active_assigned_users} active users
                    </Text>
                  </View>
                </View>
                <Pressable
                  onPress={() => setSelectedRole(null)}
                  className="p-1 rounded-lg hover:bg-dark-border text-slate-400"
                >
                  <X size={20} color={THEME_COLORS.textMuted} />
                </Pressable>
              </View>

              {/* Modal Body */}
              {isLoadingPermissions ? (
                <View className="py-8 items-center justify-center">
                  <ActivityIndicator size="large" color="#a855f7" />
                  <Text className="text-xs text-slate-400 mt-2">Loading menu permissions...</Text>
                </View>
              ) : !permissionsData || permissionsData.permissions.length === 0 ? (
                <View className="py-8 items-center justify-center">
                  <Text className="text-sm font-semibold text-slate-400">No active permissions configured.</Text>
                  <Text className="text-xs text-slate-500 mt-1">This role currently has 0 menu rights assigned.</Text>
                </View>
              ) : (
                <ScrollView className="flex-1 w-full" showsVerticalScrollIndicator={false}>
                  <View className="w-full divide-y divide-dark-border">
                    {/* Header */}
                    <View className="flex-row items-center px-4 py-2.5 bg-dark-bg/60 border-b border-dark-border">
                      <Text className="flex-1 min-w-[180px] text-[11px] font-bold uppercase tracking-wider text-slate-400">Menu / Form Name</Text>
                      <Text className="w-36 text-[11px] font-bold uppercase tracking-wider text-slate-400">Portal / Route</Text>
                      <Text className="w-16 text-center text-[11px] font-bold uppercase tracking-wider text-blue-400">View</Text>
                      <Text className="w-16 text-center text-[11px] font-bold uppercase tracking-wider text-emerald-400">Insert</Text>
                      <Text className="w-16 text-center text-[11px] font-bold uppercase tracking-wider text-amber-400">Update</Text>
                      <Text className="w-16 text-center text-[11px] font-bold uppercase tracking-wider text-rose-400">Delete</Text>
                    </View>

                    {/* Permission Rows */}
                    {permissionsData.permissions.map((p) => (
                      <View
                        key={p.role_menu_id}
                        className="flex-row items-center px-4 py-2.5 hover:bg-dark-bg/40"
                      >
                        <View className="flex-1 min-w-[180px] pr-2">
                          <Text className="text-xs font-semibold text-white" numberOfLines={1}>
                            {p.menu_name || p.form_name || "Untitled Action"}
                          </Text>
                          {p.form_name && (
                            <Text className="text-[10px] text-slate-500 font-mono">{p.form_name}</Text>
                          )}
                        </View>

                        <Text className="w-36 text-xs font-mono text-slate-400" numberOfLines={1}>
                          {p.route_portal || "default"}
                        </Text>

                        {/* View */}
                        <View className="w-16 items-center">
                          {p.can_view ? (
                            <Check size={14} color="#60a5fa" />
                          ) : (
                            <Minus size={14} color="#475569" />
                          )}
                        </View>

                        {/* Insert */}
                        <View className="w-16 items-center">
                          {p.can_insert ? (
                            <Check size={14} color="#34d399" />
                          ) : (
                            <Minus size={14} color="#475569" />
                          )}
                        </View>

                        {/* Update */}
                        <View className="w-16 items-center">
                          {p.can_update ? (
                            <Check size={14} color="#fbbf24" />
                          ) : (
                            <Minus size={14} color="#475569" />
                          )}
                        </View>

                        {/* Delete */}
                        <View className="w-16 items-center">
                          {p.can_delete ? (
                            <Check size={14} color="#f87171" />
                          ) : (
                            <Minus size={14} color="#475569" />
                          )}
                        </View>
                      </View>
                    ))}
                  </View>
                </ScrollView>
              )}

              {/* Modal Footer */}
              <View className="px-5 py-3 border-t border-dark-border bg-dark-bg/60 flex-row items-center justify-between">
                <Text className="text-xs text-slate-400 font-mono">
                  Total mapped rights: {permissionsData?.total_permissions || 0}
                </Text>
                <Pressable
                  onPress={() => setSelectedRole(null)}
                  className="bg-dark-card border border-dark-border hover:border-slate-600 px-4 py-1.5 rounded-lg"
                >
                  <Text className="text-xs font-semibold text-slate-300">Close</Text>
                </Pressable>
              </View>
            </View>
          </View>
        </Modal>
      )}
    </View>
  );
}
