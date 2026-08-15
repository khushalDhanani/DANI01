import React from "react";
import { useLocalSearchParams } from "expo-router";
import { PageContainer } from "@/components/layout/PageContainer";
import { TableDetailsView } from "@/features/table-details/TableDetailsView";

/**
 * Table Detail Route (Milestone F5)
 * /database/{schema}/{table}
 */
export default function TableDetailRoute() {
  const { schema, table } = useLocalSearchParams<{
    schema: string;
    table: string;
  }>();

  const decodedSchema = decodeURIComponent(schema || "dbo");
  const decodedTable = decodeURIComponent(table || "");

  return (
    <PageContainer scrollable={false}>
      <TableDetailsView schema={decodedSchema} table={decodedTable} />
    </PageContainer>
  );
}
