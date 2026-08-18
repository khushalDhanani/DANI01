import React from "react";
import { render, screen } from "@testing-library/react-native";
import { ContactOverviewTab } from "@/features/modules/contact/ContactOverviewTab";
import { useContactOverview } from "@/hooks/useContact";
import type { ContactOverviewResponse } from "@/types/contact.types";

jest.mock("@/hooks/useContact", () => ({
  useContactOverview: jest.fn(),
}));

const mockOverview: ContactOverviewResponse = {
  total_active_employees: 1316,
  email_metrics: {
    total_active_employees: 1316,
    with_company_email: 232,
    with_company_email_pct: 17.6,
    with_personal_email: 1029,
    with_personal_email_pct: 78.2,
    with_alternate_email: 41,
    with_alternate_email_pct: 3.1,
    with_any_email: 1065,
    with_any_email_pct: 80.9,
    without_any_email: 251,
    without_any_email_pct: 19.1,
    without_company_email: 1084,
    without_company_email_pct: 82.4,
    without_personal_email: 287,
    without_personal_email_pct: 21.8,
  },
  phone_metrics: {
    with_primary_phone: 1282,
    with_primary_phone_pct: 97.4,
    with_secondary_phone: 1067,
    with_secondary_phone_pct: 81.1,
    with_corr_phone1: 1297,
    with_corr_phone1_pct: 98.6,
    with_corr_phone2: 1080,
    with_corr_phone2_pct: 82.1,
    with_any_phone: 1299,
    with_any_phone_pct: 98.7,
    without_primary_phone: 34,
    without_primary_phone_pct: 2.6,
    without_any_phone: 17,
    without_any_phone_pct: 1.3,
    primary_phone_verified: 1267,
    primary_phone_verified_pct: 98.8,
    secondary_phone_verified: 1060,
    secondary_phone_verified_pct: 99.3,
  },
  address_metrics: {
    with_permanent_address: 1310,
    with_permanent_address_pct: 99.5,
    with_correspondence_address: 1310,
    with_correspondence_address_pct: 99.5,
    with_permanent_pincode: 1310,
    with_correspondence_pincode: 1310,
    with_ice_emergency_contact: 27,
    with_ice_emergency_contact_pct: 2.1,
  },
  domain_breakdown: [
    { domain: "aether.co.in (Corporate)", count: 219, percentage: 16.6 },
    { domain: "gmail.com (Personal)", count: 1025, percentage: 77.9 },
  ],
  security_user_sync: { total_active_users: 1284 },
  generated_at: "2026-08-17T12:00:00Z",
};

describe("ContactOverviewTab Component", () => {
  it("renders loading indicator when hook is loading", async () => {
    (useContactOverview as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    });

    await render(<ContactOverviewTab />);
    expect(screen.getByText("Loading contact & email intelligence...")).toBeTruthy();
  });

  it("renders multi-channel email, phone, and ICE metrics", async () => {
    (useContactOverview as jest.Mock).mockReturnValue({
      data: mockOverview,
      isLoading: false,
      isError: false,
    });

    await render(<ContactOverviewTab />);
    expect(screen.getByText("Workforce Communication Intelligence")).toBeTruthy();
    expect(screen.getByText("1,065")).toBeTruthy();
    expect(screen.getByText("232")).toBeTruthy();
    expect(screen.getByText("1,029")).toBeTruthy();
    expect(screen.getByText("1,282")).toBeTruthy();
    expect(screen.getByText("27")).toBeTruthy();
    expect(screen.getByText("aether.co.in (Corporate)")).toBeTruthy();
  });
});
