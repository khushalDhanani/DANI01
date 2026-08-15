from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PersonListItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True, extra="ignore")

    person_id: int = Field(..., alias="PersonID", description="Unique Person identifier")
    prefix: str | None = Field(default=None, alias="PersonPrefix")
    first_name: str | None = Field(default=None, alias="PersonFirstName")
    middle_name: str | None = Field(default=None, alias="PersonMiddleName")
    last_name: str | None = Field(default=None, alias="PersonLastName")
    suffix: str | None = Field(default=None, alias="PersonSuffix")
    nickname: str | None = Field(default=None, alias="PersonNickName")
    title: str | None = Field(default=None, alias="PersonTitle")
    department: str | None = Field(default=None, alias="PersonDepartment")
    is_active: bool | None = Field(default=None, alias="PersonIsActive")
    is_deleted: bool | None = Field(default=None, alias="PersonIsDeleted")
    is_temp: bool | None = Field(default=None, alias="PersonIsTemp")
    is_blacklist: bool | None = Field(default=None, alias="PersonIsBlackList")
    is_visitor_contact: int | None = Field(
        default=None, alias="PersonIsVisitor_Contact", description="1=Visitor, 2=Contact"
    )
    is_share_contact: bool | None = Field(
        default=None, alias="PersonIsShareContact", description="0=Private, 1=Public"
    )
    created_at: datetime | None = Field(default=None, alias="PersonEntDt")

    # Linked Primary Contact / Reachability Information
    primary_email: str | None = Field(default=None, alias="PrimaryEmail")
    primary_phone: str | None = Field(default=None, alias="PrimaryPhone")
    city: str | None = Field(default=None, alias="CityName")
    state: str | None = Field(default=None, alias="StateName")
    company_name: str | None = Field(default=None, alias="CompanyName")

    # Child Record Counts
    contact_count: int = Field(default=0, alias="ContactCount")
    address_count: int = Field(default=0, alias="AddressCount")
    company_count: int = Field(default=0, alias="CompanyCount")
    relation_count: int = Field(default=0, alias="RelationCount")

    # Contact Owner
    owner_name: str | None = Field(default=None, alias="OwnerName")
    owner_empid: int | None = Field(default=None, alias="PROwnerEmpID")
    pr_class: str | None = Field(default=None, alias="PRClassName")
    person_ent_user: str | None = Field(default=None, alias="PersonEntUser")


class PersonListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True, extra="ignore")

    total: int = Field(..., description="Total matching person records")
    limit: int = Field(..., description="Page size limit")
    offset: int = Field(..., description="Pagination offset")
    items: list[PersonListItem] = Field(default_factory=list, description="Person list items")


# ── Full Comprehensive Single Person Schema (All 8 Tables) ─────────


class PersonFullRootDetail(BaseModel):
    """
    Every column from dbo.DLPersonMst (75 columns).
    """

    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True, extra="ignore")

    # 1. Primary Keys & Identifiers
    PersonID: int = Field(...)
    EmpID: int | None = None
    CandidateID: int | None = None
    DLCategoryID: int | None = None
    PersonVisitorCategoryID: int | None = None
    CreatedForPersonID: int | None = None
    Old_PersonID: int | None = None
    UserID: int | None = None
    DLcontactID: int | None = None

    # 2. Names & Identity
    PersonPrefix: str | None = None
    PersonFirstName: str | None = None
    PersonMiddleName: str | None = None
    PersonLastName: str | None = None
    PersonSuffix: str | None = None
    PersonNickName: str | None = None
    BloodGroup: str | None = None
    PersonBirthDate: datetime | None = None
    PersonAnneversaryDate: datetime | None = None

    # 3. Work, Role & Profile Details
    PersonTitle: str | None = None
    PersonDepartment: str | None = None
    PersonDetails: str | None = None
    PersonKeywords: str | None = None
    PersonHobbies: str | None = None
    Remark: str | None = None
    DLRemark: str | None = None
    TempColumn: str | None = None

    # 4. Status & Life Cycle Flags
    PersonIsActive: bool | None = None
    PersonIsDeleted: bool | None = None
    PersonIsTemp: bool | None = None
    PersonIsShareContact: bool | None = None
    PersonIsVisitor_Contact: int | None = None
    ContactApprovalStatus: int | None = None
    DLContactFlag: bool | None = None
    Flag: bool | None = None

    # 5. Blacklist Telemetry
    PersonIsBlackList: bool | None = None
    PersonBlackListDate: datetime | None = None
    PersonBlackListType: str | None = None
    PersonBlackListDays: int | None = None
    PersonBlackListHODID: int | None = None
    PersonBlackListHODApprove: bool | None = None

    # 6. Safety & Emergency Squad Roles
    IsEmergencySquad: bool | None = None
    IsFirstAidSquad: bool | None = None
    IsFireFighter: bool | None = None
    IsSearchandRescue: bool | None = None

    # 7. PR & Device Tracking
    IsPRContacts: bool | None = None
    PRClassID: int | None = None
    DeviceTerm: str | None = None
    DeviceModel: str | None = None
    PROwnerEmpID: int | None = None
    PROwnerApprovalStatusID: int | None = None
    PRDeliveryStatusID: int | None = None
    PRDeliveryStatusUpdDt: datetime | None = None
    PRRemarks: str | None = None

    # 8. Sync, Ownership & External IDs
    PersonPhotoFileName: str | None = None
    PersonPhotoExt: str | None = None
    IsContactSync: bool | None = None
    IsContactUpdateSync: bool | None = None
    ZimbraContactID: Any | None = None
    ZimbraContactRev: Any | None = None
    UserID365: Any | None = None
    UserCreateDate365: Any | None = None
    UserUpdateDate365: Any | None = None
    RelationWithCreatedUserID: Any | None = None
    OwnerName: str | None = None
    OwnerDepartment: str | None = None
    OwnerPersonID: int | None = None

    # 9. Audit Trail (Entry, Update, Delete)
    CreatedByUserID: int | None = None
    PersonEntDt: datetime | None = None
    PersonEntUser: str | None = None
    PersonEntTerm: str | None = None
    LastModifiedByUserID: int | None = None
    UpdatedByUserID: int | None = None
    PersonUpdDt: datetime | None = None
    PersonUpdUser: str | None = None
    PersonUpdTerm: str | None = None
    PersonDelDt: datetime | None = None
    PersonDelUser: str | None = None
    PersonDelTerm: str | None = None


