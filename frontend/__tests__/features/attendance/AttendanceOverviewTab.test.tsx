import React from "react";
import { render, screen } from "@testing-library/react-native";
import { AttendanceOverviewTab } from "../../../src/features/modules/attendance/AttendanceOverviewTab";
import { useAttendanceOrgHierarchy, useAttendanceOverview } from "../../../src/hooks/useAttendance";

jest.mock("expo-router", () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

jest.mock("../../../src/hooks/useAttendance");


const mockUseAttendanceOverview = useAttendanceOverview as jest.Mock;
const mockUseAttendanceOrgHierarchy = useAttendanceOrgHierarchy as jest.Mock;

describe("AttendanceOverviewTab", () => {
  beforeEach(() => {
    mockUseAttendanceOrgHierarchy.mockReturnValue({
      data: {
        companies: [],
        locations: [],
        departments: [],
        hierarchy_tree: [],
      },
      isLoading: false,
      error: null,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });


  it("renders loading state", async () => {
    mockUseAttendanceOverview.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    });

    await render(<AttendanceOverviewTab />);
    expect(screen.getByText("Loading Attendance & Organizational Hierarchy metrics...")).toBeTruthy();
  });


  it("renders overview metrics cleanly", async () => {
    mockUseAttendanceOverview.mockReturnValue({
      data: {
        attendance_metrics: {
          total_attendance_records: 5000,
          employees_with_attendance: 200,
          present_days: 4000,
          present_pct: 80.0,
          absent_days: 500,
          absent_pct: 10.0,
          half_days: 100,
          half_days_pct: 2.0,
          leave_days: 300,
          leave_days_pct: 6.0,
          weekly_offs: 100,
          paid_holidays: 0,
        },
        punch_metrics: {
          total_punches_logged: 10000,
          valid_punch_pairs: 4800,
          missing_punch_out_count: 50,
          missing_punch_in_count: 10,
          late_arrivals_count: 200,
          early_departures_count: 80,
          overtime_records_count: 300,
          total_overtime_hours: 450.5,
        },
        shift_distribution: [
          {
            shift_id: 1,
            shift_code: "GS",
            shift_description: "General Shift",
            from_time: "09:00:00",
            to_time: "18:00:00",
            assigned_attendance_count: 4500,
            percentage: 90.0,
          },
        ],
      },
      isLoading: false,
      error: null,
    });

    await render(<AttendanceOverviewTab />);
    expect(screen.getByText("5,000")).toBeTruthy();
    expect(screen.getByText("4,000")).toBeTruthy();
    expect(screen.getByText("450.5 hrs")).toBeTruthy();
    expect(screen.getByText("Active Shift Roster Master")).toBeTruthy();
    expect(screen.getByText("General Shift")).toBeTruthy();
  });
});
