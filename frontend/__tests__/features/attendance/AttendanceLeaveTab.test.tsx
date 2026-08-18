import React from "react";
import { render, screen } from "@testing-library/react-native";
import { AttendanceLeaveTab } from "../../../src/features/modules/attendance/AttendanceLeaveTab";
import {
  useLeaveApplications,
  useLeaveBalances,
  useLeaveOverview,
} from "../../../src/hooks/useAttendance";

jest.mock("../../../src/hooks/useAttendance");

const mockUseLeaveOverview = useLeaveOverview as jest.Mock;
const mockUseLeaveApplications = useLeaveApplications as jest.Mock;
const mockUseLeaveBalances = useLeaveBalances as jest.Mock;

describe("AttendanceLeaveTab", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders leave applications cleanly", async () => {
    mockUseLeaveOverview.mockReturnValue({
      data: {
        total_leave_requests: 10,
        approved_requests: 8,
        approved_pct: 80.0,
        pending_requests: 1,
        pending_pct: 10.0,
        rejected_requests: 1,
        rejected_pct: 10.0,
        cancelled_requests: 0,
        cancelled_pct: 0.0,
        active_employees_on_leave: 2,
        total_employees_with_leave_balance: 15,
        leave_type_distribution: [],
      },
    });

    mockUseLeaveApplications.mockReturnValue({
      data: {
        total: 1,
        limit: 20,
        offset: 0,
        items: [
          {
            leave_request_id: 501,
            emp_id: 5,
            emp_code: "EMP005",
            emp_name: "Jane Smith",
            request_date: "2026-08-10",
            from_date: "2026-08-15",
            to_date: "2026-08-17",
            leave_type_code: "PL",
            leave_type_desc: "Privilege Leave",
            leave_days: 3.0,
            approve_days: 3.0,
            status_id: 13,
            status_desc: "Approved",
            is_cancelled: false,
            reason: "Family event",
          },
        ],
      },
      isLoading: false,
      isFetching: false,
    });

    mockUseLeaveBalances.mockReturnValue({
      data: { total: 0, limit: 20, offset: 0, items: [] },
      isLoading: false,
      isFetching: false,
    });

    await render(<AttendanceLeaveTab />);
    expect(screen.getByText("Total Applications")).toBeTruthy();
    expect(screen.getByText("Jane Smith")).toBeTruthy();
    expect(screen.getByText("Privilege Leave")).toBeTruthy();
  });
});
