import React from "react";
import { render, screen } from "@testing-library/react-native";
import { AttendanceQualityTab } from "../../../src/features/modules/attendance/AttendanceQualityTab";
import {
  useAttendanceQuality,
  useAttendanceQualityIssues,
} from "../../../src/hooks/useAttendance";

jest.mock("../../../src/hooks/useAttendance");

const mockUseAttendanceQuality = useAttendanceQuality as jest.Mock;
const mockUseAttendanceQualityIssues = useAttendanceQualityIssues as jest.Mock;

describe("AttendanceQualityTab", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders quality audit cards cleanly", async () => {
    mockUseAttendanceQuality.mockReturnValue({
      data: {
        overall_health_score: 95.0,
        critical_issues_count: 0,
        warning_issues_count: 1,
        info_issues_count: 0,
        rules: [
          {
            rule_code: "PUNCH_OUT_BEFORE_IN",
            rule_name: "Punch Out Timestamp Earlier Than Punch In",
            severity: "WARNING",
            description: "Invalid timestamp sequence",
            issue_count: 1,
            impact: "Negative work duration",
            recommendation: "Fix timestamps",
          },
        ],
        summary_by_severity: { CRITICAL: 0, WARNING: 1, INFO: 0 },
      },
      isLoading: false,
      error: null,
    });

    mockUseAttendanceQualityIssues.mockReturnValue({
      data: undefined,
      isLoading: false,
      isFetching: false,
    });

    await render(<AttendanceQualityTab />);
    expect(screen.getByText("Attendance & Leave Quality Index")).toBeTruthy();
    expect(screen.getByText("Punch Out Timestamp Earlier Than Punch In")).toBeTruthy();
  });
});
