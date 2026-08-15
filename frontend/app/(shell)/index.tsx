import React from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { DashboardView } from "@/features/dashboard/DashboardView";

/**
 * Dashboard Screen (Milestone F3)
 * Renders the real-time Database Overview within the application shell.
 */
export default function DashboardScreen() {
  return (
    <PageContainer>
      <DashboardView />
    </PageContainer>
  );
}
