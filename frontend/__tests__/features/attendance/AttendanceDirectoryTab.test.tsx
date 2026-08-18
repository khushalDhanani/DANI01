import React from "react";
import { render, screen } from "@testing-library/react-native";
import { AttendanceDirectoryTab } from "../../../src/features/modules/attendance/AttendanceDirectoryTab";
import { useAttendanceDirectory } from "../../../src/hooks/useAttendance";

jest.mock("expo-router", () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

jest.mock("../../../src/hooks/useAttendance");


const mockUseAttendanceDirectory = useAttendanceDirectory as jest.Mock;

describe("AttendanceDirectoryTab", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("renders loading state", async () => {
    mockUseAttendanceDirectory.mockReturnValue({
      data: undefined,
      isLoading: true,
      isFetching: false,
    });

    await render(<AttendanceDirectoryTab />);
    expect(screen.getByText("Loading attendance logs...")).toBeTruthy();
  });

  it("renders attendance logs table cleanly", async () => {
    mockUseAttendanceDirectory.mockReturnValue({
      data: {
        total: 1,
        limit: 20,
        offset: 0,
        items: [
          {
            att_id: 101,
            emp_id: 5,
            emp_code: "EMP005",
            emp_name: "Jane Smith",
            att_date: "2026-08-15",
            att_sal_type: "P",
            status_label: "Present",
            in_time: "09:00:00",
            out_time: "18:00:00",
            shift_code: "GS",
            shift_desc: "General Shift",
            late_mins: 0,
            early_mins: 0,
            ot_mins: 0,
            emp_status: "ACTIVE",
          },
        ],
      },
      isLoading: false,
      isFetching: false,
    });

    await render(<AttendanceDirectoryTab />);
    expect(screen.getByText(/Jane Smith/)).toBeTruthy();
    expect(screen.getByText("#101")).toBeTruthy();
    expect(screen.getByText("15-08-2026")).toBeTruthy();
  });
});
