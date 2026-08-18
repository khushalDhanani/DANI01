import React from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { DepartmentSummaryView } from "@/features/modules/attendance/DepartmentSummaryView";

/**
 * Dedicated Full-Page Department Summary Route
 * Path: /modules/attendance/department-summary
 * Renders department-wise summary cards and interactive master table.
 */
export default function DepartmentSummaryRoute() {
  return (
    <PageContainer scrollable={true}>
      <DepartmentSummaryView />
    </PageContainer>
  );
}
