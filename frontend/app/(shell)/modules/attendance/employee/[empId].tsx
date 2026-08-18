import React from "react";
import { useLocalSearchParams } from "expo-router";
import { PageContainer } from "@/components/layout/PageContainer";
import { EmployeeAttendanceAnalyticsView } from "@/features/modules/attendance/EmployeeAttendanceAnalyticsView";
import { ErrorState } from "@/components/ui/ErrorState";

/**
 * Dedicated Full-Page Employee 360 Lifetime Attendance & Leave Analytics Route
 * Path: /modules/attendance/employee/[empId]
 * Loads complete lifecycle attendance, biometric punches, leave breakdown, and HR metrics from joining date to present.
 */
export default function EmployeeAttendanceAnalyticsRoute() {
  const { empId } = useLocalSearchParams<{ empId: string }>();
  const parsedId = empId ? parseInt(empId, 10) : NaN;

  if (isNaN(parsedId)) {
    return (
      <PageContainer>
        <ErrorState
          title="Invalid Employee ID"
          message={`The provided Employee ID "${empId}" is not a valid numerical identifier.`}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer scrollable={true}>
      <EmployeeAttendanceAnalyticsView empId={parsedId} />
    </PageContainer>
  );
}
