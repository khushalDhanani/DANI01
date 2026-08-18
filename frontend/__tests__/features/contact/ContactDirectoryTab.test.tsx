import React from "react";
import { render, screen } from "@testing-library/react-native";
import { ContactDirectoryTab } from "@/features/modules/contact/ContactDirectoryTab";
import { useContactDirectory } from "@/hooks/useContact";
import type { ContactDirectoryListResponse } from "@/types/contact.types";

jest.mock("@/hooks/useContact", () => ({
  useContactDirectory: jest.fn(),
}));

const mockDirectory: ContactDirectoryListResponse = {
  total: 1,
  limit: 25,
  offset: 0,
  items: [
    {
      emp_id: 1,
      emp_code: "1001",
      full_name: "Aman Sharma",
      department: "CIS Team",
      designation: "Technical Leader",
      location: "Catalyst",
      company_email: "aman.sharma@aether.co.in",
      personal_email: "aman@gmail.com",
      alternate_email: null,
      primary_phone: "+919876543210",
      is_verified_phone1: true,
      secondary_phone: "+919876543211",
      is_verified_phone2: false,
      corr_phone1: "+919876543210",
      ice_mobile: "+919876543219",
      ice_contact_name: "Pooja Sharma",
      permanent_pincode: "395007",
      correspondence_pincode: "395007",
      has_valid_email: true,
      has_valid_phone: true,
    },
  ],
};

describe("ContactDirectoryTab Component", () => {
  it("renders loading indicator when directory is loading", async () => {
    (useContactDirectory as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    });

    await render(<ContactDirectoryTab />);
    expect(screen.getByText("Loading workforce contact directory...")).toBeTruthy();
  });

  it("renders employee contact roster card properly", async () => {
    (useContactDirectory as jest.Mock).mockReturnValue({
      data: mockDirectory,
      isLoading: false,
      isError: false,
    });

    await render(<ContactDirectoryTab />);
    expect(screen.getByText("Aman Sharma")).toBeTruthy();
    expect(screen.getByText("1001")).toBeTruthy();
    expect(screen.getByText("aman.sharma@aether.co.in")).toBeTruthy();
    expect(screen.getByText("aman@gmail.com")).toBeTruthy();
    expect(screen.getByText("+919876543210")).toBeTruthy();
    expect(screen.getByText("+919876543219 (Pooja Sharma)")).toBeTruthy();
  });
});
