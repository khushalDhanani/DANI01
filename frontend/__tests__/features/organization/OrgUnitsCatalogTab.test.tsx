import React from "react";
import { render, screen } from "@testing-library/react-native";
import { OrgUnitsCatalogTab } from "@/features/modules/organization/OrgUnitsCatalogTab";
import { useOrgUnits } from "@/hooks/useOrganization";

jest.mock("@/hooks/useOrganization", () => ({
  useOrgUnits: jest.fn(),
}));

const mockUnitsData = {
  total: 2,
  limit: 25,
  offset: 0,
  items: [
    {
      unit_id: 1,
      unit_type: "COMPANY",
      unit_code: "AIL",
      unit_name: "Aether Industries Limited",
      parent_id: null,
      parent_name: null,
      head_emp_id: null,
      head_name: null,
      head_code: null,
      active_headcount: 1225,
      is_active: true,
      is_deleted: false,
    },
    {
      unit_id: 1,
      unit_type: "LOCATION",
      unit_code: "Site 1",
      unit_name: "Catalyst",
      parent_id: 1,
      parent_name: "Aether Industries Limited",
      head_emp_id: 864,
      head_name: "Ramesh Maurya",
      head_code: "1799",
      active_headcount: 387,
      is_active: true,
      is_deleted: false,
    },
  ],
};

describe("OrgUnitsCatalogTab Feature Component", () => {
  beforeEach(() => {
    (useOrgUnits as jest.Mock).mockReturnValue({
      data: mockUnitsData,
      isLoading: false,
    });
  });

  it("renders catalog items with unit name, leader, and headcount", async () => {
    await render(<OrgUnitsCatalogTab />);

    expect(screen.getAllByText("Aether Industries Limited").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("AIL")).toBeTruthy();
    expect(screen.getByText("Catalyst")).toBeTruthy();
    expect(screen.getByText("Ramesh Maurya")).toBeTruthy();
    expect(screen.getByText("1,225")).toBeTruthy();
    expect(screen.getByText("387")).toBeTruthy();
  });

  it("renders filter tabs and search bar", async () => {
    await render(<OrgUnitsCatalogTab />);

    expect(screen.getByText("All Units")).toBeTruthy();
    expect(screen.getByText("Companies")).toBeTruthy();
    expect(screen.getByText("Locations")).toBeTruthy();
    expect(screen.getByText("Main Divisions")).toBeTruthy();
    expect(screen.getByText("Departments")).toBeTruthy();
    expect(screen.getByText("Designations")).toBeTruthy();
    expect(screen.getByText("Grades")).toBeTruthy();
  });
});
