import { apiClient } from "@/api/client";
import { procedureLogicApi } from "@/api/procedure_logic.api";

jest.mock("@/api/client", () => ({
  apiClient: {
    get: jest.fn(),
  },
}));

describe("Procedure Logic API Domain Client", () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it("calls getOverview with proper endpoint", async () => {
    const mockOverview = {
      total_sql_objects: 566,
      total_stored_procedures: 450,
      total_functions: 80,
      total_views: 3,
      total_triggers: 33,
      total_inconsistencies: 146,
      critical_inconsistencies_count: 5,
      warning_inconsistencies_count: 10,
      info_inconsistencies_count: 131,
      business_rules: [],
      object_type_distribution: {},
      module_distribution: {},
    };

    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockOverview });

    const result = await procedureLogicApi.getOverview();
    expect(apiClient.get).toHaveBeenCalledWith("/modules/PROCEDURE_LOGIC/overview");
    expect(result).toEqual(mockOverview);
  });

  it("calls getObjects with proper parameters", async () => {
    const mockObjects = {
      items: [],
      total: 0,
      limit: 25,
      offset: 0,
    };

    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockObjects });

    const result = await procedureLogicApi.getObjects({ object_type: "PROCEDURE", search: "Emp" });
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/PROCEDURE_LOGIC/objects?object_type=PROCEDURE&search=Emp"
    );
    expect(result).toEqual(mockObjects);
  });

  it("calls getInconsistencies with proper parameters", async () => {
    const mockIncons = {
      items: [],
      total: 0,
      limit: 25,
      offset: 0,
    };

    (apiClient.get as jest.Mock).mockResolvedValueOnce({ data: mockIncons });

    const result = await procedureLogicApi.getInconsistencies({ severity: "CRITICAL" });
    expect(apiClient.get).toHaveBeenCalledWith(
      "/modules/PROCEDURE_LOGIC/inconsistencies?severity=CRITICAL"
    );
    expect(result).toEqual(mockIncons);
  });
});
