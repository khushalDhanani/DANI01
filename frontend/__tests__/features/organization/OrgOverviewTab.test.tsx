import React from "react";
import { render, screen } from "@testing-library/react-native";
import { OrgOverviewTab } from "@/features/modules/organization/OrgOverviewTab";
import type { OrgOverviewResponse } from "@/types/organization.types";

const mockOverview: OrgOverviewResponse = {
  scale_counts: {
    total_companies: 2,
    active_companies: 2,
    total_locations: 22,
    active_locations: 18,
    total_main_depts: 26,
    active_main_depts: 26,
    total_departments: 52,
    active_departments: 43,
    total_designations: 389,
    active_designations: 370,
    total_grades: 9,
    active_grades: 9,
    total_active_units: 468,
    total_inactive_units: 32,
  },
  headcount_by_company: [
    { id: 1, name: "Aether Industries Limited", code: "AIL", count: 1225, percentage: 93.1 },
    { id: 2, name: "Aether Speciality Chemicals Limited", code: "ASCL", count: 85, percentage: 6.5 },
  ],
  headcount_by_location: [
    { id: 1, name: "Catalyst", code: "Site 1", count: 387, percentage: 29.4 },
    { id: 2, name: "Genesis", code: "Site 2", count: 384, percentage: 29.2 },
  ],
  headcount_by_top_departments: [
    { id: 24, name: "Maintenance Team - 2 (Parag Detroja)", code: "M2", count: 140, percentage: 10.6 },
    { id: 21, name: "Production Team - 3 (Kalpesh Patel)", code: "P3", count: 133, percentage: 10.1 },
  ],
  headcount_by_grade: [
    { id: 1, name: "Grade I", code: null, count: 15, percentage: 1.1 },
    { id: 2, name: "Grade II", code: null, count: 45, percentage: 3.4 },
  ],
  active_employee_total: 1316,
  generated_at: "2026-08-17T12:00:00Z",
};

describe("OrgOverviewTab Feature Component", () => {
  it("renders loading indicator when isLoading is true", async () => {
    await render(<OrgOverviewTab overview={undefined} isLoading={true} />);
    expect(screen.getByText("Loading organization structure metrics...")).toBeTruthy();
  });

  it("renders corporate scale metrics correctly", async () => {
    await render(<OrgOverviewTab overview={mockOverview} isLoading={false} />);
    expect(screen.getByText("2")).toBeTruthy();
    expect(screen.getByText("22")).toBeTruthy();
    expect(screen.getByText("26")).toBeTruthy();
    expect(screen.getByText("52")).toBeTruthy();
    expect(screen.getByText("389")).toBeTruthy();
    expect(screen.getByText("9")).toBeTruthy();
  });

  it("renders active vs inactive units counts", async () => {
    await render(<OrgOverviewTab overview={mockOverview} isLoading={false} />);
    expect(screen.getByText("468")).toBeTruthy();
    expect(screen.getByText("32")).toBeTruthy();
  });

  it("renders legal entities and staffing distribution", async () => {
    await render(<OrgOverviewTab overview={mockOverview} isLoading={false} />);
    expect(screen.getByText("Aether Industries Limited")).toBeTruthy();
    expect(screen.getByText("AIL")).toBeTruthy();
    expect(screen.getByText("1,225 (93.1%)")).toBeTruthy();
    expect(screen.getByText("Catalyst")).toBeTruthy();
  });
});
