import React from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { TablesExplorerView } from "@/features/explorer/TablesExplorerView";

/**
 * Database Explorer Screen (Milestone F4)
 * Provides searching, schema filtering, sorting, and pagination across 970+ tables.
 */
export default function DatabaseScreen() {
  return (
    <PageContainer scrollable={false}>
      <TablesExplorerView />
    </PageContainer>
  );
}