class PersonAddressDetail(BaseModel):
    """
    Every column from dbo.DLPersonAddressDet (24 columns).
    """

    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True, extra="ignore")

    PersonAddID: int = Field(...)
    PersonID: int | None = None
    LabelTypeID: int | None = None
    Street: str | None = None
    CityName: str | None = None
    CityID: int | None = None
    StateName: str | None = None
    StateID: int | None = None
    PostalCode: str | None = None
    CountryID: int | None = None
    LocationMapURL: str | None = None
    Notes: str | None = None
    PersonAddIsActive: bool | None = None
    Latitude: Any | None = None
    Longitude: Any | None = None
    GoogleFormattedAddress: str | None = None
    SttID: int | None = None
    DayliteImport_AddTemp_RowNo: int | None = None

    # Audit
    PersonAddEntDt: datetime | None = None
    PresonAddEntUser: str | None = None
    PersonAddEntTerm: str | None = None
    PersonAddUpdDt: datetime | None = None
    PersonAddUpdUser: str | None = None
    PersonAddUpdTerm: str | None = None


class PersonContactDetail(BaseModel):
    """
    Every column from dbo.DLPersonPhoneEmailURLDet (14 columns).
    """

    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True, extra="ignore")

    PersonPhoneID: int = Field(...)
    PersionID: int | None = None
    LabelTypeID: int | None = None
    TypeValue: Any | None = None
    PersonPhoneNotes: str | None = None
    IsVerified: bool | None = None
    IsPrimary: bool | None = None
    PersonPhoneIsActive: bool | None = None

    # Audit
    PersonPhoneEntDt: datetime | None = None
    PersonPhoneEntUser: str | None = None
    PersonPhoneEntTerm: str | None = None
    PersonPhoneUpdDt: datetime | None = None
    PersonPhoneUpdUser: str | None = None
    PersonPhoneUpdTerm: str | None = None


class PersonCompanyLinkDetail(BaseModel):
    """
    Every column from dbo.DLPersonCompanyLinkDet (14 columns) + DLCompName.
    """

    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True, extra="ignore")

    PersonLinkID: int = Field(...)
    PersonID: int | None = None
    DLCompID: int | None = None
    DLCompName: str | None = None
    CompPersonRoleID: int | None = None
    IsPrimary: bool | None = None

    # Audit
    PersonLinkEntDt: datetime | None = None
    PersonLinkEntUser: str | None = None
    PersonLinkEntTerm: str | None = None
    PersonLinkUpdDt: datetime | None = None
    PersonLinkUpdUser: str | None = None
    PersonLinkUpdTerm: str | None = None
    PersonLinkDelDt: datetime | None = None
    PersonLinkDelUser: str | None = None
    PersonLinkDelTerm: str | None = None


