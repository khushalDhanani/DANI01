/**
 * TypeScript interface definitions for Modules domain (PERSON, DAYLITE, etc.)
 */

export interface ModuleTableDefinition {
  schema: string;
  table: string;
  role: "ROOT" | "DETAIL" | "LOOKUP" | "LOG";
  required: boolean;
  key_columns: string[];
  important_columns: string[];
  description: string;
}

export interface ModuleRelationshipDefinition {
  parent_table: string;
  child_table: string;
  parent_key: string;
  child_key: string;
  relationship_type: "ONE_TO_ONE" | "ONE_TO_MANY" | "MANY_TO_MANY";
  required: boolean;
}

export interface ModuleDefinition {
  code: string;
  name: string;
  description: string;
  root_schema: string;
  root_table: string;
  root_key: string;
  tables: ModuleTableDefinition[];
  relationships: ModuleRelationshipDefinition[];
  enabled: boolean;
  tags: string[];
}

export interface ModuleListItem {
  code: string;
  name: string;
  description: string;
  root_table: string;
  table_count: number;
  tags: string[];
  enabled: boolean;
}

export type ModuleInfo = ModuleListItem;

export interface ModuleValidationStatus {
  code: string;
  name: string;
  root_table: string;
  is_valid: boolean;
  status: "READY" | "DEGRADED" | "BROKEN" | "CONFIG_ERROR";
  tables_expected: number;
  tables_found: number;
  tables_missing: number;
  missing_tables: string[];
  warnings: string[];
  errors: string[];
}

export interface TableValidationDetail {
  schema?: string;
  table?: string;
  schema_name?: string;
  table_name?: string;
  role?: string;
  required?: boolean;
  exists?: boolean;
  estimated_rows?: number;
  row_count_estimate?: number;
  column_count?: number;
  missing_columns?: string[];
  status?: "VALID" | "MISSING_TABLE" | "MISSING_COLUMNS" | string;
}

export interface DetailedModuleValidation {
  module_code: string;
  module_name: string;
  is_valid: boolean;
  status: "READY" | "DEGRADED" | "BROKEN" | "CONFIG_ERROR";
  tables_total: number;
  tables_found: number;
  tables_missing: number;
  table_validations: TableValidationDetail[];
  validation_errors: string[];
  validation_warnings: string[];
}

export type ModuleValidationResult = DetailedModuleValidation;

export interface PersonMetricsSummary {
  total_persons: number;
  active_persons?: number | null;
  inactive_persons?: number | null;
  active_percent?: number | null;
  inactive_percent?: number | null;
  deleted_persons?: number | null;
  deleted_percent?: number | null;
  temp_persons?: number | null;
  temp_percent?: number | null;
  blacklist_persons?: number | null;
  blacklist_percent?: number | null;

  // Business Mappings
  visitor_count?: number | null;
  visitor_percent?: number | null;
  contact_entity_count?: number | null;
  contact_entity_percent?: number | null;
  public_count?: number | null;
  public_percent?: number | null;
  private_count?: number | null;
  private_percent?: number | null;

  // Address Coverage
  persons_with_address?: number | null;
  persons_without_address?: number | null;
  address_coverage_percent?: number | null;
  total_addresses?: number | null;

  // Contact Coverage
  persons_with_contact?: number | null;
  persons_without_contact?: number | null;
  contact_coverage_percent?: number | null;
  total_contacts?: number | null;

  // Email & Phone
  persons_with_email?: number | null;
  persons_without_email?: number | null;
  email_coverage_percent?: number | null;
  persons_with_phone?: number | null;
  persons_without_phone?: number | null;
  phone_coverage_percent?: number | null;

  // Company Link
  persons_with_company_link?: number | null;
  persons_without_company_link?: number | null;
  company_link_coverage_percent?: number | null;
  total_company_links?: number | null;

