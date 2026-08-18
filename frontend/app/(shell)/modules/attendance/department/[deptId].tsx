import React from "react";
import { useLocalSearchParams } from "expo-router";
import { PageContainer } from "@/components/layout/PageContainer";
import { DepartmentDetailView } from "@/features/modules/attendance/DepartmentDetailView";
import { ErrorState } from "@/components/ui/ErrorState";

/**
 * Dedicated Full-Page Department Attendance & Leave Detail Route
 * Path: /modules/attendance/department/[deptId]
 * Loads active headcount, daily punches, employee leave applications, and monthly ledgers for a specific department.
 */
export default function DepartmentAttendanceDetailRoute() {
  const { deptId } = useLocalSearchParams<{ deptId: string }>();
  const parsedId = deptId ? parseInt(deptId, 10) : NaN;

  if (isNaN(parsedId)) {
    return (
      <PageContainer>
        <ErrorState
          title="Invalid Department ID"
          message={`The provided Department ID "${deptId}" is not a valid numerical identifier.`}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer scrollable={true}>
      <DepartmentDetailView deptId={parsedId} />
    </PageContainer>
  );
}