class PersonRelationDetail(BaseModel):
    """
    Every column from dbo.DLPersonRelationDet (15 columns) + RelatedPersonName.
    """

    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True, extra="ignore")

    PersonRelationID: int = Field(...)
    PersonID: int | None = None
    RelatedPersonID: int | None = None
    RelatedPersonName: str | None = None
    RelationShipTypeID: int | None = None
    RelationDetail: str | None = None
    PersonRelationIsDeleted: bool | None = None

    # Audit
    PersonRelationEntDt: datetime | None = None
    PersonRelationEntUser: str | None = None
    PresonRelationEntTerm: str | None = None
    PersonRelationUpdDt: datetime | None = None
    PersonRelationUpdUser: str | None = None
    PersonRelationUpdTerm: str | None = None
    PersonRelationDelDt: datetime | None = None
    PersonRelationDelUser: str | None = None
    PersonRelationDelTerm: str | None = None


class PersonDocumentDetail(BaseModel):
    """
    Every column from dbo.DLPersonDocumentDet (13 columns).
    """

    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True, extra="ignore")

    PersonDocID: int = Field(...)
    PersonID: int | None = None
    PersonDocExtention: str | None = None
    PersonDocDesc: str | None = None
    PersonDocIsReadOnly: bool | None = None
    PersonDocIsDownloadable: bool | None = None
    PersonDocUploadByUserID: int | None = None

    # Audit
    PersonDocEntDt: datetime | None = None
    PersonDocEntUser: str | None = None
    PersonDocEntTerm: str | None = None
    PersonDocUpdDt: datetime | None = None
    PersonDocUpdUser: str | None = None
    PersonDocUpdTerm: str | None = None


class PersonExtraFieldDetail(BaseModel):
    """
    Every column from dbo.DLPersonExtraFieldValueDet (15 columns).
    """

    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True, extra="ignore")

    PersonExtraFieldValueID: int = Field(...)
    PersonID: int | None = None
    ExtraFieldID: int | None = None
    PersonExtraFieldValue: Any | None = None
    PersonExtraFieldIsActive: bool | None = None
    PersonExtraFieldIsDeleted: bool | None = None

    # Audit
    PersonExtraFieldEntDt: datetime | None = None
    PersonExtraFieldEntUser: str | None = None
    PersonExtraFieldEntTerm: str | None = None
    PersonExtraFieldUpdDt: datetime | None = None
    PersonExtraFieldUpdUser: str | None = None
    PersonExtraFieldUpdTerm: str | None = None
    PersonExtraFieldDelDt: datetime | None = None
    PersonExtraFieldDelUser: str | None = None
    PersonExtraFieldDelTerm: str | None = None


class PersonIMDetail(BaseModel):
    """
    Every column from dbo.DLPersonIMDet (12 columns).
    """

    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True, extra="ignore")

    PersonIMID: int = Field(...)
    PersionID: int | None = None
    LabelTypeAIMID: int | None = None
    LabelTypeIMID: int | None = None
    TypeValue: Any | None = None
    PersonPhoneNotes: str | None = None

    # Audit
    PersonPhoneEntDt: datetime | None = None
    PersonPhoneEntUser: str | None = None
    PersonPhoneEntTerm: str | None = None
    PersonPhoneUpdDt: datetime | None = None
    PersonPhoneUpdUser: str | None = None
    PersonPhoneUpdTerm: str | None = None


class PersonOwnershipHistoryItem(BaseModel):
    """
    Historical Contact Ownership change records from dbo.ChangeContactOwnershipTransaction.
    """

    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True, extra="ignore")

    ChangeOwnershipID: int = Field(...)
    PersonID: int = Field(...)
    LastPersonID: int | None = None
    LastOwnerName: str | None = None
    NewPersonID: int | None = None
    NewOwnerName: str | None = None
    RequestedByPersonID: int | None = None
    RequestedByName: str | None = None
    EntDt: datetime | None = None
    EntUser: str | None = None
    EntTerm: str | None = None


class PersonRecordDetailResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, coerce_numbers_to_str=True, extra="ignore")

    person: PersonFullRootDetail
    addresses: list[PersonAddressDetail] = Field(default_factory=list)
    contacts: list[PersonContactDetail] = Field(default_factory=list)
    companies: list[PersonCompanyLinkDetail] = Field(default_factory=list)
    relations: list[PersonRelationDetail] = Field(default_factory=list)
    documents: list[PersonDocumentDetail] = Field(default_factory=list)
    extra_fields: list[PersonExtraFieldDetail] = Field(default_factory=list)
    ims: list[PersonIMDetail] = Field(default_factory=list)
    ownership_history: list[PersonOwnershipHistoryItem] = Field(default_factory=list)
