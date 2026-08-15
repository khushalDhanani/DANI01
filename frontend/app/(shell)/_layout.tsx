import React from "react";
import { Slot } from "expo-router";
import { AppShell } from "@/components/layout/AppShell";

/**
 * Shell group layout.
 *
 * Every route under app/(shell)/ is automatically wrapped in AppShell.
 * This file must stay thin — no business logic.
 */
export default function ShellLayout() {
  return (
    <AppShell>
      <Slot />
    </AppShell>
  );
}
