import React, { useState } from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import {
  Activity,
  AlertTriangle,
  ArrowLeft,
  Building2,
  Calendar,
  CheckCircle2,
  ChevronLeft,
  Clock,
  Edit2,
  FileText,
  HeartHandshake,
  Link as LinkIcon,
  Mail,
  MapPin,
  MessageSquare,
  MoreVertical,
  Phone,
  Settings,
  Share2,
  Shield,
  Sliders,
  Sparkles,
  User,
  UserCheck,
  UserPlus,
  Users,
} from "lucide-react-native";
import { usePersonDetail } from "@/hooks/useModules";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { THEME_COLORS } from "@/constants/theme";
import { FieldRow } from "./components/FieldRow";

interface PersonDetailViewProps {
  personId: number;
}

type DetailTab =
  | "profile"
  | "contacts"
  | "addresses"
  | "companies"
  | "relations"
  | "custom_docs"
  | "audit";

export const PersonDetailView: React.FC<PersonDetailViewProps> = ({ personId }) => {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<DetailTab>("profile");

  const {
    data: detail,
    isLoading,
    isError,
    error,
    refetch,
  } = usePersonDetail(personId);

  const person = detail?.person;
  const fullName = person
    ? [
      person.PersonPrefix,
      person.PersonFirstName,
      person.PersonMiddleName,
      person.PersonLastName,
      person.PersonSuffix,
    ]
      .filter(Boolean)
      .join(" ")
      .trim() || `Person #${person.PersonID}`
    : `Person #${personId}`;

  const initials = person
    ? [person.PersonFirstName?.[0], person.PersonLastName?.[0]]
      .filter(Boolean)
      .join("")
      .toUpperCase() || "P"
    : "P";

  const subtitle = person
    ? [person.PersonTitle, person.PersonDepartment].filter(Boolean).join(" • ").trim()
    : "";

  const tabs: { id: DetailTab; label: string; count?: number }[] = [
    { id: "profile", label: "Profile & Identity" },
    {
      id: "contacts",
      label: "Contacts & IM",
      count: (detail?.contacts.length || 0) + (detail?.ims.length || 0),
    },
    { id: "addresses", label: "Addresses", count: detail?.addresses.length },
    { id: "companies", label: "Companies", count: detail?.companies.length },
    { id: "relations", label: "Relations", count: detail?.relations.length },
    {
      id: "custom_docs",
      label: "Custom & Docs",
      count: (detail?.extra_fields.length || 0) + (detail?.documents.length || 0),
    },
    { id: "audit", label: "Status & Audit" },
  ];

  if (isLoading) {
    return <LoadingState message={`Resolving complete profile for Person #${personId}…`} />;
  }

  if (isError || !detail || !person) {
    return (
      <View className="gap-4">
        {/* Back navigation */}
        <Pressable
          onPress={() => router.push("/daylite/person" as Href)}
          className="flex-row items-center gap-1.5 py-1 self-start"
        >
          <ArrowLeft size={14} color={THEME_COLORS.primaryIcon} />
          <Text className="text-xs font-semibold text-blue-400">Back to Person Directory</Text>
        </Pressable>

        <ErrorState
          title={`Person #${personId} Not Found`}
          message={error?.message || "Could not retrieve Person details from database catalog."}
          onRetry={() => refetch()}
        />
      </View>
    );
  }

  return (
    <View className="gap-4 pb-12">
      {/* ── Breadcrumb Navigation ─────────────────────────────── */}
      <View className="flex-row items-center gap-2">
        <Pressable
          onPress={() => router.push("/daylite" as Href)}
          className="py-1"
          accessibilityRole="button"
          accessibilityLabel="Back to Daylite Dashboard"
        >
          <Text className="text-xs font-semibold text-blue-400">Daylite</Text>
        </Pressable>
        <Text className="text-xs text-slate-600">/</Text>
        <Pressable
          onPress={() => router.push("/daylite/person" as Href)}
          className="py-1"
          accessibilityRole="button"
          accessibilityLabel="Back to Person Directory"
        >
          <Text className="text-xs font-semibold text-blue-400">Persons</Text>
        </Pressable>
        <Text className="text-xs text-slate-600">/</Text>
        <Text className="text-xs font-medium text-slate-300" numberOfLines={1}>
          {fullName}
        </Text>
      </View>

      {/* ── Dedicated Hero Profile Card ────────────────────────── */}
      <View className="bg-dark-card border border-dark-border rounded-xl p-4 shadow-sm">
        <View className="flex-col sm:flex-row sm:items-center justify-between gap-3">
          <View className="flex-row items-center gap-3.5 flex-1 min-w-[240px]">
            {/* Avatar Circle */}
            <View className="w-11 h-11 rounded-full bg-blue-600/20 border border-blue-500/30 items-center justify-center">
              {initials ? (
                <Text className="text-sm font-black text-blue-300">{initials}</Text>
              ) : (
                <User size={18} color={THEME_COLORS.primaryIcon} />
              )}
            </View>

            <View className="flex-1">
              <View className="flex-row items-center gap-2 flex-wrap mb-0.5">
                <Text className="text-xl sm:text-2xl font-black text-white tracking-tight">
                  {fullName}
                </Text>
                <View className="bg-blue-950/80 border border-blue-800/80 px-2 py-0.5 rounded">
                  <Text className="text-[10px] font-mono font-bold text-blue-300">
                    PersonID: {personId}
                  </Text>
                </View>
                {/* PersonIsActive: 1=Active, 0=Inactive */}
                {person.PersonIsActive ? (
                  <View className="flex-row items-center gap-1 bg-emerald-950/60 border border-emerald-800/60 px-2 py-0.5 rounded-full">
                    <CheckCircle2 size={10} color={THEME_COLORS.success} />
                    <Text className="text-[10px] font-bold text-emerald-300">ACTIVE</Text>
                  </View>
                ) : (
                  <View className="bg-slate-900 border border-slate-800 px-2 py-0.5 rounded-full">
                    <Text className="text-[10px] font-bold text-slate-400">INACTIVE</Text>
                  </View>
                )}

                {/* PersonIsVisitor_Contact: 1=Visitor, 2=Contact */}
                {person.PersonIsVisitor_Contact === 1 ? (
                  <View className="bg-indigo-950/60 border border-indigo-800/60 px-2 py-0.5 rounded-full">
                    <Text className="text-[10px] font-bold text-indigo-300">VISITOR</Text>
                  </View>
                ) : person.PersonIsVisitor_Contact === 2 ? (
                  <View className="bg-blue-950/60 border border-blue-800/60 px-2 py-0.5 rounded-full">
                    <Text className="text-[10px] font-bold text-blue-300">CONTACT</Text>
                  </View>
                ) : null}

                {/* PersonIsShareContact: 1=Public, 0=Private */}
                {person.PersonIsShareContact ? (
                  <View className="bg-teal-950/60 border border-teal-800/60 px-2 py-0.5 rounded-full">
                    <Text className="text-[10px] font-bold text-teal-300">PUBLIC</Text>
                  </View>
                ) : (
                  <View className="bg-slate-900 border border-slate-700 px-2 py-0.5 rounded-full">
                    <Text className="text-[10px] font-bold text-slate-300">PRIVATE</Text>
                  </View>
                )}

                {person.PersonIsTemp ? (
                  <View className="bg-amber-950/60 border border-amber-800/60 px-2 py-0.5 rounded-full">
                    <Text className="text-[10px] font-bold text-amber-300">TEMP</Text>
                  </View>
                ) : null}
                {person.PersonIsBlackList ? (
                  <View className="bg-purple-950/60 border border-purple-800/60 px-2 py-0.5 rounded-full">
                    <Text className="text-[10px] font-bold text-purple-300">BLACKLISTED</Text>
                  </View>
                ) : null}
                {person.PersonIsDeleted ? (
                  <View className="bg-rose-950/60 border border-rose-800/60 px-2 py-0.5 rounded-full">
                    <Text className="text-[10px] font-bold text-rose-300">DELETED</Text>
                  </View>
                ) : null}
              </View>

              {subtitle ? (
                <Text className="text-xs text-slate-400 leading-snug">
                  {subtitle}
                </Text>
              ) : null}

              <View className="flex-row items-center gap-2 mt-2 flex-wrap">
                {/* Contact Owner */}
                {person.PersonEntUser && (
                  <View className="flex-row items-center gap-1.5 bg-emerald-950/50 border border-emerald-800 px-3 py-1 rounded-full shadow-sm">
                    <UserCheck size={12} color={THEME_COLORS.successIcon || "#10b981"} />
                    <Text className="text-[11px] font-bold text-emerald-300 tracking-wide uppercase">
                      Contact Owner: {person.PersonEntUser}
                    </Text>
                  </View>
                )}

                {/* PR Grade */}
                {person.PRClassName && (
                  <View className="flex-row items-center gap-1.5 bg-pink-950/50 border border-pink-800 px-3 py-1 rounded-full shadow-sm">
                    <Sparkles size={12} color="#f472b6" />
                    <Text className="text-[11px] font-bold text-pink-300 tracking-wide uppercase">
                      PR Grade: {person.PRClassName}
                    </Text>
                  </View>
                )}

                {/* PR Owner */}
                {person.OwnerName ? (
                  <View className="flex-row items-center gap-1.5 bg-indigo-950/50 border border-indigo-800 px-3 py-1 rounded-full shadow-sm">
                    <UserCheck size={12} color={THEME_COLORS.ownerIcon} />
                    <Text className="text-[11px] font-bold text-indigo-300 tracking-wide uppercase">
                      PR Owner: {person.OwnerName}
                    </Text>
                  </View>
                ) : (
                  <View className="flex-row items-center gap-1.5 bg-slate-800/80 border border-slate-700 px-3 py-1 rounded-full shadow-sm">
                    <UserCheck size={12} color={THEME_COLORS.textMuted} />
                    <Text className="text-[11px] font-bold text-slate-400 tracking-wide uppercase">
                      Unassigned PR Owner
                    </Text>
                  </View>
                )}
              </View>
            </View>
          </View>

          {/* Quick Back Action */}
          <Pressable
            onPress={() => router.push("/daylite/person" as Href)}
            className="flex-row items-center gap-1.5 bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg border border-slate-700 self-start sm:self-auto transition-all"
            accessibilityRole="button"
          >
            <ArrowLeft size={13} color={THEME_COLORS.textMuted} />
            <Text className="text-xs font-semibold text-slate-300">Person Directory</Text>
          </Pressable>
        </View>
      </View>

      {/* ── Tab Navigation Bar ─────────────────────────────────── */}
      <View className="flex-row items-center border-b border-dark-border bg-dark-card rounded-t-xl px-2 overflow-x-auto flex-nowrap">
        {tabs.map((t) => {
          const active = activeTab === t.id;
          return (
            <Pressable
              key={t.id}
              onPress={() => setActiveTab(t.id)}
              accessibilityRole="tab"
              accessibilityState={{ selected: active }}
              className={`flex-row items-center gap-1.5 px-3.5 py-2.5 border-b-2 transition-all ${active
                  ? "border-blue-500 bg-blue-500/10"
                  : "border-transparent hover:bg-slate-800/40"
                }`}
            >
              <Text
                className={`text-xs font-semibold ${active ? "text-white font-bold" : "text-slate-400"
                  }`}
              >
                {t.label}
              </Text>
              {t.count !== undefined && t.count > 0 ? (
                <View className="bg-slate-800 border border-slate-700 px-1.5 py-0.2 rounded-full">
                  <Text className="text-[9px] font-mono font-bold text-slate-300">
                    {t.count}
                  </Text>
                </View>
              ) : null}
            </Pressable>
          );
        })}
      </View>

      {/* ── Tab Content Panes ──────────────────────────────────── */}
      <View className="gap-3.5">
        {/* ── TAB 1: Profile & Identity ──────────────────────── */}
        {activeTab === "profile" && (
          <View className="gap-3.5">
            {/* Identity Details */}
            <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
              <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
                <User size={14} color={THEME_COLORS.primaryIcon} />
                <Text className="text-xs font-bold text-white uppercase tracking-wider">
                  Identity & Personal Attributes (dbo.DLPersonMst)
                </Text>
              </View>
              <View className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
                <FieldRow label="Prefix" value={person.PersonPrefix} columnName="PersonPrefix" />
                <FieldRow label="First Name" value={person.PersonFirstName} columnName="PersonFirstName" />
                <FieldRow label="Middle Name" value={person.PersonMiddleName} columnName="PersonMiddleName" />
                <FieldRow label="Last Name" value={person.PersonLastName} columnName="PersonLastName" />
                <FieldRow label="Suffix" value={person.PersonSuffix} columnName="PersonSuffix" />
                <FieldRow label="Nickname" value={person.PersonNickName} columnName="PersonNickName" />
                <FieldRow label="Blood Group" value={person.BloodGroup} columnName="BloodGroup" />
                <FieldRow label="Birth Date" value={person.PersonBirthDate} type="date" columnName="PersonBirthDate" />
                <FieldRow label="Anniversary Date" value={person.PersonAnneversaryDate} type="date" columnName="PersonAnneversaryDate" />
              </View>
            </View>

            {/* Work & Profile Details */}
            <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
              <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
                <Building2 size={14} color={THEME_COLORS.companyIcon} />
                <Text className="text-xs font-bold text-white uppercase tracking-wider">
                  Role, Department & Profile Bio
                </Text>
              </View>
              <View className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
                <FieldRow label="Job Title" value={person.PersonTitle} columnName="PersonTitle" />
                <FieldRow label="Department" value={person.PersonDepartment} columnName="PersonDepartment" />
                <FieldRow label="Employee ID" value={person.EmpID} type="code" columnName="EmpID" />
                <FieldRow label="Candidate ID" value={person.CandidateID} type="code" columnName="CandidateID" />
                <FieldRow label="Category ID" value={person.DLCategoryID} type="code" columnName="DLCategoryID" />
                <FieldRow label="Visitor Category ID" value={person.PersonVisitorCategoryID} type="code" columnName="PersonVisitorCategoryID" />
                <FieldRow label="Keywords" value={person.PersonKeywords} columnName="PersonKeywords" />
                <FieldRow label="Hobbies" value={person.PersonHobbies} columnName="PersonHobbies" />
                <FieldRow label="Approval Status" value={person.ContactApprovalStatus} columnName="ContactApprovalStatus" />
              </View>
              <View className="grid grid-cols-1 md:grid-cols-2 gap-2.5 mt-1">
                <FieldRow label="Person Details / Bio" value={person.PersonDetails} columnName="PersonDetails" />
                <FieldRow label="General Remark" value={person.Remark || person.DLRemark} columnName="Remark" />
              </View>
            </View>

            {/* Safety, Emergency Squad & Device Tracking */}
            <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
              <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
                <Shield size={14} color={THEME_COLORS.warningIcon} />
                <Text className="text-xs font-bold text-white uppercase tracking-wider">
                  Safety Squads & Device Telemetry
                </Text>
              </View>
              <View className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <FieldRow label="Emergency Squad" value={person.IsEmergencySquad} type="boolean" columnName="IsEmergencySquad" />
                <FieldRow label="First Aid Squad" value={person.IsFirstAidSquad} type="boolean" columnName="IsFirstAidSquad" />
                <FieldRow label="Fire Fighter" value={person.IsFireFighter} type="boolean" columnName="IsFireFighter" />
                <FieldRow label="Search & Rescue" value={person.IsSearchandRescue} type="boolean" columnName="IsSearchandRescue" />
              </View>
              <View className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 mt-1">
                <FieldRow label="Device Model" value={person.DeviceModel} columnName="DeviceModel" />
                <FieldRow label="Device Terminal" value={person.DeviceTerm} columnName="DeviceTerm" />
                <FieldRow label="PR Class ID" value={person.PRClassID} type="code" columnName="PRClassID" />
              </View>
            </View>
          </View>
        )}

        {/* ── TAB 2: Contacts & IM ───────────────────────────── */}
        {activeTab === "contacts" && (
          <View className="gap-3.5">
            {/* Phone / Email / URL Table */}
            <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
              <View className="flex-row items-center justify-between pb-2.5 border-b border-dark-border">
                <View className="flex-row items-center gap-2">
                  <Phone size={14} color={THEME_COLORS.successIcon} />
                  <Text className="text-xs font-bold text-white uppercase tracking-wider">
                    Phone, Email & Web Channels ({detail.contacts.length} in dbo.DLPersonPhoneEmailURLDet)
                  </Text>
                </View>
              </View>

              {detail.contacts.length === 0 ? (
                <Text className="text-xs text-slate-500 italic py-3">
                  No contact channels found for Person #{personId}.
                </Text>
              ) : (
                <View className="gap-2.5">
                  {detail.contacts.map((c) => (
                    <View
                      key={c.PersonPhoneID}
                      className="bg-dark-bg/60 border border-dark-border/80 rounded-lg p-3 gap-2.5"
                    >
                      <View className="flex-row items-center justify-between flex-wrap gap-2">
                        <View className="flex-row items-center gap-2">
                          {c.TypeValue?.includes("@") ? (
                            <Mail size={14} color={THEME_COLORS.primaryIcon} />
                          ) : (
                            <Phone size={14} color={THEME_COLORS.successIcon} />
                          )}
                          <Text className="text-sm font-mono font-bold text-white">
                            {c.TypeValue}
                          </Text>
                        </View>
                        <View className="flex-row items-center gap-1.5">
                          <FieldRow label="Primary" value={c.IsPrimary} type="boolean" columnName="IsPrimary" />
                          <FieldRow label="Verified" value={c.IsVerified} type="boolean" columnName="IsVerified" />
                          <FieldRow label="Active" value={c.PersonPhoneIsActive} type="boolean" columnName="PersonPhoneIsActive" />
                        </View>
                      </View>
                      <View className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1 border-t border-dark-border/40">
                        <FieldRow label="Contact ID" value={c.PersonPhoneID} type="code" columnName="PersonPhoneID" />
                        <FieldRow label="Label Type ID" value={c.LabelTypeID} type="code" columnName="LabelTypeID" />
                        <FieldRow label="Notes" value={c.PersonPhoneNotes} columnName="PersonPhoneNotes" />
                        <FieldRow label="Created At" value={c.PersonPhoneEntDt} type="date" columnName="PersonPhoneEntDt" />
                        <FieldRow label="Created By" value={c.PersonPhoneEntUser} columnName="PersonPhoneEntUser" />
                        <FieldRow label="Terminal" value={c.PersonPhoneEntTerm} columnName="PersonPhoneEntTerm" />
                      </View>
                    </View>
                  ))}
                </View>
              )}
            </View>

            {/* Instant Messaging (dbo.DLPersonIMDet) */}
            <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
              <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
                <MessageSquare size={14} color={THEME_COLORS.imIcon} />
                <Text className="text-xs font-bold text-white uppercase tracking-wider">
                  Instant Messaging Handles ({detail.ims.length} in dbo.DLPersonIMDet)
                </Text>
              </View>

              {detail.ims.length === 0 ? (
                <Text className="text-xs text-slate-500 italic py-3">
                  No instant messaging handles found for Person #{personId}.
                </Text>
              ) : (
                <View className="gap-2.5">
                  {detail.ims.map((im) => (
                    <View
                      key={im.PersonIMID}
                      className="bg-dark-bg/60 border border-dark-border/80 rounded-lg p-3 gap-2"
                    >
                      <Text className="text-sm font-mono font-bold text-white">
                        {im.TypeValue}
                      </Text>
                      <View className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1 border-t border-dark-border/40">
                        <FieldRow label="IM ID" value={im.PersonIMID} type="code" columnName="PersonIMID" />
                        <FieldRow label="AIM Label ID" value={im.LabelTypeAIMID} type="code" columnName="LabelTypeAIMID" />
                        <FieldRow label="IM Label ID" value={im.LabelTypeIMID} type="code" columnName="LabelTypeIMID" />
                        <FieldRow label="Notes" value={im.PersonPhoneNotes} columnName="PersonPhoneNotes" />
                        <FieldRow label="Created At" value={im.PersonPhoneEntDt} type="date" columnName="PersonPhoneEntDt" />
                        <FieldRow label="Created By" value={im.PersonPhoneEntUser} columnName="PersonPhoneEntUser" />
                      </View>
                    </View>
                  ))}
                </View>
              )}
            </View>
          </View>
        )}

        {/* ── TAB 3: Addresses ───────────────────────────────── */}
        {activeTab === "addresses" && (
          <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
            <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
              <MapPin size={14} color={THEME_COLORS.warningIcon} />
              <Text className="text-xs font-bold text-white uppercase tracking-wider">
                Physical & Postal Addresses ({detail.addresses.length} in dbo.DLPersonAddressDet)
              </Text>
            </View>

            {detail.addresses.length === 0 ? (
              <Text className="text-xs text-slate-500 italic py-3">
                No address records found in dbo.DLPersonAddressDet for Person #{personId}.
              </Text>
            ) : (
              <View className="gap-3">
                {detail.addresses.map((a) => (
                  <View
                    key={a.PersonAddID}
                    className="bg-dark-bg/60 border border-dark-border/80 rounded-lg p-3.5 gap-3"
                  >
                    <View className="flex-row items-center justify-between flex-wrap gap-2">
                      <Text className="text-sm font-bold text-white font-mono">
                        {a.GoogleFormattedAddress || a.Street || "Address Record"}
                      </Text>
                      <FieldRow label="Active" value={a.PersonAddIsActive} type="boolean" columnName="PersonAddIsActive" />
                    </View>

                    <View className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5">
                      <FieldRow label="Address ID" value={a.PersonAddID} type="code" columnName="PersonAddID" />
                      <FieldRow label="Street" value={a.Street} columnName="Street" />
                      <FieldRow label="City" value={a.CityName} columnName="CityName" />
                      <FieldRow label="City ID" value={a.CityID} type="code" columnName="CityID" />
                      <FieldRow label="State" value={a.StateName} columnName="StateName" />
                      <FieldRow label="State ID" value={a.StateID} type="code" columnName="StateID" />
                      <FieldRow label="Postal Code" value={a.PostalCode} columnName="PostalCode" />
                      <FieldRow label="Country ID" value={a.CountryID} type="code" columnName="CountryID" />
                      <FieldRow label="Latitude" value={a.Latitude} columnName="Latitude" />
                      <FieldRow label="Longitude" value={a.Longitude} columnName="Longitude" />
                      <FieldRow label="Location Map URL" value={a.LocationMapURL} columnName="LocationMapURL" />
                      <FieldRow label="Notes" value={a.Notes} columnName="Notes" />
                    </View>

                    <View className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1 border-t border-dark-border/40">
                      <FieldRow label="Created At" value={a.PersonAddEntDt} type="date" columnName="PersonAddEntDt" />
                      <FieldRow label="Created By" value={a.PresonAddEntUser} columnName="PresonAddEntUser" />
                      <FieldRow label="Terminal" value={a.PersonAddEntTerm} columnName="PersonAddEntTerm" />
                      <FieldRow label="Updated At" value={a.PersonAddUpdDt} type="date" columnName="PersonAddUpdDt" />
                      <FieldRow label="Updated By" value={a.PersonAddUpdUser} columnName="PersonAddUpdUser" />
                      <FieldRow label="Update Terminal" value={a.PersonAddUpdTerm} columnName="PersonAddUpdTerm" />
                    </View>
                  </View>
                ))}
              </View>
            )}
          </View>
        )}

        {/* ── TAB 4: Companies ───────────────────────────────── */}
        {activeTab === "companies" && (
          <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
            <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
              <Building2 size={14} color={THEME_COLORS.companyIcon} />
              <Text className="text-xs font-bold text-white uppercase tracking-wider">
                Company Affiliations ({detail.companies.length} in dbo.DLPersonCompanyLinkDet)
              </Text>
            </View>

            {detail.companies.length === 0 ? (
              <Text className="text-xs text-slate-500 italic py-3">
                No company affiliations recorded for Person #{personId}.
              </Text>
            ) : (
              <View className="gap-3">
                {detail.companies.map((cmp) => (
                  <View
                    key={cmp.PersonLinkID}
                    className="bg-dark-bg/60 border border-dark-border/80 rounded-lg p-3.5 gap-2.5"
                  >
                    <View className="flex-row items-center justify-between flex-wrap gap-2">
                      <Text className="text-base font-bold text-purple-300">
                        {cmp.DLCompName || `Company #${cmp.DLCompID}`}
                      </Text>
                      <FieldRow label="Primary" value={cmp.IsPrimary} type="boolean" columnName="IsPrimary" />
                    </View>
                    <View className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                      <FieldRow label="Link ID" value={cmp.PersonLinkID} type="code" columnName="PersonLinkID" />
                      <FieldRow label="Company ID" value={cmp.DLCompID} type="code" columnName="DLCompID" />
                      <FieldRow label="Role ID" value={cmp.CompPersonRoleID} type="code" columnName="CompPersonRoleID" />
                      <FieldRow label="Created At" value={cmp.PersonLinkEntDt} type="date" columnName="PersonLinkEntDt" />
                      <FieldRow label="Created By" value={cmp.PersonLinkEntUser} columnName="PersonLinkEntUser" />
                      <FieldRow label="Terminal" value={cmp.PersonLinkEntTerm} columnName="PersonLinkEntTerm" />
                      <FieldRow label="Updated At" value={cmp.PersonLinkUpdDt} type="date" columnName="PersonLinkUpdDt" />
                      <FieldRow label="Deleted At" value={cmp.PersonLinkDelDt} type="date" columnName="PersonLinkDelDt" />
                    </View>
                  </View>
                ))}
              </View>
            )}
          </View>
        )}

        {/* ── TAB 5: Relations ───────────────────────────────── */}
        {activeTab === "relations" && (
          <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
            <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
              <HeartHandshake size={14} color={THEME_COLORS.relationIcon} />
              <Text className="text-xs font-bold text-white uppercase tracking-wider">
                Inter-Personal Relationships ({detail.relations.length} in dbo.DLPersonRelationDet)
              </Text>
            </View>

            {detail.relations.length === 0 ? (
              <Text className="text-xs text-slate-500 italic py-3">
                No interpersonal relationship records found for Person #{personId}.
              </Text>
            ) : (
              <View className="gap-3">
                {detail.relations.map((r) => (
                  <View
                    key={r.PersonRelationID}
                    className="bg-dark-bg/60 border border-dark-border/80 rounded-lg p-3.5 gap-2.5"
                  >
                    <View className="flex-row items-center justify-between flex-wrap gap-2">
                      <Text className="text-base font-bold text-pink-300">
                        {r.RelatedPersonName}
                      </Text>
                      <FieldRow label="Deleted" value={r.PersonRelationIsDeleted} type="boolean" columnName="PersonRelationIsDeleted" />
                    </View>
                    <View className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                      <FieldRow label="Relation ID" value={r.PersonRelationID} type="code" columnName="PersonRelationID" />
                      <FieldRow label="Related Person ID" value={r.RelatedPersonID} type="code" columnName="RelatedPersonID" />
                      <FieldRow label="Relation Type ID" value={r.RelationShipTypeID} type="code" columnName="RelationShipTypeID" />
                      <FieldRow label="Relation Detail" value={r.RelationDetail} columnName="RelationDetail" />
                      <FieldRow label="Created At" value={r.PersonRelationEntDt} type="date" columnName="PersonRelationEntDt" />
                      <FieldRow label="Created By" value={r.PersonRelationEntUser} columnName="PersonRelationEntUser" />
                    </View>
                  </View>
                ))}
              </View>
            )}
          </View>
        )}

        {/* ── TAB 6: Custom & Docs ───────────────────────────── */}
        {activeTab === "custom_docs" && (
          <View className="gap-3.5">
            {/* Extra Fields */}
            <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
              <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
                <Sliders size={14} color={THEME_COLORS.ownerIcon} />
                <Text className="text-xs font-bold text-white uppercase tracking-wider">
                  Custom Extra Fields ({detail.extra_fields.length} in dbo.DLPersonExtraFieldValueDet)
                </Text>
              </View>

              {detail.extra_fields.length === 0 ? (
                <Text className="text-xs text-slate-500 italic py-3">
                  No dynamic extra field values recorded for Person #{personId}.
                </Text>
              ) : (
                <View className="gap-2.5">
                  {detail.extra_fields.map((ef) => (
                    <View
                      key={ef.PersonExtraFieldValueID}
                      className="bg-dark-bg/60 border border-dark-border/80 rounded-lg p-3 gap-2"
                    >
                      <View className="flex-row items-center justify-between flex-wrap gap-2">
                        <Text className="text-xs font-mono font-bold text-indigo-300">
                          Field #{ef.ExtraFieldID}: {ef.PersonExtraFieldValue}
                        </Text>
                        <FieldRow label="Active" value={ef.PersonExtraFieldIsActive} type="boolean" columnName="PersonExtraFieldIsActive" />
                      </View>
                      <View className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1 border-t border-dark-border/40">
                        <FieldRow label="Value ID" value={ef.PersonExtraFieldValueID} type="code" columnName="PersonExtraFieldValueID" />
                        <FieldRow label="Deleted" value={ef.PersonExtraFieldIsDeleted} type="boolean" columnName="PersonExtraFieldIsDeleted" />
                        <FieldRow label="Created At" value={ef.PersonExtraFieldEntDt} type="date" columnName="PersonExtraFieldEntDt" />
                        <FieldRow label="Created By" value={ef.PersonExtraFieldEntUser} columnName="PersonExtraFieldEntUser" />
                      </View>
                    </View>
                  ))}
                </View>
              )}
            </View>

            {/* Documents */}
            <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
              <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
                <FileText size={14} color={THEME_COLORS.textMuted} />
                <Text className="text-xs font-bold text-white uppercase tracking-wider">
                  Uploaded Document Attachments ({detail.documents.length} in dbo.DLPersonDocumentDet)
                </Text>
              </View>

              {detail.documents.length === 0 ? (
                <Text className="text-xs text-slate-500 italic py-3">
                  No document attachments recorded for Person #{personId}.
                </Text>
              ) : (
                <View className="gap-2.5">
                  {detail.documents.map((doc) => (
                    <View
                      key={doc.PersonDocID}
                      className="bg-dark-bg/60 border border-dark-border/80 rounded-lg p-3 gap-2"
                    >
                      <Text className="text-sm font-bold text-slate-200">
                        {doc.PersonDocDesc || `Document #${doc.PersonDocID}`} ({doc.PersonDocExtention})
                      </Text>
                      <View className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1 border-t border-dark-border/40">
                        <FieldRow label="Doc ID" value={doc.PersonDocID} type="code" columnName="PersonDocID" />
                        <FieldRow label="Read Only" value={doc.PersonDocIsReadOnly} type="boolean" columnName="PersonDocIsReadOnly" />
                        <FieldRow label="Downloadable" value={doc.PersonDocIsDownloadable} type="boolean" columnName="PersonDocIsDownloadable" />
                        <FieldRow label="Uploaded By" value={doc.PersonDocUploadByUserID} type="code" columnName="PersonDocUploadByUserID" />
                        <FieldRow label="Created At" value={doc.PersonDocEntDt} type="date" columnName="PersonDocEntDt" />
                      </View>
                    </View>
                  ))}
                </View>
              )}
            </View>
          </View>
        )}

        {/* ── TAB 7: Status & Audit ──────────────────────────── */}
        {activeTab === "audit" && (
          <View className="gap-3.5">
            {/* Status & Lifecycle Flags */}
            <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
              <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
                <Activity size={14} color={THEME_COLORS.successIcon} />
                <Text className="text-xs font-bold text-white uppercase tracking-wider">
                  Lifecycle Status & Flags
                </Text>
              </View>
              <View className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <FieldRow
                  label="Active Status"
                  value={person.PersonIsActive ? "Active (1)" : "Inactive (0)"}
                  type="badge"
                  badgeColor={person.PersonIsActive ? "emerald" : "rose"}
                  columnName="PersonIsActive"
                />
                <FieldRow
                  label="Classification"
                  value={
                    person.PersonIsVisitor_Contact === 1
                      ? "Visitor (1)"
                      : person.PersonIsVisitor_Contact === 2
                        ? "Contact (2)"
                        : null
                  }
                  type="badge"
                  badgeColor={person.PersonIsVisitor_Contact === 1 ? "indigo" : "blue"}
                  columnName="PersonIsVisitor_Contact"
                />
                <FieldRow
                  label="Visibility (Share)"
                  value={person.PersonIsShareContact ? "Public (1)" : "Private (0)"}
                  type="badge"
                  badgeColor={person.PersonIsShareContact ? "emerald" : "slate"}
                  columnName="PersonIsShareContact"
                />
                <FieldRow label="Deleted Status" value={person.PersonIsDeleted} type="boolean" columnName="PersonIsDeleted" />
                <FieldRow label="Temporary Status" value={person.PersonIsTemp} type="boolean" columnName="PersonIsTemp" />
                <FieldRow label="Approval Status" value={person.ContactApprovalStatus} columnName="ContactApprovalStatus" />
                <FieldRow label="DL Contact Flag" value={person.DLContactFlag} type="boolean" columnName="DLContactFlag" />
                <FieldRow label="General Flag" value={person.Flag} type="boolean" columnName="Flag" />
              </View>
            </View>

            {/* Blacklist Telemetry */}
            <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
              <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
                <AlertTriangle size={14} color={THEME_COLORS.dangerIcon} />
                <Text className="text-xs font-bold text-white uppercase tracking-wider">
                  Blacklist Telemetry & Governance
                </Text>
              </View>
              <View className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                <FieldRow label="Is Blacklisted" value={person.PersonIsBlackList} type="boolean" columnName="PersonIsBlackList" />
                <FieldRow label="Blacklist Date" value={person.PersonBlackListDate} type="date" columnName="PersonBlackListDate" />
                <FieldRow label="Blacklist Type" value={person.PersonBlackListType} columnName="PersonBlackListType" />
                <FieldRow label="Blacklist Days" value={person.PersonBlackListDays} columnName="PersonBlackListDays" />
                <FieldRow label="HOD Approver ID" value={person.PersonBlackListHODID} type="code" columnName="PersonBlackListHODID" />
                <FieldRow label="HOD Approved" value={person.PersonBlackListHODApprove} type="boolean" columnName="PersonBlackListHODApprove" />
              </View>
            </View>

            {/* Integrations & Sync IDs */}
            <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
              <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
                <Building2 size={14} color={THEME_COLORS.primaryIcon} />
                <Text className="text-xs font-bold text-white uppercase tracking-wider">
                  Integrations & Sync Identifiers
                </Text>
              </View>
              <View className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                <FieldRow label="Zimbra Contact ID" value={person.ZimbraContactID} type="code" columnName="ZimbraContactID" />
                <FieldRow label="Zimbra Revision" value={person.ZimbraContactRev} type="code" columnName="ZimbraContactRev" />
                <FieldRow label="Contact Sync" value={person.IsContactSync} type="boolean" columnName="IsContactSync" />
                <FieldRow label="Update Sync" value={person.IsContactUpdateSync} type="boolean" columnName="IsContactUpdateSync" />
                <FieldRow label="Microsoft 365 User ID" value={person.UserID365} columnName="UserID365" />
                <FieldRow label="System User ID" value={person.UserID} type="code" columnName="UserID" />
              </View>
            </View>

            {/* Contact Ownership & Relationship Management */}
            <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
              <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
                <UserCheck size={14} color={THEME_COLORS.ownerIcon} />
                <Text className="text-xs font-bold text-white uppercase tracking-wider">
                  Contact Ownership & Primary Relationship Owner
                </Text>
              </View>
              <View className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                <FieldRow label="Assigned Owner Name" value={person.OwnerName} columnName="PROwnerEmpID" />
                <FieldRow label="Owner Department" value={person.OwnerDepartment} columnName="PersonDepartment" />
                <FieldRow label="Owner Employee ID" value={person.PROwnerEmpID} type="code" columnName="PROwnerEmpID" />
                <FieldRow label="Owner Approval Status" value={person.PROwnerApprovalStatusID} type="code" columnName="PROwnerApprovalStatusID" />
                <FieldRow label="PR Class ID" value={person.PRClassID} type="code" columnName="PRClassID" />
                <FieldRow label="PR Remarks" value={person.PRRemarks} columnName="PRRemarks" />
              </View>
            </View>

            {/* Ownership Transfer History (dbo.ChangeContactOwnershipTransaction) */}
            {detail.ownership_history && detail.ownership_history.length > 0 && (
              <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
                <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
                  <Clock size={14} color={THEME_COLORS.companyIcon} />
                  <Text className="text-xs font-bold text-white uppercase tracking-wider">
                    Ownership Transfer History ({detail.ownership_history.length} in dbo.ChangeContactOwnershipTransaction)
                  </Text>
                </View>
                <View className="gap-2">
                  {detail.ownership_history.map((h) => (
                    <View key={h.ChangeOwnershipID} className="bg-dark-bg/60 border border-dark-border/80 rounded-lg p-3 gap-2">
                      <View className="flex-row items-center justify-between flex-wrap gap-2">
                        <Text className="text-xs font-bold text-white">
                          Transferred to: <Text className="text-emerald-400">{h.NewOwnerName || `Person #${h.NewPersonID}`}</Text>
                        </Text>
                        <Text className="text-[10px] font-mono text-slate-400">
                          {h.EntDt ? new Date(h.EntDt).toLocaleString() : "—"}
                        </Text>
                      </View>
                      <View className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1 border-t border-dark-border/40">
                        <FieldRow label="Previous Owner" value={h.LastOwnerName || `Person #${h.LastPersonID}`} columnName="LastPersonID" />
                        <FieldRow label="Requested By" value={h.RequestedByName || `Person #${h.RequestedByPersonID}`} columnName="RequestedByPersonID" />
                        <FieldRow label="Executed By User" value={h.EntUser} columnName="EntUser" />
                      </View>
                    </View>
                  ))}
                </View>
              </View>
            )}

            {/* Master Record Audit Trail */}
            <View className="bg-dark-card border border-dark-border rounded-xl p-4 gap-3 shadow-sm">
              <View className="flex-row items-center gap-2 pb-2.5 border-b border-dark-border">
                <FileText size={14} color={THEME_COLORS.textMuted} />
                <Text className="text-xs font-bold text-white uppercase tracking-wider">
                  Entry, Update & Deletion Audit Trail
                </Text>
              </View>
              <View className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                <FieldRow label="Created Date (EntDt)" value={person.PersonEntDt} type="date" columnName="PersonEntDt" />
                <FieldRow label="Created By User (EntUser)" value={person.PersonEntUser} columnName="PersonEntUser" />
                <FieldRow label="Created Terminal (EntTerm)" value={person.PersonEntTerm} columnName="PersonEntTerm" />
                <FieldRow label="Updated Date (UpdDt)" value={person.PersonUpdDt} type="date" columnName="PersonUpdDt" />
                <FieldRow label="Updated By User (UpdUser)" value={person.PersonUpdUser} columnName="PersonUpdUser" />
                <FieldRow label="Updated Terminal (UpdTerm)" value={person.PersonUpdTerm} columnName="PersonUpdTerm" />
                <FieldRow label="Deleted Date (DelDt)" value={person.PersonDelDt} type="date" columnName="PersonDelDt" />
                <FieldRow label="Deleted By User (DelUser)" value={person.PersonDelUser} columnName="PersonDelUser" />
                <FieldRow label="Deleted Terminal (DelTerm)" value={person.PersonDelTerm} columnName="PersonDelTerm" />
              </View>
            </View>
          </View>
        )}
      </View>
    </View>
  );
};