  // Relationships
  persons_with_relationship?: number | null;
  persons_without_relationship?: number | null;
  relationship_coverage_percent?: number | null;
  total_relationships?: number | null;

  // Documents
  persons_with_document?: number | null;
  persons_without_document?: number | null;
  document_coverage_percent?: number | null;
  total_documents?: number | null;

  // Extra Fields
  persons_with_extra_field?: number | null;
  persons_without_extra_field?: number | null;
  extra_field_coverage_percent?: number | null;
  total_extra_fields?: number | null;

  // IM Handles
  persons_with_im?: number | null;
  persons_without_im?: number | null;
  im_coverage_percent?: number | null;
  total_ims?: number | null;

  // Contact Health
  active_contacts?: number | null;
  active_contacts_percent?: number | null;
  verified_contacts?: number | null;
  verified_contacts_percent?: number | null;
  primary_contacts?: number | null;
  primary_contacts_percent?: number | null;

  // Address Health
  active_addresses?: number | null;
  active_addresses_percent?: number | null;
  geo_addresses?: number | null;
  geo_addresses_percent?: number | null;
  formatted_addresses?: number | null;
  formatted_addresses_percent?: number | null;
  postal_addresses?: number | null;
  postal_addresses_percent?: number | null;
}

export interface PersonModuleMetricsResponse {
  module: string;
  status: string;
  root_entity: string;
  metrics: PersonMetricsSummary;
  warnings: string[];
  duration_ms: number;
  calculated_at: string;
}

// ── Person List & Complete Record Detail Interfaces ───────────────

export interface PersonListItem {
  PersonID: number;
  PersonPrefix?: string | null;
  PersonFirstName?: string | null;
  PersonMiddleName?: string | null;
  PersonLastName?: string | null;
  PersonSuffix?: string | null;
  PersonNickName?: string | null;
  PersonTitle?: string | null;
  PersonDepartment?: string | null;
  PersonIsActive?: boolean | null;
  PersonIsDeleted?: boolean | null;
  PersonIsTemp?: boolean | null;
  PersonIsBlackList?: boolean | null;
  PersonEntDt?: string | null;

  // Linked values
  PrimaryEmail?: string | null;
  PrimaryPhone?: string | null;
  CityName?: string | null;
  StateName?: string | null;
  CompanyName?: string | null;

  // Child row counts
  ContactCount: number;
  AddressCount: number;
  CompanyCount: number;
  RelationCount: number;

  // Business Mappings
  PersonIsVisitor_Contact?: number | null; // 1 = Visitor, 2 = Contact
  PersonIsShareContact?: boolean | null; // 0 = Private, 1 = Public

  // Contact Owner
  PROwnerEmpID?: number | null;
  PRClassName?: string | null;
  OwnerName?: string | null;
  PersonEntUser?: string | null;
}

export interface PersonListResponse {
  total: number;
  limit: number;
  offset: number;
  items: PersonListItem[];
}

export interface PersonListParams {
  search?: string;
  status?: "ALL" | "ACTIVE" | "INACTIVE" | "VISITOR" | "CONTACT" | "PUBLIC" | "PRIVATE" | "DELETED" | "TEMP" | "BLACKLIST" | string;
  has_email?: boolean;
  has_phone?: boolean;
  has_address?: boolean;
  has_company?: boolean;
  has_owner?: boolean;
  visitor_contact?: number;
  share_contact?: number | boolean;
  limit?: number;
  offset?: number;
  sort_by?: "PersonID" | "PersonFirstName" | "PersonLastName" | "PersonEntDt" | string;
  sort_order?: "asc" | "desc";
}

/**
 * All 75 columns from dbo.DLPersonMst
 */
export interface PersonFullRootDetail {
  PersonID: number;
  EmpID?: number | null;
  CandidateID?: number | null;
  DLCategoryID?: number | null;
  PersonVisitorCategoryID?: number | null;
  CreatedForPersonID?: number | null;
  Old_PersonID?: number | null;
  UserID?: number | null;

