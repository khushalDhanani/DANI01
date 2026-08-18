import React, { useState } from "react";
import { ActivityIndicator, Modal, Pressable, ScrollView, Text, View } from "react-native";
import {
  Briefcase,
  Building2,
  CreditCard,
  GraduationCap,
  Heart,
  Lock,
  Mail,
  User,
  Users,
  X,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import { useEmployeeRecordDetail } from "@/hooks/useEmployee";

interface EmployeeDetailModalProps {
  empId: number | null;
  onClose: () => void;
}

type DetailTabType = "overview" | "history" | "family" | "qual" | "exp";

export const EmployeeDetailModal: React.FC<EmployeeDetailModalProps> = ({
  empId,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<DetailTabType>("overview");
  const { data: detail, isLoading } = useEmployeeRecordDetail(empId);

  if (!empId) return null;

  return (
    <Modal visible={true} transparent={true} animationType="fade">
      <View className="flex-1 bg-black/75 justify-center items-center p-3 md:p-4">
        <View className="w-full max-w-4xl max-h-[90vh] bg-dark-card border border-dark-border rounded-xl flex-col overflow-hidden shadow-2xl">
          {/* ── Modal Header ─────────────────────────────────── */}
          <View className="p-4 border-b border-dark-border bg-slate-900 flex-row items-center justify-between">
            <View className="flex-row items-center gap-3">
              <View className="w-10 h-10 rounded-full bg-blue-600/20 border border-blue-500/30 items-center justify-center">
                <User size={20} color={THEME_COLORS.primaryIcon} />
              </View>
              <View>
                <View className="flex-row items-center gap-2">
                  <Text className="text-base font-bold text-white">
                    {detail?.full_name || `Employee #${empId}`}
                  </Text>
                  {detail?.is_active ? (
                    <View className="bg-emerald-950 border border-emerald-800 px-2 py-0.5 rounded text-[10px]">
                      <Text className="text-[10px] font-bold text-emerald-300">ACTIVE</Text>
                    </View>
                  ) : (
                    <View className="bg-slate-800 px-2 py-0.5 rounded text-[10px]">
                      <Text className="text-[10px] font-bold text-slate-400">INACTIVE</Text>
                    </View>
                  )}
                </View>
                <Text className="text-xs font-mono text-slate-400">
                  Badge: <Text className="text-blue-300 font-bold">{detail?.emp_code || "N/A"}</Text> • EmpID: {empId}
                </Text>
              </View>
            </View>

            <Pressable
              onPress={onClose}
              className="w-8 h-8 rounded-lg bg-slate-800 items-center justify-center hover:bg-slate-700"
            >
              <X size={16} color={THEME_COLORS.textMuted} />
            </Pressable>
          </View>

          {/* ── Tab Navigation ──────────────────────────────── */}
          <View className="px-4 border-b border-dark-border bg-dark-bg flex-row items-center gap-2 overflow-x-auto">
            {[
              { id: "overview", label: "Overview & Posting", icon: Briefcase },
              { id: "history", label: "Position History", icon: Building2 },
              { id: "family", label: "Family & Emergency", icon: Heart },
              { id: "qual", label: "Qualifications", icon: GraduationCap },
              { id: "exp", label: "Past Experience", icon: Users },
            ].map((tab) => {
              const Icon = tab.icon;
              const active = activeTab === tab.id;
              return (
                <Pressable
                  key={tab.id}
                  onPress={() => setActiveTab(tab.id as DetailTabType)}
                  className={`flex-row items-center gap-1.5 py-3 px-3 border-b-2 text-xs font-bold transition-all ${
                    active
                      ? "border-blue-500 text-blue-400 bg-blue-950/20"
                      : "border-transparent text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <Icon size={13} color={active ? THEME_COLORS.primaryIcon : THEME_COLORS.textMuted} />
                  <Text className={`text-xs font-bold ${active ? "text-blue-400" : "text-slate-400"}`}>
                    {tab.label}
                  </Text>
                </Pressable>
              );
            })}
          </View>

          {/* ── Content Body ─────────────────────────────────── */}
          {isLoading || !detail ? (
            <View className="py-20 items-center justify-center">
              <ActivityIndicator size="large" color={THEME_COLORS.primaryIcon} />
              <Text className="text-xs text-slate-400 mt-2">Loading complete employee profile...</Text>
            </View>
          ) : (
            <ScrollView className="flex-1 p-4" showsVerticalScrollIndicator={false}>
              {/* TAB 1: OVERVIEW */}
              {activeTab === "overview" && (
                <View className="gap-4">
                  {/* Current Position & Department Card */}
                  <View className="bg-dark-bg border border-dark-border rounded-xl p-4">
                    <View className="flex-row items-center gap-2 mb-3">
                      <Briefcase size={15} color={THEME_COLORS.primaryIcon} />
                      <Text className="text-xs font-bold text-white uppercase tracking-wider">Current Official Assignment</Text>
                    </View>
                    <View className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <View>
                        <Text className="text-[10px] text-slate-400">Department</Text>
                        <Text className="text-xs font-bold text-white">{detail.current_dept || "Unassigned"}</Text>
                      </View>
                      <View>
                        <Text className="text-[10px] text-slate-400">Designation</Text>
                        <Text className="text-xs font-bold text-white">{detail.current_desig || "Unassigned"}</Text>
                      </View>
                      <View>
                        <Text className="text-[10px] text-slate-400">Site Location</Text>
                        <Text className="text-xs font-bold text-white">{detail.current_location || "Unassigned"}</Text>
                      </View>
                      <View>
                        <Text className="text-[10px] text-slate-400">Grade &amp; Type</Text>
                        <Text className="text-xs font-bold text-white">{detail.current_grade || "N/A"} ({detail.employment_type || "Permanent"})</Text>
                      </View>
                    </View>
                  </View>

                  {/* Manager Hierarchy */}
                  <View className="bg-dark-bg border border-dark-border rounded-xl p-4">
                    <View className="flex-row items-center gap-2 mb-3">
                      <Users size={15} color={THEME_COLORS.primaryIcon} />
                      <Text className="text-xs font-bold text-white uppercase tracking-wider">Reporting Lines</Text>
                    </View>
                    <View className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <View className="bg-dark-card border border-dark-border p-3 rounded-lg">
                        <Text className="text-[10px] uppercase font-bold text-blue-400 mb-1">Functional Manager (Technical HOD)</Text>
                        <Text className="text-xs font-bold text-white">
                          {detail.functional_mgr_name || "No Manager Configured"}
                        </Text>
                        {detail.functional_mgr_code ? (
                          <Text className="text-[10px] font-mono text-slate-400">Badge: {detail.functional_mgr_code}</Text>
                        ) : null}
                      </View>

                      <View className="bg-dark-card border border-dark-border p-3 rounded-lg">
                        <Text className="text-[10px] uppercase font-bold text-purple-400 mb-1">Administrative Manager (HR)</Text>
                        <Text className="text-xs font-bold text-white">
                          {detail.admin_mgr_name || "No Manager Configured"}
                        </Text>
                        {detail.admin_mgr_code ? (
                          <Text className="text-[10px] font-mono text-slate-400">Badge: {detail.admin_mgr_code}</Text>
                        ) : null}
                      </View>
                    </View>
                  </View>

                  {/* Contact & Address */}
                  <View className="bg-dark-bg border border-dark-border rounded-xl p-4">
                    <View className="flex-row items-center gap-2 mb-3">
                      <Mail size={15} color={THEME_COLORS.primaryIcon} />
                      <Text className="text-xs font-bold text-white uppercase tracking-wider">Contact &amp; Addresses</Text>
                    </View>
                    <View className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <View>
                        <Text className="text-[10px] text-slate-400">Corporate Email</Text>
                        <Text className="text-xs font-mono font-bold text-blue-300">{detail.company_email || "N/A"}</Text>
                      </View>
                      <View>
                        <Text className="text-[10px] text-slate-400">Personal Email</Text>
                        <Text className="text-xs font-mono text-slate-300">{detail.personal_email || "N/A"}</Text>
                      </View>
                      <View>
                        <Text className="text-[10px] text-slate-400">Primary Mobile</Text>
                        <Text className="text-xs font-mono font-bold text-white">{detail.phone1 || "N/A"}</Text>
                      </View>
                      <View className="col-span-1 md:col-span-3">
                        <Text className="text-[10px] text-slate-400">Correspondence Address</Text>
                        <Text className="text-xs text-slate-300">{detail.correspondence_address || "No address documented"} {detail.corr_pincode ? `(${detail.corr_pincode})` : ""}</Text>
                      </View>
                    </View>
                  </View>

                  {/* Identity Identifiers */}
                  <View className="bg-dark-bg border border-dark-border rounded-xl p-4">
                    <View className="flex-row items-center gap-2 mb-3">
                      <CreditCard size={15} color={THEME_COLORS.primaryIcon} />
                      <Text className="text-xs font-bold text-white uppercase tracking-wider">Statutory &amp; Identity Keys</Text>
                    </View>
                    <View className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <View className="bg-dark-card p-2 rounded border border-dark-border">
                        <Text className="text-[9px] text-slate-400">Income Tax PAN</Text>
                        <Text className="text-xs font-mono font-bold text-slate-200">{detail.pan_no || "N/A"}</Text>
                      </View>
                      <View className="bg-dark-card p-2 rounded border border-dark-border">
                        <Text className="text-[9px] text-slate-400">Aadhaar No</Text>
                        <Text className="text-xs font-mono font-bold text-slate-200">{detail.aadhar_no || "N/A"}</Text>
                      </View>
                      <View className="bg-dark-card p-2 rounded border border-dark-border">
                        <Text className="text-[9px] text-slate-400">UAN / PF No</Text>
                        <Text className="text-xs font-mono font-bold text-slate-200">{detail.uan_no || detail.pf_no || "N/A"}</Text>
                      </View>
                      <View className="bg-dark-card p-2 rounded border border-dark-border">
                        <Text className="text-[9px] text-slate-400">Azure AD Object ID</Text>
                        <Text className="text-[10px] font-mono text-slate-300 truncate">{detail.microsoft_object_id || "N/A"}</Text>
                      </View>
                    </View>
                  </View>

                  {/* Portal User Account */}
                  <View className="bg-dark-bg border border-dark-border rounded-xl p-4">
                    <View className="flex-row items-center justify-between mb-3">
                      <View className="flex-row items-center gap-2">
                        <Lock size={15} color={THEME_COLORS.primaryIcon} />
                        <Text className="text-xs font-bold text-white uppercase tracking-wider">Portal User Account</Text>
                      </View>
                      {detail.user_id ? (
                        <View className="bg-emerald-950 border border-emerald-800 px-2 py-0.5 rounded">
                          <Text className="text-[10px] font-bold text-emerald-300">USER ID: {detail.user_id}</Text>
                        </View>
                      ) : (
                        <View className="bg-slate-800 px-2 py-0.5 rounded">
                          <Text className="text-[10px] text-slate-400">No User Account</Text>
                        </View>
                      )}
                    </View>
                    {detail.user_id ? (
                      <View className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <View>
                          <Text className="text-[10px] text-slate-400">Username / Login</Text>
                          <Text className="text-xs font-mono font-bold text-white">{detail.user_name}</Text>
                        </View>
                        <View>
                          <Text className="text-[10px] text-slate-400">Security Role</Text>
                          <Text className="text-xs font-bold text-blue-300">{detail.role_desc || "Default"}</Text>
                        </View>
                        <View>
                          <Text className="text-[10px] text-slate-400">AD Login ID</Text>
                          <Text className="text-xs font-mono text-slate-300">{detail.user_ad_id || "N/A"}</Text>
                        </View>
                      </View>
                    ) : (
                      <Text className="text-xs text-slate-400">This employee does not have an active login account in SecurityUserMst.</Text>
                    )}
                  </View>
                </View>
              )}

              {/* TAB 2: POSITION HISTORY */}
              {activeTab === "history" && (
                <View className="gap-3">
                  <Text className="text-xs font-bold text-slate-400 mb-1">Position &amp; Designation History ({detail.official_history.length})</Text>
                  {detail.official_history.map((hist, idx) => (
                    <View
                      key={hist.office_det_id || idx}
                      className={`p-3 rounded-lg border ${
                        hist.is_active ? "bg-blue-950/20 border-blue-500/40" : "bg-dark-bg border-dark-border"
                      }`}
                    >
                      <View className="flex-row items-center justify-between mb-1">
                        <Text className="text-xs font-bold text-white">{hist.desig_name || "Unassigned"}</Text>
                        {hist.is_active ? (
                          <View className="bg-emerald-950 px-1.5 py-0.5 rounded border border-emerald-800">
                            <Text className="text-[9px] font-bold text-emerald-300">CURRENT POSITION</Text>
                          </View>
                        ) : null}
                      </View>
                      <Text className="text-[11px] text-slate-300">
                        {hist.dept_name} • {hist.loc_name} • Grade: {hist.grade_desc || "N/A"}
                      </Text>
                      <Text className="text-[10px] font-mono text-slate-400 mt-1">
                        Effective From: {hist.applicable_from || hist.joining_date || "N/A"}
                      </Text>
                    </View>
                  ))}
                </View>
              )}

              {/* TAB 3: FAMILY & EMERGENCY */}
              {activeTab === "family" && (
                <View className="gap-3">
                  <Text className="text-xs font-bold text-slate-400 mb-1">Family Members &amp; Emergency Contacts ({detail.family_members.length})</Text>
                  {!detail.family_members.length ? (
                    <Text className="text-xs text-slate-400 py-6 text-center">No family member records documented.</Text>
                  ) : (
                    detail.family_members.map((fam, idx) => (
                      <View key={fam.family_det_id || idx} className="bg-dark-bg border border-dark-border p-3 rounded-lg flex-row items-center justify-between">
                        <View>
                          <View className="flex-row items-center gap-2">
                            <Text className="text-xs font-bold text-white">{fam.name}</Text>
                            {fam.is_emergency_contact ? (
                              <View className="bg-rose-950 px-1.5 py-0.5 rounded border border-rose-800">
                                <Text className="text-[9px] font-bold text-rose-300">EMERGENCY CONTACT</Text>
                              </View>
                            ) : null}
                          </View>
                          {fam.phone ? <Text className="text-[10px] font-mono text-slate-400 mt-0.5">{fam.phone}</Text> : null}
                        </View>
                        {fam.birth_date ? <Text className="text-[10px] text-slate-400">DOB: {fam.birth_date}</Text> : null}
                      </View>
                    ))
                  )}
                </View>
              )}

              {/* TAB 4: QUALIFICATIONS */}
              {activeTab === "qual" && (
                <View className="gap-3">
                  <Text className="text-xs font-bold text-slate-400 mb-1">Academic Qualifications ({detail.qualifications.length})</Text>
                  {!detail.qualifications.length ? (
                    <Text className="text-xs text-slate-400 py-6 text-center">No qualification records documented.</Text>
                  ) : (
                    detail.qualifications.map((q, idx) => (
                      <View key={q.qual_det_id || idx} className="bg-dark-bg border border-dark-border p-3 rounded-lg">
                        <Text className="text-xs font-bold text-white">{q.institute_name || "Academic Degree"}</Text>
                        <Text className="text-[11px] text-slate-300">Passing Year: {q.passing_year || "N/A"} • Grade: {q.percentage_grade || "N/A"}</Text>
                      </View>
                    ))
                  )}
                </View>
              )}

              {/* TAB 5: PAST EXPERIENCE */}
              {activeTab === "exp" && (
                <View className="gap-3">
                  <Text className="text-xs font-bold text-slate-400 mb-1">Prior Work Experience ({detail.experiences.length})</Text>
                  {!detail.experiences.length ? (
                    <Text className="text-xs text-slate-400 py-6 text-center">No prior experience records documented.</Text>
                  ) : (
                    detail.experiences.map((exp, idx) => (
                      <View key={exp.exp_det_id || idx} className="bg-dark-bg border border-dark-border p-3 rounded-lg">
                        <Text className="text-xs font-bold text-white">{exp.company_name}</Text>
                        <Text className="text-[11px] text-slate-300">{exp.designation || "Role"} • CTC: {exp.last_drawn_ctc || "N/A"}</Text>
                      </View>
                    ))
                  )}
                </View>
              )}
            </ScrollView>
          )}
        </View>
      </View>
    </Modal>
  );
};
