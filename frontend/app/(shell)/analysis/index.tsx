import React from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { QuickAnalysisView } from "@/features/analysis/QuickAnalysisView";

/**
 * Database-Wide Quick Analysis Route (Milestone F7)
 * /analysis
 */
export default function AnalysisScreen() {
  return (
    <PageContainer scrollable={false}>
      <QuickAnalysisView />
    </PageContainer>
  );
}