  // Names & Identity
  PersonPrefix?: string | null;
  PersonFirstName?: string | null;
  PersonMiddleName?: string | null;
  PersonLastName?: string | null;
  PersonSuffix?: string | null;
  PersonNickName?: string | null;
  BloodGroup?: string | null;
  PersonBirthDate?: string | null;
  PersonAnneversaryDate?: string | null;

  // Work, Role & Profile
  PersonTitle?: string | null;
  PersonDepartment?: string | null;
  PersonDetails?: string | null;
  PersonKeywords?: string | null;
  PersonHobbies?: string | null;
  Remark?: string | null;
  DLRemark?: string | null;
  TempColumn?: string | null;

  // Status & Flags
  PersonIsActive?: boolean | null;
  PersonIsDeleted?: boolean | null;
  PersonIsTemp?: boolean | null;
  PersonIsShareContact?: boolean | null;
  PersonIsVisitor_Contact?: number | null;
  ContactApprovalStatus?: number | null;
  DLContactFlag?: boolean | null;
  Flag?: boolean | null;

  // Blacklist
  PersonIsBlackList?: boolean | null;
  PersonBlackListDate?: string | null;
  PersonBlackListType?: string | null;
  PersonBlackListDays?: number | null;
  PersonBlackListHODID?: number | null;
  PersonBlackListHODApprove?: boolean | null;

  // Safety & Emergency Squads
  IsEmergencySquad?: boolean | null;
  IsFirstAidSquad?: boolean | null;
  IsFireFighter?: boolean | null;
  IsSearchandRescue?: boolean | null;

  // PR & Devices
  IsPRContacts?: boolean | null;
  PRClassID?: number | null;
  DeviceTerm?: string | null;
  DeviceModel?: string | null;
  PROwnerEmpID?: number | null;
  PRClassName?: string | null;
  PROwnerApprovalStatusID?: number | null;
  OwnerName?: string | null;
  OwnerDepartment?: string | null;
  OwnerPersonID?: number | null;
  PRDeliveryStatusID?: number | null;
  PRDeliveryStatusUpdDt?: string | null;
  PRRemarks?: string | null;

  // Photos & Sync
  PersonPhotoFileName?: string | null;
  PersonPhotoExt?: string | null;
  IsContactSync?: boolean | null;
  ZimbraContactID?: number | null;
  ZimbraContactRev?: number | null;
  IsContactUpdateSync?: boolean | null;
  DLcontactID?: number | null;
  UserID365?: string | null;
  UserCreateDate365?: string | null;
  UserUpdateDate365?: string | null;
  RelationWithCreatedUserID?: string | null;

  // Audit
  CreatedByUserID?: number | null;
  PersonEntDt?: string | null;
  PersonEntUser?: string | null;
  PersonEntTerm?: string | null;
  LastModifiedByUserID?: number | null;
  UpdatedByUserID?: number | null;
  PersonUpdDt?: string | null;
  PersonUpdUser?: string | null;
  PersonUpdTerm?: string | null;
  PersonDelDt?: string | null;
  PersonDelUser?: string | null;
  PersonDelTerm?: string | null;
}

/**
 * All 24 columns from dbo.DLPersonAddressDet
 */
export interface PersonAddressDetail {
  PersonAddID: number;
  PersonID?: number | null;
  LabelTypeID?: number | null;
  Street?: string | null;
  CityName?: string | null;
  CityID?: number | null;
  StateName?: string | null;
  StateID?: number | null;
  PostalCode?: string | null;
  CountryID?: number | null;
  LocationMapURL?: string | null;
  Notes?: string | null;
  PersonAddIsActive?: boolean | null;
  Latitude?: number | null;
  Longitude?: number | null;
  GoogleFormattedAddress?: string | null;
  SttID?: number | null;
  DayliteImport_AddTemp_RowNo?: number | null;

