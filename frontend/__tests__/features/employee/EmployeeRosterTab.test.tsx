import React from "react";
import { render, screen } from "@testing-library/react-native";
import { EmployeeRosterTab } from "@/features/modules/employee/EmployeeRosterTab";
import { useEmployeeRecords } from "@/hooks/useEmployee";

jest.mock("@/hooks/useEmployee", () => ({
  useEmployeeRecords: jest.fn(),
}));

const mockRecords = {
  total: 1316,
  active_count: 1316,
  inactive_count: 0,
  limit: 25,
  offset: 0,
  items: [
    {
      emp_id: 3,
      emp_code: "1002",
      full_name: "Kevin Kiritbhai Shah",
      first_name: "Kevin",
      middle_name: "Kiritbhai",
      last_name: "Shah",
      gender: "M",
      birth_date: "1991-11-24",
      company_email: "kevin@aether.co.in",
      personal_email: "kevin@yahoo.com",
      phone: "+917600817822",
      pan_no: "ENGPS6706C",
      aadhar_no: "476474429318",
      joining_date: "2013-05-04",
      resign_date: null,
      is_active: true,
      is_deleted: false,
      employment_type: "Permanent",
      company_name: "Aether Industries Limited",
      department_name: "Procurement Team",
      designation_name: "Lead Procurement",
      location_name: "Site 1",
      grade_desc: "Grade II",
      functional_mgr_id: 5,
      functional_mgr_name: "Rohan Desai",
      admin_mgr_id: 92,
      admin_mgr_name: "Denish Dodhiyawala",
      user_id: 2,
      user_name: "Kevin Shah",
      user_is_active: true,
      role_desc: "Manager",
    },
  ],
};

describe("EmployeeRosterTab Feature Component", () => {
  beforeEach(() => {
    (useEmployeeRecords as jest.Mock).mockReturnValue({
      data: mockRecords,
      isLoading: false,
    });
  });

  it("renders employee roster items with name, badge, and department", async () => {
    const handleSelect = jest.fn();
    await render(<EmployeeRosterTab onSelectEmployee={handleSelect} />);

    expect(screen.getByText("Kevin Kiritbhai Shah")).toBeTruthy();
    expect(screen.getByText("1002")).toBeTruthy();
    expect(screen.getByText("Procurement Team")).toBeTruthy();
    expect(screen.getByText("Lead Procurement")).toBeTruthy();
    expect(screen.getByText("Rohan Desai")).toBeTruthy();
    expect(screen.getAllByText("ACTIVE").length).toBeGreaterThanOrEqual(1);
  });

  it("renders status filter options and search bar", async () => {
    await render(<EmployeeRosterTab onSelectEmployee={jest.fn()} />);

    expect(screen.getAllByText("ACTIVE").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("INACTIVE")).toBeTruthy();
    expect(screen.getByText("RESIGNED")).toBeTruthy();
    expect(screen.getByText("DELETED")).toBeTruthy();
    expect(screen.getByText("ALL")).toBeTruthy();
  });

  it("renders total record count in footer", async () => {
    await render(<EmployeeRosterTab onSelectEmployee={jest.fn()} />);
    expect(screen.getByText(/Showing 1 - 25 of 1,316 records/)).toBeTruthy();
  });
});
