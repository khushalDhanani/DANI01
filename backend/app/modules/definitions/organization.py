from app.modules.models import (
    ModuleDefinition,
    ModuleRelationshipDefinition,
    ModuleTableDefinition,
    ModuleTableRole,
)

OrganizationModuleDefinition = ModuleDefinition(
    code="ORGANIZATION",
    name="Organization Structure & Hierarchy",
    description=(
        "Comprehensive corporate organizational intelligence covering Companies, Locations/Sites, "
        "Main Functional Divisions, Operational Sub-Departments, Designations/Positions, Grades, "
        "and multi-level Executive Reporting Hierarchies."
    ),
    root_schema="dbo",
    root_table="OrgCompanyMst",
    root_key="CompID",
    tables=[
        # 1. Root Master
        ModuleTableDefinition(
            schema="dbo",
            table="OrgCompanyMst",
            role=ModuleTableRole.ROOT,
            required=True,
            key_columns=["CompID"],
            important_columns=["CompID", "CompCode", "CompName", "CompIsActive", "CompIsDeleted"],
            description="Corporate legal entity master directory",
        ),
        # 2. Location / Site Master
        ModuleTableDefinition(
            schema="dbo",
            table="OrgLocationMst",
            role=ModuleTableRole.LOOKUP,
            required=True,
            key_columns=["LocID"],
            important_columns=[
                "LocID",
                "LocCode",
                "LocName",
                "ShortName",
                "CompID",
                "LocIsActive",
                "LocIsDeleted",
                "SOSSiteHeadEmpID",
                "SAPPlantCode",
            ],
            description="Physical facilities, manufacturing plants, sites, and warehouses",
        ),
        # 3. Main Functional Division
        ModuleTableDefinition(
            schema="dbo",
            table="OrgMainDepartmentMst",
            role=ModuleTableRole.LOOKUP,
            required=True,
            key_columns=["MainDeptID"],
            important_columns=["MainDeptID", "DeptName", "IsActive"],
            description="High-level functional divisions and corporate branches",
        ),
        # 4. Operational Department / Sub-Department
        ModuleTableDefinition(
            schema="dbo",
            table="OrgDepartmentMst",
            role=ModuleTableRole.DETAIL,
            required=True,
            key_columns=["DeptID"],
            important_columns=[
                "DeptID",
                "CompID",
                "DeptName",
                "MainDeptID",
                "DeptHeadEmpID",
                "DeptIsActive",
                "DeptIsDeleted",
                "SAPCostCenterCode",
            ],
            description="Operational sub-teams and functional departments with designated HODs",
        ),
        # 5. Designation / Position Master
        ModuleTableDefinition(
            schema="dbo",
            table="OrgDesignationMst",
            role=ModuleTableRole.DETAIL,
            required=True,
            key_columns=["DesigID"],
            important_columns=[
                "DesigID",
                "CompID",
                "DeptID",
                "MainDeptID",
                "DesigName",
                "DesigType",
                "EmpGradeID",
                "DesigIsActive",
                "DesigIsDeleted",
            ],
            description="Organizational job roles, position titles, and grading criteria",
        ),
        # 6. Executive Grade / Level Master
        ModuleTableDefinition(
            schema="dbo",
            table="EmployeeGradeMst",
            role=ModuleTableRole.LOOKUP,
            required=True,
            key_columns=["EmpGradeID"],
            important_columns=[
                "EmpGradeID",
                "EmpGradeDesc",
                "EmpGradeIsActive",
                "EmpGradeIsDeleted",
            ],
            description="Executive and operational grading bands (Grade 0 through Grade IX)",
        ),
        # 7. Employee Organization Position Mapping (SCD-2)
        ModuleTableDefinition(
            schema="dbo",
            table="EmployeeOfficialDet",
            role=ModuleTableRole.DETAIL,
            required=True,
            key_columns=["EmpOfficeDetID"],
            important_columns=[
                "EmpOfficeDetID",
                "EmpID",
                "LocID",
                "DeptID",
                "DesigID",
                "EmpGradeID",
                "ApplicableFrDate",
                "EmpOfficeDetIsActive",
                "EmpOfficeDetIsDeleted",
            ],
            description="Current and historical employee organizational postings and job assignments",
        ),
        # 8. Designation Reporting Hierarchy Matrix
        ModuleTableDefinition(
            schema="dbo",
            table="OrgDesignationReportingDet",
            role=ModuleTableRole.DETAIL,
            required=False,
            key_columns=["DesigReportingDetID"],
            important_columns=[
                "DesigReportingDetID",
                "CompID",
                "DesigID",
                "ReportingCompID",
                "ReportingDesigID",
                "ReportingType",
                "ReportingIsDefault",
                "ReportingIsActive",
                "ReportingIsDeleted",
            ],
            description="Designation-level functional ('F') and administrative ('A') reporting matrix",
        ),
        # 9. Individual Employee Reporting Line
        ModuleTableDefinition(
            schema="dbo",
            table="EmployeeReportingDet",
            role=ModuleTableRole.DETAIL,
            required=False,
            key_columns=["EmpReportingDetID"],
            important_columns=[
                "EmpReportingDetID",
                "EmpID",
                "ReportingEmpID",
                "DesigID",
                "ReportingDesigID",
                "ReportingDetIsActive",
                "ReportingDetIsDeleted",
            ],
            description="Individual employee reporting assignments to functional/administrative managers",
        ),
    ],
    relationships=[
        # Company -> Location
        ModuleRelationshipDefinition(
            parent_table="dbo.OrgCompanyMst",
            child_table="dbo.OrgLocationMst",
            parent_key="CompID",
            child_key="CompID",
            relationship_type="ONE_TO_MANY",
            confidence="CONFIRMED",
            description="Company owns multiple manufacturing plants and office locations",
        ),
        # Company -> Department
        ModuleRelationshipDefinition(
            parent_table="dbo.OrgCompanyMst",
            child_table="dbo.OrgDepartmentMst",
            parent_key="CompID",
            child_key="CompID",
            relationship_type="ONE_TO_MANY",
            confidence="CONFIRMED",
            description="Company owns multiple operational departments",
        ),
        # Main Department -> Department
        ModuleRelationshipDefinition(
            parent_table="dbo.OrgMainDepartmentMst",
            child_table="dbo.OrgDepartmentMst",
            parent_key="MainDeptID",
            child_key="MainDeptID",
            relationship_type="ONE_TO_MANY",
            confidence="CONFIRMED",
            description="Main functional division groups multiple operational sub-departments",
        ),
        # Department -> Designation
        ModuleRelationshipDefinition(
            parent_table="dbo.OrgDepartmentMst",
            child_table="dbo.OrgDesignationMst",
            parent_key="DeptID",
            child_key="DeptID",
            relationship_type="ONE_TO_MANY",
            confidence="CONFIRMED",
            description="Department establishes role designations and job positions",
        ),
        # Grade -> Designation
        ModuleRelationshipDefinition(
            parent_table="dbo.EmployeeGradeMst",
            child_table="dbo.OrgDesignationMst",
            parent_key="EmpGradeID",
            child_key="EmpGradeID",
            relationship_type="ONE_TO_MANY",
            confidence="CONFIRMED",
            description="Grade band assigned to designation",
        ),
        # Location -> EmployeeOfficialDet
        ModuleRelationshipDefinition(
            parent_table="dbo.OrgLocationMst",
            child_table="dbo.EmployeeOfficialDet",
            parent_key="LocID",
            child_key="LocID",
            relationship_type="ONE_TO_MANY",
            confidence="CONFIRMED",
            description="Location assigned in employee posting record",
        ),
        # Department -> EmployeeOfficialDet
        ModuleRelationshipDefinition(
            parent_table="dbo.OrgDepartmentMst",
            child_table="dbo.EmployeeOfficialDet",
            parent_key="DeptID",
            child_key="DeptID",
            relationship_type="ONE_TO_MANY",
            confidence="CONFIRMED",
            description="Department assigned in employee posting record",
        ),
        # Designation -> EmployeeOfficialDet
        ModuleRelationshipDefinition(
            parent_table="dbo.OrgDesignationMst",
            child_table="dbo.EmployeeOfficialDet",
            parent_key="DesigID",
            child_key="DesigID",
            relationship_type="ONE_TO_MANY",
            confidence="CONFIRMED",
            description="Designation assigned in employee posting record",
        ),
        # EmployeeReportingDet -> EmployeeMst (Manager)
        ModuleRelationshipDefinition(
            parent_table="dbo.EmployeeMst",
            child_table="dbo.EmployeeReportingDet",
            parent_key="EmpID",
            child_key="ReportingEmpID",
            relationship_type="ONE_TO_MANY",
            confidence="CONFIRMED",
            description="Manager reporting line link to employee master",
        ),
    ],
    enabled=True,
    tags=[
        "organization",
        "workforce",
        "structure",
        "company",
        "department",
        "designation",
        "location",
        "hierarchy",
    ],
)