  // Audit
  PersonAddEntDt?: string | null;
  PresonAddEntUser?: string | null;
  PersonAddEntTerm?: string | null;
  PersonAddUpdDt?: string | null;
  PersonAddUpdUser?: string | null;
  PersonAddUpdTerm?: string | null;
}

/**
 * All 14 columns from dbo.DLPersonPhoneEmailURLDet
 */
export interface PersonContactDetail {
  PersonPhoneID: number;
  PersionID?: number | null;
  LabelTypeID?: number | null;
  TypeValue?: string | null;
  PersonPhoneNotes?: string | null;
  IsVerified?: boolean | null;
  IsPrimary?: boolean | null;
  PersonPhoneIsActive?: boolean | null;

  // Audit
  PersonPhoneEntDt?: string | null;
  PersonPhoneEntUser?: string | null;
  PersonPhoneEntTerm?: string | null;
  PersonPhoneUpdDt?: string | null;
  PersonPhoneUpdUser?: string | null;
  PersonPhoneUpdTerm?: string | null;
}

/**
 * All 14 columns from dbo.DLPersonCompanyLinkDet + DLCompName
 */
export interface PersonCompanyLinkDetail {
  PersonLinkID: number;
  PersonID?: number | null;
  DLCompID?: number | null;
  DLCompName?: string | null;
  CompPersonRoleID?: number | null;
  IsPrimary?: boolean | null;

  // Audit
  PersonLinkEntDt?: string | null;
  PersonLinkEntUser?: string | null;
  PersonLinkEntTerm?: string | null;
  PersonLinkUpdDt?: string | null;
  PersonLinkUpdUser?: string | null;
  PersonLinkUpdTerm?: string | null;
  PersonLinkDelDt?: string | null;
  PersonLinkDelUser?: string | null;
  PersonLinkDelTerm?: string | null;
}

/**
 * All 15 columns from dbo.DLPersonRelationDet + RelatedPersonName
 */
export interface PersonRelationDetail {
  PersonRelationID: number;
  PersonID?: number | null;
  RelatedPersonID?: number | null;
  RelatedPersonName?: string | null;
  RelationShipTypeID?: number | null;
  RelationDetail?: string | null;
  PersonRelationIsDeleted?: boolean | null;

  // Audit
  PersonRelationEntDt?: string | null;
  PersonRelationEntUser?: string | null;
  PresonRelationEntTerm?: string | null;
  PersonRelationUpdDt?: string | null;
  PersonRelationUpdUser?: string | null;
  PersonRelationUpdTerm?: string | null;
  PersonRelationDelDt?: string | null;
  PersonRelationDelUser?: string | null;
  PersonRelationDelTerm?: string | null;
}

/**
 * All 13 columns from dbo.DLPersonDocumentDet
 */
export interface PersonDocumentDetail {
  PersonDocID: number;
  PersonID?: number | null;
  PersonDocExtention?: string | null;
  PersonDocDesc?: string | null;
  PersonDocIsReadOnly?: boolean | null;
  PersonDocIsDownloadable?: boolean | null;
  PersonDocUploadByUserID?: number | null;

  // Audit
  PersonDocEntDt?: string | null;
  PersonDocEntUser?: string | null;
  PersonDocEntTerm?: string | null;
  PersonDocUpdDt?: string | null;
  PersonDocUpdUser?: string | null;
  PersonDocUpdTerm?: string | null;
}

/**
 * All 15 columns from dbo.DLPersonExtraFieldValueDet
 */
export interface PersonExtraFieldDetail {
  PersonExtraFieldValueID: number;
  PersonID?: number | null;
  ExtraFieldID?: number | null;
  PersonExtraFieldValue?: string | null;
  PersonExtraFieldIsActive?: boolean | null;
  PersonExtraFieldIsDeleted?: boolean | null;

