"""
Contact & Email Analysis Module Definition.

Identifies company emails, personal emails, alternate emails, primary/secondary phones,
emergency ICE contacts, postal addresses, social handles, and contact data-quality metrics
across the workforce.
"""

from app.modules.models import (
    ModuleDefinition,
    ModuleRelationshipDefinition,
    ModuleTableDefinition,
    ModuleTableRole,
)

ContactModuleDefinition = ModuleDefinition(
    code="CONTACT",
    name="Contact & Communication Intelligence",
    description=(
        "Discovery, profiling, and quality auditing of employee emails, phone numbers, "
        "emergency ICE contacts, postal addresses, and multi-channel communication profiles."
    ),
    root_schema="dbo",
    root_table="EmployeeMst",
    root_key="EmpID",
    tables=[
        # 1. Canonical Workforce Master
        ModuleTableDefinition(
            schema="dbo",
            table="EmployeeMst",
            role=ModuleTableRole.ROOT,
            required=True,
            key_columns=["EmpID"],
            important_columns=[
                "EmpID",
                "EmpCode",
                "EmpFirstName",
                "EmpMiddleName",
                "EmpLastName",
                "EmpEmailIDCompany",
                "EmpEmailIDPersonal",
                "EmpEmailID2",
                "EmpPhone1",
                "EmpPhone2",
                "EmpCorrPhone1",
                "EmpCorrPhone2",
                "IsVerifiedEmpPhone1",
                "IsVerifiedEmpPhone2",
                "EmpPermCityID",
                "EmpPermStateID",
                "EmpPermPincode",
                "EmpCorrCityID",
                "EmpCorrStateID",
                "EmpCorrPincode",
                "EmpIsActive",
                "EmpIsDeleted",
                "EmpResignDate",
            ],
            description="Canonical employee master containing multi-channel emails, phones, and addresses",
        ),
        # 2. Emergency Contacts
        ModuleTableDefinition(
            schema="dbo",
            table="EmployeeFamilyDet",
            role=ModuleTableRole.CHILD,
            required=False,
            key_columns=["EmpFamilyID"],
            important_columns=[
                "EmpFamilyID",
                "EmpID",
                "FalimyMemFirstName",
                "RelationID",
                "IsICENo",
                "ICEMobileNo",
                "IsICENoVerify",
                "FamilyMemIsActive",
                "FamilyMemIsDeleted",
            ],
            description="Emergency In Case of Emergency (ICE) contacts and family members",
        ),
        # 3. Reference Contacts
        ModuleTableDefinition(
            schema="dbo",
            table="EmployeeReferenceDet",
            role=ModuleTableRole.CHILD,
            required=False,
            key_columns=["EmpReferenceID"],
            important_columns=[
                "EmpReferenceID",
                "EmpID",
                "EmpRefEmailID",
                "EmpRefPhone",
            ],
            description="Employee reference verification email and phone contacts",
        ),
        # 4. Instant Messaging & Social Handles
        ModuleTableDefinition(
            schema="dbo",
            table="EmployeeIMTypeDet",
            role=ModuleTableRole.CHILD,
            required=False,
            key_columns=["IMDetID"],
            important_columns=[
                "IMDetID",
                "EmpID",
                "IMID",
                "IMDesc",
                "IMDetIsDeleted",
            ],
            description="Instant messaging handles and social communication profiles",
        ),
        # 5. Security & Portal Users
        ModuleTableDefinition(
            schema="dbo",
            table="SecurityUserMst",
            role=ModuleTableRole.REFERENCE,
            required=False,
            key_columns=["UserID"],
            important_columns=[
                "UserID",
                "UserEmpID",
                "UserEmail",
                "UserMobile",
                "UserIsActive",
                "UserIsDeleted",
            ],
            description="Application login accounts, notification email and mobile numbers",
        ),
        # 6. Company Registered Contacts
        ModuleTableDefinition(
            schema="dbo",
            table="OrgCompanyMst",
            role=ModuleTableRole.LOOKUP,
            required=False,
            key_columns=["CompID"],
            important_columns=[
                "CompID",
                "CompEmail1",
                "CompEmail2",
                "CompPhoneNo",
                "CompContactNo",
                "CompEmerContactNo",
            ],
            description="Corporate registered office communication channels",
        ),
        # 7. Plant / Site Addresses & Phones
        ModuleTableDefinition(
            schema="dbo",
            table="OrgLocationMst",
            role=ModuleTableRole.LOOKUP,
            required=False,
            key_columns=["LocID"],
            important_columns=[
                "LocID",
                "LocName",
                "LocAddress",
                "CompPhoneNo",
                "GoogleFormattedAddress",
            ],
            description="Manufacturing site physical addresses and facility phone numbers",
        ),
        # 8. Generic Person Phone / Email Store
        ModuleTableDefinition(
            schema="dbo",
            table="DLPersonPhoneEmailURLDet",
            role=ModuleTableRole.DETAIL,
            required=False,
            key_columns=["PersonPhoneID"],
            important_columns=[
                "PersonPhoneID",
                "PersionID",
                "LabelTypeID",
                "TypeValue",
                "IsPrimary",
                "IsVerified",
                "PersonPhoneIsActive",
            ],
            description="Generic person communication endpoints (email, phone, URL, IM)",
        ),
    ],
    relationships=[
        ModuleRelationshipDefinition(
            parent_table="dbo.EmployeeMst",
            child_table="dbo.EmployeeFamilyDet",
            parent_key="EmpID",
            child_key="EmpID",
            relationship_type="ONE_TO_MANY",
            required=False,
        ),
        ModuleRelationshipDefinition(
            parent_table="dbo.EmployeeMst",
            child_table="dbo.EmployeeReferenceDet",
            parent_key="EmpID",
            child_key="EmpID",
            relationship_type="ONE_TO_MANY",
            required=False,
        ),
        ModuleRelationshipDefinition(
            parent_table="dbo.EmployeeMst",
            child_table="dbo.EmployeeIMTypeDet",
            parent_key="EmpID",
            child_key="EmpID",
            relationship_type="ONE_TO_MANY",
            required=False,
        ),
        ModuleRelationshipDefinition(
            parent_table="dbo.EmployeeMst",
            child_table="dbo.SecurityUserMst",
            parent_key="EmpID",
            child_key="UserEmpID",
            relationship_type="ONE_TO_ONE",
            required=False,
        ),
    ],
)
