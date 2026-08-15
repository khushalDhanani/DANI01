import logging
from typing import Any

from app.db.mssql import execute_readonly_query
from app.modules.person.records_schemas import (
    PersonAddressDetail,
    PersonCompanyLinkDetail,
    PersonContactDetail,
    PersonDocumentDetail,
    PersonExtraFieldDetail,
    PersonFullRootDetail,
    PersonIMDetail,
    PersonListItem,
    PersonListResponse,
    PersonOwnershipHistoryItem,
    PersonRecordDetailResponse,
    PersonRelationDetail,
)

logger = logging.getLogger(__name__)


class PersonRecordsService:
    """
    Service for querying paginated and detailed records from dbo.DLPersonMst and child tables.
    """

    async def get_persons_list(
        self,
        search: str | None = None,
        status: str | None = "ALL",
        has_email: bool | None = None,
        has_phone: bool | None = None,
        has_address: bool | None = None,
        has_company: bool | None = None,
        has_owner: bool | None = None,
        visitor_contact: int | None = None,
        share_contact: int | bool | None = None,
        limit: int = 25,
        offset: int = 0,
        sort_by: str = "PersonID",
        sort_order: str = "desc",
    ) -> PersonListResponse:
        where_clauses: list[str] = []
        params: dict[str, Any] = {}

        # 1. Search Query Filter
        if search and search.strip():
            clean_search = search.strip()
            params["search_pattern"] = f"%{clean_search}%"
            where_clauses.append(
                "("
                "CAST(p.PersonID AS varchar) LIKE :search_pattern OR "
                "ISNULL(p.PersonFirstName, '') + ' ' + ISNULL(p.PersonLastName, '') LIKE :search_pattern OR "
                "p.PersonFirstName LIKE :search_pattern OR "
                "p.PersonLastName LIKE :search_pattern OR "
                "p.PersonNickName LIKE :search_pattern OR "
                "p.PersonTitle LIKE :search_pattern OR "
                "p.PersonDepartment LIKE :search_pattern OR "
                "EXISTS (SELECT 1 FROM dbo.DLPersonPhoneEmailURLDet c WHERE c.PersionID = p.PersonID AND c.TypeValue LIKE :search_pattern) OR "
                "EXISTS (SELECT 1 FROM dbo.DLPersonAddressDet a WHERE a.PersonID = p.PersonID AND (a.CityName LIKE :search_pattern OR a.Street LIKE :search_pattern)) OR "
                "EXISTS (SELECT 1 FROM dbo.DLPersonCompanyLinkDet l JOIN dbo.DLCompanyMst cmp ON l.DLCompID = cmp.DLCompID WHERE l.PersonID = p.PersonID AND cmp.DLCompName LIKE :search_pattern) OR "
                "EXISTS (SELECT 1 FROM dbo.DLPersonMst o WHERE o.EmpID = p.PROwnerEmpID AND (ISNULL(o.PersonFirstName, '') + ' ' + ISNULL(o.PersonLastName, '') LIKE :search_pattern)) OR "
                "EXISTS (SELECT TOP 1 1 FROM dbo.ChangeContactOwnershipTransaction t JOIN dbo.DLPersonMst o ON o.PersonID = t.NewPersonID WHERE t.PersonID = p.PersonID AND (ISNULL(o.PersonFirstName, '') + ' ' + ISNULL(o.PersonLastName, '') LIKE :search_pattern) ORDER BY t.EntDt DESC)"
                ")"
            )

        # 2. Status & Classification Filter (Business Mappings)
        norm_status = (status or "ALL").upper()
        if norm_status == "ACTIVE":
            where_clauses.append("p.PersonIsActive = 1")
        elif norm_status == "INACTIVE":
            where_clauses.append("(p.PersonIsActive = 0 OR p.PersonIsActive IS NULL)")
        elif norm_status == "VISITOR":
            where_clauses.append("p.PersonIsVisitor_Contact = 1")
        elif norm_status == "CONTACT":
            where_clauses.append("p.PersonIsVisitor_Contact = 2")
        elif norm_status == "PUBLIC":
            where_clauses.append("p.PersonIsShareContact = 1")
        elif norm_status == "PRIVATE":
            where_clauses.append("(p.PersonIsShareContact = 0 OR p.PersonIsShareContact IS NULL)")
        elif norm_status == "DELETED":
            where_clauses.append("p.PersonIsDeleted = 1")
        elif norm_status == "TEMP":
            where_clauses.append("p.PersonIsTemp = 1")
        elif norm_status == "BLACKLIST":
            where_clauses.append("p.PersonIsBlackList = 1")

        # Explicit Classification / Visibility filters
        if visitor_contact is not None:
            if visitor_contact == 1:
                where_clauses.append("p.PersonIsVisitor_Contact = 1")
            elif visitor_contact == 2:
                where_clauses.append("p.PersonIsVisitor_Contact = 2")

        if share_contact is not None:
            if share_contact in (1, True, "1", "true", "TRUE"):
                where_clauses.append("p.PersonIsShareContact = 1")
            elif share_contact in (0, False, "0", "false", "FALSE"):
                where_clauses.append("(p.PersonIsShareContact = 0 OR p.PersonIsShareContact IS NULL)")

        # 3. Attribute Presence Filters
        if has_email is True:
            where_clauses.append(
                "EXISTS (SELECT 1 FROM dbo.DLPersonPhoneEmailURLDet WHERE PersionID = p.PersonID AND TypeValue LIKE '%@%')"
            )
        elif has_email is False:
            where_clauses.append(
                "NOT EXISTS (SELECT 1 FROM dbo.DLPersonPhoneEmailURLDet WHERE PersionID = p.PersonID AND TypeValue LIKE '%@%')"
            )

        if has_phone is True:
            where_clauses.append(
                "EXISTS (SELECT 1 FROM dbo.DLPersonPhoneEmailURLDet WHERE PersionID = p.PersonID AND TypeValue NOT LIKE '%@%' AND TypeValue NOT LIKE 'http%' AND TypeValue NOT LIKE 'www%')"
            )
        elif has_phone is False:
            where_clauses.append(
                "NOT EXISTS (SELECT 1 FROM dbo.DLPersonPhoneEmailURLDet WHERE PersionID = p.PersonID AND TypeValue NOT LIKE '%@%' AND TypeValue NOT LIKE 'http%' AND TypeValue NOT LIKE 'www%')"
            )

        if has_address is True:
            where_clauses.append(
                "EXISTS (SELECT 1 FROM dbo.DLPersonAddressDet WHERE PersonID = p.PersonID)"
            )
        elif has_address is False:
            where_clauses.append(
                "NOT EXISTS (SELECT 1 FROM dbo.DLPersonAddressDet WHERE PersonID = p.PersonID)"
            )

        if has_company is True:
            where_clauses.append(
                "EXISTS (SELECT 1 FROM dbo.DLPersonCompanyLinkDet WHERE PersonID = p.PersonID)"
            )
        elif has_company is False:
            where_clauses.append(
                "NOT EXISTS (SELECT 1 FROM dbo.DLPersonCompanyLinkDet WHERE PersonID = p.PersonID)"
            )

        if has_owner is True:
            where_clauses.append("p.PROwnerEmpID IS NOT NULL")
        elif has_owner is False:
            where_clauses.append("p.PROwnerEmpID IS NULL")

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # 4. Count Total Matching Rows
        count_sql = f"SELECT COUNT_BIG(1) AS total FROM dbo.DLPersonMst p {where_sql};"
        count_rows = execute_readonly_query(count_sql, params)
        total_count = int(count_rows[0]["total"]) if count_rows else 0

        if total_count == 0 or offset >= total_count:
            return PersonListResponse(
                total=total_count,
                limit=limit,
                offset=offset,
                items=[],
            )

        # 5. Determine Sort Column & Direction (whitelist protected against SQL injection)
        valid_sort_cols = {
            "personid": "p.PersonID",
            "personfirstname": "p.PersonFirstName",
            "personlastname": "p.PersonLastName",
            "personentdt": "p.PersonEntDt",
        }
        order_col = valid_sort_cols.get((sort_by or "").lower().strip(), "p.PersonID")
        order_dir = "ASC" if (sort_order or "").lower().strip() == "asc" else "DESC"

        # 6. Fetch Paginated Records with Related Counts and Resolved Owner
        params["limit"] = max(1, min(100, limit))
        params["offset"] = max(0, offset)

        items_sql = f"""
        SELECT 
            p.PersonID,
            p.PersonPrefix,
            p.PersonFirstName,
            p.PersonMiddleName,
            p.PersonLastName,
            p.PersonSuffix,
            p.PersonNickName,
            p.PersonTitle,
            p.PersonDepartment,
            p.PersonIsActive,
            p.PersonIsDeleted,
            p.PersonIsTemp,
            p.PersonIsBlackList,
            p.PersonIsVisitor_Contact,
            p.PersonIsShareContact,
            p.PersonEntDt,
            p.PersonEntUser,
            p.PROwnerEmpID,
            COALESCE(
                NULLIF(LTRIM(RTRIM(ISNULL(owner_p.PersonFirstName, '') + ' ' + ISNULL(owner_p.PersonLastName, ''))), ''),
                (
                    SELECT TOP 1 ISNULL(NULLIF(LTRIM(RTRIM(ISNULL(new_p.PersonFirstName, '') + ' ' + ISNULL(new_p.PersonLastName, ''))), ''), 'Person #' + CAST(t.NewPersonID AS varchar))
                    FROM dbo.ChangeContactOwnershipTransaction t
                    LEFT JOIN dbo.DLPersonMst new_p ON new_p.PersonID = t.NewPersonID
                    WHERE t.PersonID = p.PersonID
                    ORDER BY t.EntDt DESC, t.ChangeOwnershipID DESC
                )
            ) AS OwnerName,
            (
                SELECT TOP 1 ISNULL(NULLIF(LTRIM(RTRIM(ISNULL(new_p.PersonFirstName, '') + ' ' + ISNULL(new_p.PersonLastName, ''))), ''), 'Person #' + CAST(t.NewPersonID AS varchar))
                FROM dbo.ChangeContactOwnershipTransaction t
                LEFT JOIN dbo.DLPersonMst new_p ON new_p.PersonID = t.NewPersonID
                WHERE t.PersonID = p.PersonID
                ORDER BY t.EntDt DESC, t.ChangeOwnershipID DESC
            ) AS FallbackOwnerName,
            (SELECT TOP 1 TypeValue FROM dbo.DLPersonPhoneEmailURLDet WHERE PersionID = p.PersonID AND TypeValue LIKE '%@%') AS PrimaryEmail,
            (SELECT TOP 1 TypeValue FROM dbo.DLPersonPhoneEmailURLDet WHERE PersionID = p.PersonID AND TypeValue NOT LIKE '%@%' AND TypeValue NOT LIKE 'http%' AND TypeValue NOT LIKE 'www%') AS PrimaryPhone,
            (SELECT TOP 1 CityName FROM dbo.DLPersonAddressDet WHERE PersonID = p.PersonID) AS CityName,
            (SELECT TOP 1 StateName FROM dbo.DLPersonAddressDet WHERE PersonID = p.PersonID) AS StateName,
            (SELECT TOP 1 c.DLCompName FROM dbo.DLPersonCompanyLinkDet l JOIN dbo.DLCompanyMst c ON l.DLCompID = c.DLCompID WHERE l.PersonID = p.PersonID) AS CompanyName,
            (SELECT TOP 1 pr.PRClassName FROM dbo.PRClassMst pr WHERE pr.PRClassID = p.PRClassID) AS PRClassName,
            (SELECT COUNT_BIG(1) FROM dbo.DLPersonPhoneEmailURLDet WHERE PersionID = p.PersonID) AS ContactCount,
            (SELECT COUNT_BIG(1) FROM dbo.DLPersonAddressDet WHERE PersonID = p.PersonID) AS AddressCount,
            (SELECT COUNT_BIG(1) FROM dbo.DLPersonCompanyLinkDet WHERE PersonID = p.PersonID) AS CompanyCount,
            (SELECT COUNT_BIG(1) FROM dbo.DLPersonRelationDet WHERE PersonID = p.PersonID OR RelatedPersonID = p.PersonID) AS RelationCount
        FROM dbo.DLPersonMst p
        LEFT JOIN dbo.DLPersonMst owner_p ON owner_p.EmpID = p.PROwnerEmpID
        {where_sql}
        ORDER BY {order_col} {order_dir}
        OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY;
        """

        rows = execute_readonly_query(items_sql, params)
        for r in rows:
            if r.get("PROwnerEmpID") is None and r.get("FallbackOwnerName") is not None:
                logger.warning(
                    f"Data Integrity Issue: PersonID {r.get('PersonID')} has no PROwnerEmpID on master record, "
                    f"but has ownership history. Fallback Owner '{r.get('FallbackOwnerName')}' used."
                )

        items = [PersonListItem.model_validate(r) for r in rows]

        return PersonListResponse(
            total=total_count,
            limit=limit,
            offset=offset,
            items=items,
        )

    async def get_person_detail(self, person_id: int) -> PersonRecordDetailResponse | None:
        """
        Fetches a single person entity with all associated child table rows.
        Includes all 75 columns from dbo.DLPersonMst and all columns from all 7 child tables.
        """
        # 1. Root entity (all 75 columns from dbo.DLPersonMst)
        person_sql = """
        SELECT 
            p.PersonID,
            p.PersonPrefix,
            p.PersonFirstName,
            p.PersonMiddleName,
            p.PersonLastName,
            p.PersonSuffix,
            p.PersonNickName,
            p.EmpID,
            p.PersonIsActive,
            p.PersonIsDeleted,
            p.PersonIsTemp,
            p.PersonIsShareContact,
            p.PersonIsVisitor_Contact,
            p.ContactApprovalStatus,
            p.DLCategoryID,
            p.PersonVisitorCategoryID,
            p.CreatedByUserID,
            p.PersonEntDt,
            p.PersonEntUser,
            p.PersonEntTerm,
            p.LastModifiedByUserID,
            p.PersonUpdDt,
            p.PersonUpdUser,
            p.PersonUpdTerm,
            p.IsContactSync,
            p.ZimbraContactID,
            p.ZimbraContactRev,
            p.PersonPhotoFileName,
            p.PersonPhotoExt,
            p.PersonKeywords,
            p.PersonTitle,
            p.PersonDepartment,
            p.PersonDetails,
            p.PersonHobbies,
            p.PersonBirthDate,
            p.PersonAnneversaryDate,
            p.RelationWithCreatedUserID,
            p.PersonIsBlackList,
            p.PersonBlackListDate,
            p.PersonBlackListType,
            p.PersonBlackListDays,
            p.PersonBlackListHODID,
            p.PersonBlackListHODApprove,
            p.PersonDelDt,
            p.PersonDelUser,
            p.PersonDelTerm,
            p.CandidateID,
            p.Remark,
            p.IsContactUpdateSync,
            p.DLcontactID,
            p.IsEmergencySquad,
            p.IsFirstAidSquad,
            p.IsFireFighter,
            p.IsSearchandRescue,
            p.CreatedForPersonID,
            p.Old_PersonID,
            p.DLContactFlag,
            p.DLRemark,
            p.TempColumn,
            p.UpdatedByUserID,
            p.BloodGroup,
            p.UserID365,
            p.UserCreateDate365,
            p.UserUpdateDate365,
            p.UserID,
            p.Flag,
            p.IsPRContacts,
            p.PRClassID,
            (SELECT TOP 1 pr.PRClassName FROM dbo.PRClassMst pr WHERE pr.PRClassID = p.PRClassID) AS PRClassName,
            p.DeviceTerm,
            p.DeviceModel,
            p.PROwnerEmpID,
            p.PROwnerApprovalStatusID,
            COALESCE(
                NULLIF(LTRIM(RTRIM(ISNULL(owner_p.PersonFirstName, '') + ' ' + ISNULL(owner_p.PersonLastName, ''))), ''),
                (
                    SELECT TOP 1 ISNULL(NULLIF(LTRIM(RTRIM(ISNULL(new_p.PersonFirstName, '') + ' ' + ISNULL(new_p.PersonLastName, ''))), ''), 'Person #' + CAST(t.NewPersonID AS varchar))
                    FROM dbo.ChangeContactOwnershipTransaction t
                    LEFT JOIN dbo.DLPersonMst new_p ON new_p.PersonID = t.NewPersonID
                    WHERE t.PersonID = p.PersonID
                    ORDER BY t.EntDt DESC, t.ChangeOwnershipID DESC
                )
            ) AS OwnerName,
            (
                SELECT TOP 1 ISNULL(NULLIF(LTRIM(RTRIM(ISNULL(new_p.PersonFirstName, '') + ' ' + ISNULL(new_p.PersonLastName, ''))), ''), 'Person #' + CAST(t.NewPersonID AS varchar))
                FROM dbo.ChangeContactOwnershipTransaction t
                LEFT JOIN dbo.DLPersonMst new_p ON new_p.PersonID = t.NewPersonID
                WHERE t.PersonID = p.PersonID
                ORDER BY t.EntDt DESC, t.ChangeOwnershipID DESC
            ) AS FallbackOwnerName,
            owner_p.PersonDepartment AS OwnerDepartment,
            owner_p.PersonID AS OwnerPersonID,
            p.PRDeliveryStatusID,
            p.PRDeliveryStatusUpdDt,
            p.PRRemarks
        FROM dbo.DLPersonMst p
        LEFT JOIN dbo.DLPersonMst owner_p ON owner_p.EmpID = p.PROwnerEmpID
        WHERE p.PersonID = :person_id;
        """
        p_res = execute_readonly_query(person_sql, {"person_id": person_id})
        if not p_res:
            return None

        row = p_res[0]
        if row.get("PROwnerEmpID") is None and row.get("FallbackOwnerName") is not None:
            logger.warning(
                f"Data Integrity Issue: PersonID {row.get('PersonID')} has no PROwnerEmpID on master record, "
                f"but has ownership history. Fallback Owner '{row.get('FallbackOwnerName')}' used."
            )

        person_item = PersonFullRootDetail.model_validate(row)

        # 2. Addresses (all 24 columns from dbo.DLPersonAddressDet)
        addr_sql = """
        SELECT 
            PersonAddID, PersonID, LabelTypeID, Street, CityName, CityID, StateName, StateID,
            PostalCode, CountryID, LocationMapURL, Notes, PersonAddIsActive,
            PersonAddEntDt, PresonAddEntUser, PersonAddEntTerm,
            PersonAddUpdDt, PersonAddUpdUser, PersonAddUpdTerm,
            Latitude, Longitude, GoogleFormattedAddress,
            DayliteImport_AddTemp_RowNo, SttID
        FROM dbo.DLPersonAddressDet
        WHERE PersonID = :person_id;
        """
        addrs = [PersonAddressDetail.model_validate(r) for r in execute_readonly_query(addr_sql, {"person_id": person_id})]

        # 3. Contacts (all 14 columns from dbo.DLPersonPhoneEmailURLDet)
        contact_sql = """
        SELECT 
            PersonPhoneID, PersionID, LabelTypeID, TypeValue, PersonPhoneNotes, IsVerified,
            PersonPhoneEntDt, PersonPhoneEntUser, PersonPhoneEntTerm,
            PersonPhoneUpdDt, PersonPhoneUpdUser, PersonPhoneUpdTerm,
            PersonPhoneIsActive, IsPrimary
        FROM dbo.DLPersonPhoneEmailURLDet
        WHERE PersionID = :person_id;
        """
        contacts = [PersonContactDetail.model_validate(r) for r in execute_readonly_query(contact_sql, {"person_id": person_id})]

        # 4. Companies (all 14 columns from dbo.DLPersonCompanyLinkDet + DLCompName)
        comp_sql = """
        SELECT 
            l.PersonLinkID, l.PersonID, l.DLCompID, c.DLCompName, l.CompPersonRoleID, l.IsPrimary,
            l.PersonLinkEntDt, l.PersonLinkEntUser, l.PersonLinkEntTerm,
            l.PersonLinkUpdDt, l.PersonLinkUpdUser, l.PersonLinkUpdTerm,
            l.PersonLinkDelDt, l.PersonLinkDelUser, l.PersonLinkDelTerm
        FROM dbo.DLPersonCompanyLinkDet l
        LEFT JOIN dbo.DLCompanyMst c ON l.DLCompID = c.DLCompID
        WHERE l.PersonID = :person_id;
        """
        companies = [PersonCompanyLinkDetail.model_validate(r) for r in execute_readonly_query(comp_sql, {"person_id": person_id})]

        # 5. Relations (all 15 columns from dbo.DLPersonRelationDet + RelatedPersonName)
        rel_sql = """
        SELECT 
            r.PersonRelationID, r.PersonID, r.RelatedPersonID,
            ISNULL(NULLIF(LTRIM(RTRIM(ISNULL(p2.PersonFirstName, '') + ' ' + ISNULL(p2.PersonLastName, ''))), ''), 'Person #' + CAST(r.RelatedPersonID AS varchar)) AS RelatedPersonName,
            r.RelationShipTypeID, r.RelationDetail, r.PersonRelationIsDeleted,
            r.PersonRelationEntDt, r.PersonRelationEntUser, r.PresonRelationEntTerm,
            r.PersonRelationUpdDt, r.PersonRelationUpdUser, r.PersonRelationUpdTerm,
            r.PersonRelationDelDt, r.PersonRelationDelUser, r.PersonRelationDelTerm
        FROM dbo.DLPersonRelationDet r
        LEFT JOIN dbo.DLPersonMst p2 ON r.RelatedPersonID = p2.PersonID
        WHERE r.PersonID = :person_id;
        """
        relations = [PersonRelationDetail.model_validate(r) for r in execute_readonly_query(rel_sql, {"person_id": person_id})]

        # 6. Documents (all 13 columns from dbo.DLPersonDocumentDet)
        doc_sql = """
        SELECT 
            PersonDocID, PersonID, PersonDocExtention, PersonDocDesc, PersonDocIsReadOnly,
            PersonDocIsDownloadable, PersonDocUploadByUserID,
            PersonDocEntDt, PersonDocEntUser, PersonDocEntTerm,
            PersonDocUpdDt, PersonDocUpdUser, PersonDocUpdTerm
        FROM dbo.DLPersonDocumentDet
        WHERE PersonID = :person_id;
        """
        documents = [PersonDocumentDetail.model_validate(r) for r in execute_readonly_query(doc_sql, {"person_id": person_id})]

        # 7. Extra Fields (all 15 columns from dbo.DLPersonExtraFieldValueDet)
        extra_sql = """
        SELECT 
            PersonExtraFieldValueID, PersonID, ExtraFieldID, PersonExtraFieldValue,
            PersonExtraFieldIsActive, PersonExtraFieldIsDeleted,
            PersonExtraFieldEntDt, PersonExtraFieldEntUser, PersonExtraFieldEntTerm,
            PersonExtraFieldUpdDt, PersonExtraFieldUpdUser, PersonExtraFieldUpdTerm,
            PersonExtraFieldDelDt, PersonExtraFieldDelUser, PersonExtraFieldDelTerm
        FROM dbo.DLPersonExtraFieldValueDet
        WHERE PersonID = :person_id;
        """
        extra_fields = [PersonExtraFieldDetail.model_validate(r) for r in execute_readonly_query(extra_sql, {"person_id": person_id})]

        # 8. Instant Messaging (all 12 columns from dbo.DLPersonIMDet)
        im_sql = """
        SELECT 
            PersonIMID, PersionID, LabelTypeAIMID, LabelTypeIMID, TypeValue, PersonPhoneNotes,
            PersonPhoneEntDt, PersonPhoneEntUser, PersonPhoneEntTerm,
            PersonPhoneUpdDt, PersonPhoneUpdUser, PersonPhoneUpdTerm
        FROM dbo.DLPersonIMDet
        WHERE PersionID = :person_id;
        """
        ims = [PersonIMDetail.model_validate(r) for r in execute_readonly_query(im_sql, {"person_id": person_id})]

        # 9. Contact Ownership Transfer History (dbo.ChangeContactOwnershipTransaction)
        history_sql = """
        SELECT 
            t.ChangeOwnershipID,
            t.PersonID,
            t.LastPersonID,
            ISNULL(NULLIF(LTRIM(RTRIM(ISNULL(last_p.PersonFirstName, '') + ' ' + ISNULL(last_p.PersonLastName, ''))), ''), 'Person #' + CAST(t.LastPersonID AS varchar)) AS LastOwnerName,
            t.NewPersonID,
            ISNULL(NULLIF(LTRIM(RTRIM(ISNULL(new_p.PersonFirstName, '') + ' ' + ISNULL(new_p.PersonLastName, ''))), ''), 'Person #' + CAST(t.NewPersonID AS varchar)) AS NewOwnerName,
            t.RequestedByPersonID,
            ISNULL(NULLIF(LTRIM(RTRIM(ISNULL(req_p.PersonFirstName, '') + ' ' + ISNULL(req_p.PersonLastName, ''))), ''), 'Person #' + CAST(t.RequestedByPersonID AS varchar)) AS RequestedByName,
            t.EntDt,
            t.EntUser,
            t.EntTerm
        FROM dbo.ChangeContactOwnershipTransaction t
        LEFT JOIN dbo.DLPersonMst last_p ON last_p.PersonID = t.LastPersonID
        LEFT JOIN dbo.DLPersonMst new_p ON new_p.PersonID = t.NewPersonID
        LEFT JOIN dbo.DLPersonMst req_p ON req_p.PersonID = t.RequestedByPersonID
        WHERE t.PersonID = :person_id
        ORDER BY t.EntDt DESC, t.ChangeOwnershipID DESC;
        """
        ownership_history = [
            PersonOwnershipHistoryItem.model_validate(r)
            for r in execute_readonly_query(history_sql, {"person_id": person_id})
        ]

        return PersonRecordDetailResponse(
            person=person_item,
            addresses=addrs,
            contacts=contacts,
            companies=companies,
            relations=relations,
            documents=documents,
            extra_fields=extra_fields,
            ims=ims,
            ownership_history=ownership_history,
        )