  // Audit
  PersonExtraFieldEntDt?: string | null;
  PersonExtraFieldEntUser?: string | null;
  PersonExtraFieldEntTerm?: string | null;
  PersonExtraFieldUpdDt?: string | null;
  PersonExtraFieldUpdUser?: string | null;
  PersonExtraFieldUpdTerm?: string | null;
  PersonExtraFieldDelDt?: string | null;
  PersonExtraFieldDelUser?: string | null;
  PersonExtraFieldDelTerm?: string | null;
}

/**
 * All 12 columns from dbo.DLPersonIMDet
 */
export interface PersonIMDetail {
  PersonIMID: number;
  PersionID?: number | null;
  LabelTypeAIMID?: number | null;
  LabelTypeIMID?: number | null;
  TypeValue?: string | null;
  PersonPhoneNotes?: string | null;

  // Audit
  PersonPhoneEntDt?: string | null;
  PersonPhoneEntUser?: string | null;
  PersonPhoneEntTerm?: string | null;
  PersonPhoneUpdDt?: string | null;
  PersonPhoneUpdUser?: string | null;
  PersonPhoneUpdTerm?: string | null;
}

export interface PersonOwnershipHistoryItem {
  ChangeOwnershipID: number;
  PersonID: number;
  LastPersonID?: number | null;
  LastOwnerName?: string | null;
  NewPersonID?: number | null;
  NewOwnerName?: string | null;
  RequestedByPersonID?: number | null;
  RequestedByName?: string | null;
  EntDt?: string | null;
  EntUser?: string | null;
  EntTerm?: string | null;
}

export interface PersonRecordDetailResponse {
  person: PersonFullRootDetail;
  addresses: PersonAddressDetail[];
  contacts: PersonContactDetail[];
  companies: PersonCompanyLinkDetail[];
  relations: PersonRelationDetail[];
  documents: PersonDocumentDetail[];
  extra_fields: PersonExtraFieldDetail[];
  ims: PersonIMDetail[];
  ownership_history?: PersonOwnershipHistoryItem[];
}

// ── Contact Quality Analyzer Interfaces ────────────────────────────

export interface ContactQualitySummary {
  // 1. Contact Channels
  persons_without_email: number;
  persons_without_phone: number;
  invalid_emails: number;
  invalid_phones: number;
  invalid_urls: number;
  unverified_contacts: number;
  duplicate_email_cross_persons: number;
  duplicate_email_same_person: number;
  duplicate_phone_cross_persons: number;
  duplicate_phone_same_person: number;
  persons_multiple_primary: number;
  primary_contact_inactive: number;

  // 2. Address & Location Quality
  addr_missing_postal_code: number;
  addr_invalid_pin_format: number;
  addr_street_without_city: number;
  addr_city_without_state: number;
  addr_missing_geocodes: number;
  addr_duplicate_same_person: number;

  // 3. Profile & Chronological Integrity
  person_anniversary_before_birth: number;
  person_invalid_birth_date: number;
  person_birth_date_ancient: number;
  person_suspicious_dummy_names: number;
  person_missing_lastname_only: number;

  // 4. Employment & Lifecycle Consistency
  active_emp_missing_title: number;
  inactive_with_empid: number;
  status_active_and_deleted: number;
  stale_temp_persons: number;

  // 5. Governance & Blacklist Compliance
  blacklist_unapproved: number;
  blacklist_missing_details: number;

  // 6. Entity Linkages & Child Records
  company_orphan_links: number;
  company_duplicate_links: number;
  company_missing_role: number;
  extra_field_orphan_id: number;
  extra_field_duplicate_entries: number;

  // 7. Audit Trail & Sync Integration
  deleted_missing_del_date: number;
  audit_del_before_ent: number;
  sync_zimbra_missing_id: number;

  // 8. Distinct Person Quality Telemetry (Entity-Level)
  persons_with_critical_issues: number;
  persons_with_warning_issues: number;
  persons_with_any_issue: number;
  total_clean_persons: number;
  health_score_pct: number;

