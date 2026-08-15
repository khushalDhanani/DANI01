import React from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { ContactQualityIssuesView } from "@/features/modules/person/ContactQualityIssuesView";

/**
 * Daylite Contact Quality Issues Explorer Route
 * Path: /daylite/quality
 */
export default function DayliteContactQualityScreen() {
  return (
    <PageContainer scrollable={false}>
      <ContactQualityIssuesView />
    </PageContainer>
  );
}
