import React from "react";
import { Pressable, Text, View } from "react-native";
import { useRouter } from "expo-router";
import type { Href } from "expo-router";
import {
  Building2,
  CheckCircle2,
  ChevronRight,
  Mail,
  MapPin,
  Phone,
  User,
  UserCheck,
} from "lucide-react-native";
import { THEME_COLORS } from "@/constants/theme";
import type { PersonListItem } from "@/types/modules.types";

interface PersonListItemCardProps {
  person: PersonListItem;
  onPress?: (personId: number) => void;
}

export const PersonListItemCard: React.FC<PersonListItemCardProps> = ({
  person,
  onPress,
}) => {
  const router = useRouter();

  const fullName =
    [
      person.PersonPrefix,
      person.PersonFirstName,
      person.PersonMiddleName,
      person.PersonLastName,
      person.PersonSuffix,
    ]
      .filter(Boolean)
      .join(" ")
      .trim() || `Person #${person.PersonID}`;

  const initials =
    [person.PersonFirstName?.[0], person.PersonLastName?.[0]]
      .filter(Boolean)
      .join("")
      .toUpperCase() || "P";

  const subtitle = [person.PersonTitle, person.PersonDepartment]
    .filter(Boolean)
    .join(" • ")
    .trim();

  const location = [person.CityName, person.StateName]
    .filter(Boolean)
    .join(", ")
    .trim();

  const handlePress = () => {
    if (onPress) {
      onPress(person.PersonID);
    } else {
      router.push(`/daylite/person/${person.PersonID}` as Href);
    }
  };

  return (
    <Pressable
      onPress={handlePress}
      accessibilityRole="button"
      accessibilityLabel={`View full profile for ${fullName}`}
      className="bg-dark-card border border-dark-border hover:border-slate-700 active:bg-slate-900/80 rounded-xl p-3 shadow-sm transition-all flex-col gap-2.5"
    >
      {/* ── Top Row: Avatar, Name, Title, Status ─────────────── */}
      <View className="flex-row items-start justify-between gap-3">
        <View className="flex-row items-center gap-2.5 flex-1 min-w-[200px]">
          {/* Avatar Circle */}
          <View className="w-8 h-8 rounded-full bg-blue-600/20 border border-blue-500/30 items-center justify-center">
            {initials ? (
              <Text className="text-[11px] font-bold text-blue-300">{initials}</Text>
            ) : (
              <User size={14} color={THEME_COLORS.primaryIcon} />
            )}
          </View>

          <View className="flex-1">
            <View className="flex-row items-center gap-1.5 flex-wrap">
              <Text className="text-xs font-bold text-white tracking-tight" numberOfLines={1}>
                {fullName}
              </Text>
              <View className="bg-slate-800/80 px-1.5 py-0.2 rounded border border-slate-700">
                <Text className="text-[9px] font-mono text-slate-400">
                  #{person.PersonID}
                </Text>
              </View>
            </View>

            {subtitle ? (
              <Text className="text-[10px] text-slate-400 mt-0.5" numberOfLines={1}>
                {subtitle}
              </Text>
            ) : null}
          </View>
        </View>

        {/* Status Indicators & Business Mappings */}
        <View className="flex-row items-center gap-1.5 flex-wrap">
          {/* PersonIsActive: 1=Active, 0=Inactive */}
          {person.PersonIsActive ? (
            <View className="flex-row items-center gap-1 bg-emerald-950/60 border border-emerald-800/60 px-2 py-0.5 rounded-full">
              <CheckCircle2 size={10} color={THEME_COLORS.success} />
              <Text className="text-[9px] font-bold text-emerald-300 uppercase">Active</Text>
            </View>
          ) : (
            <View className="bg-slate-900 border border-slate-800 px-2 py-0.5 rounded-full">
              <Text className="text-[9px] font-bold text-slate-400 uppercase">Inactive</Text>
            </View>
          )}

          {/* PersonIsVisitor_Contact: 1=Visitor, 2=Contact */}
          {person.PersonIsVisitor_Contact === 1 ? (
            <View className="bg-indigo-950/60 border border-indigo-800/60 px-1.5 py-0.5 rounded-full">
              <Text className="text-[9px] font-bold text-indigo-300">Visitor</Text>
            </View>
          ) : person.PersonIsVisitor_Contact === 2 ? (
            <View className="bg-blue-950/60 border border-blue-800/60 px-1.5 py-0.5 rounded-full">
              <Text className="text-[9px] font-bold text-blue-300">Contact</Text>
            </View>
          ) : null}

          {/* PersonIsShareContact: 1=Public, 0=Private */}
          {person.PersonIsShareContact ? (
            <View className="bg-teal-950/60 border border-teal-800/60 px-1.5 py-0.5 rounded-full">
              <Text className="text-[9px] font-bold text-teal-300">Public</Text>
            </View>
          ) : (
            <View className="bg-slate-900 border border-slate-700 px-1.5 py-0.5 rounded-full">
              <Text className="text-[9px] font-bold text-slate-400">Private</Text>
            </View>
          )}

          {person.PersonIsTemp ? (
            <View className="bg-amber-950/60 border border-amber-800/60 px-1.5 py-0.5 rounded-full">
              <Text className="text-[9px] font-bold text-amber-300">Temp</Text>
            </View>
          ) : null}

          {person.PersonIsBlackList ? (
            <View className="bg-purple-950/60 border border-purple-800/60 px-1.5 py-0.5 rounded-full">
              <Text className="text-[9px] font-bold text-purple-300">Blacklist</Text>
            </View>
          ) : null}

          {person.PersonIsDeleted ? (
            <View className="bg-rose-950/60 border border-rose-800/60 px-1.5 py-0.5 rounded-full">
              <Text className="text-[9px] font-bold text-rose-300">Deleted</Text>
            </View>
          ) : null}

          <ChevronRight size={14} color={THEME_COLORS.textDark} />
        </View>
      </View>

      {/* ── Middle Row: Reachability Channels & Attributes ──── */}
      <View className="flex-row flex-wrap items-center gap-2 pt-2 border-t border-dark-border/60">
        {/* Email */}
        {person.PrimaryEmail ? (
          <View className="flex-row items-center gap-1 bg-blue-950/40 border border-blue-800/40 px-2 py-0.5 rounded-md">
            <Mail size={11} color={THEME_COLORS.primaryIcon} />
            <Text className="text-[10px] font-mono text-blue-300" numberOfLines={1}>
              {person.PrimaryEmail}
            </Text>
          </View>
        ) : (
          <View className="flex-row items-center gap-1 bg-slate-900/60 px-2 py-0.5 rounded-md">
            <Mail size={11} color={THEME_COLORS.textDisabled} />
            <Text className="text-[10px] text-slate-500 italic">No email</Text>
          </View>
        )}

        {/* Phone */}
        {person.PrimaryPhone ? (
          <View className="flex-row items-center gap-1 bg-emerald-950/40 border border-emerald-800/40 px-2 py-0.5 rounded-md">
            <Phone size={11} color={THEME_COLORS.successIcon} />
            <Text className="text-[10px] font-mono text-emerald-300" numberOfLines={1}>
              {person.PrimaryPhone}
            </Text>
          </View>
        ) : (
          <View className="flex-row items-center gap-1 bg-slate-900/60 px-2 py-0.5 rounded-md">
            <Phone size={11} color={THEME_COLORS.textDisabled} />
            <Text className="text-[10px] text-slate-500 italic">No phone</Text>
          </View>
        )}

        {/* Company Link */}
        {person.CompanyName ? (
          <View className="flex-row items-center gap-1 bg-purple-950/40 border border-purple-800/40 px-2 py-0.5 rounded-md">
            <Building2 size={11} color={THEME_COLORS.companyIcon} />
            <Text className="text-[10px] text-purple-300 font-medium" numberOfLines={1}>
              {person.CompanyName}
            </Text>
          </View>
        ) : null}

        {/* Contact Owner */}
        {person.OwnerName ? (
          <View className="flex-row items-center gap-1 bg-indigo-950/40 border border-indigo-800/40 px-2 py-0.5 rounded-md">
            <UserCheck size={11} color={THEME_COLORS.ownerIcon} />
            <Text className="text-[10px] text-indigo-300 font-medium" numberOfLines={1}>
              Owner: {person.OwnerName}
            </Text>
          </View>
        ) : null}

        {/* Location (City / State) */}
        {location ? (
          <View className="flex-row items-center gap-1 bg-amber-950/40 border border-amber-800/40 px-2 py-0.5 rounded-md">
            <MapPin size={11} color={THEME_COLORS.warningIcon} />
            <Text className="text-[10px] text-amber-300" numberOfLines={1}>
              {location}
            </Text>
          </View>
        ) : null}
      </View>

      {/* ── Footer Row: Counts Metadata ─────────────────────── */}
      <View className="flex-row items-center justify-between pt-1">
        <View className="flex-row items-center gap-2">
          <Text className="text-[10px] text-slate-500 font-mono">
            {person.ContactCount} contacts
          </Text>
          <Text className="text-[10px] text-slate-600">•</Text>
          <Text className="text-[10px] text-slate-500 font-mono">
            {person.AddressCount} addresses
          </Text>
          <Text className="text-[10px] text-slate-600">•</Text>
          <Text className="text-[10px] text-slate-500 font-mono">
            {person.CompanyCount} affiliations
          </Text>
        </View>

        <Text className="text-[9px] text-slate-500 font-mono">
          {person.PersonEntDt ? new Date(person.PersonEntDt).toLocaleDateString() : ""}
        </Text>
      </View>
    </Pressable>
  );
};