  // 9. Standardized Aggregate Findings (Rule-Level)
  total_critical_findings: number;
  total_warning_findings: number;
  total_info_findings: number;

  // Scope & Metadata (Root Entity: dbo.DLPersonMst)
  total_persons_evaluated: number;
  total_inactive_persons?: number;
  total_deleted_persons?: number;
  related_tables_checked: number;
  calculated_at: string;
  duration_ms: number;
}

export type IssueCountUnit =
  | "PERSON"
  | "CONTACT"
  | "ADDRESS"
  | "COMPANY_LINK"
  | "EXTRA_FIELD"
  | "DUPLICATE_GROUP";

export interface QualityRuleMeta {
  code: string;
  title: string;
  dimension: string;
  severity: "CRITICAL" | "WARNING" | "INFO" | string;
  count_unit: IssueCountUnit;
  unit_label_singular: string;
  unit_label_plural: string;
  description: string;
}

export interface ContactQualityIssueItem {
  PersonID: number;
  PersonName: string;
  ContactID?: number | null;
  ContactType: string;
  LabelName?: string | null;
  CurrentValue?: string | null;
  MaskedValue?: string | null;
  IssueCode: string;
  IssueDescription: string;
  Severity: "CRITICAL" | "WARNING" | "INFO" | string;
  IsVerified?: boolean | null;
  IsPrimary?: boolean | null;
  IsActive?: boolean | null;
}

export interface ContactQualityGroupMember {
  PersonID: number;
  PersonName: string;
  ContactID?: number | null;
  ContactType: string;
  LabelName?: string | null;
  CurrentValue?: string | null;
  MaskedValue?: string | null;
  IssueCode: string;
  IssueDescription: string;
  Severity: "CRITICAL" | "WARNING" | "INFO" | string;
  IsVerified?: boolean | null;
  IsPrimary?: boolean | null;
  IsActive?: boolean | null;
}

export interface ContactQualityGroupItem {
  GroupKey: string;
  GroupLabel: string;
  AffectedPersonsCount: number;
  AffectedRecordsCount: number;
  Members: ContactQualityGroupMember[];
}

export interface ContactQualityIssuesResponse {
  issue: string;
  count_unit?: IssueCountUnit;
  unit_label_singular?: string;
  unit_label_plural?: string;
  total: number;
  total_affected_persons?: number | null;
  total_affected_records?: number | null;
  limit: number;
  offset: number;
  items: ContactQualityIssueItem[];
  groups?: ContactQualityGroupItem[];
  calculated_at?: string;
}

export interface ContactQualityIssueParams {
  issue?: string;
  search?: string;
  sort_by?: "PersonID" | "PersonName" | "CurrentValue" | string;
  sort_order?: "asc" | "desc";
  limit?: number;
  offset?: number;
}

export type QualityCategory = "COMPLETENESS" | "VALIDITY" | "INTEGRITY" | "CONSISTENCY";

export type QualitySeverity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";

export type QualityFindingStatus = "PASSED" | "FAILED" | "WARNING" | "SKIPPED" | "ERROR" | "APPLIED";

export interface QualityFinding {
  rule_code: string;
  category: QualityCategory;
  severity: QualitySeverity;
  title: string;
  description: string;
  affected_count: number;
  total_evaluated: number;
  affected_percent: number;
  exact: boolean;
  message: string;
  status: QualityFindingStatus;
  skip_reason?: string | null;
  sample_records?: Record<string, unknown>[];
}

export interface QualitySeveritySummary {
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
}

export interface PersonQualityResponse {
  module: string;
  status: string;
  rules_evaluated: number;
  rules_skipped: number;
  findings_count: number;
  severity_summary: QualitySeveritySummary;
  findings: QualityFinding[];
  duration_ms: number;
  evaluated_at: string;
}