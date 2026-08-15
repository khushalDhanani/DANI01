from typing import Dict


def build_person_metrics_query(
    root_table: str = "dbo.DLPersonMst",
    root_key: str = "PersonID",
    has_active_col: bool = True,
    has_deleted_col: bool = True,
    has_temp_col: bool = True,
    has_blacklist_col: bool = True,
    address_table: str | None = "dbo.DLPersonAddressDet",
    contact_table: str | None = "dbo.DLPersonPhoneEmailURLDet",
    contact_person_key: str = "PersionID",
    company_link_table: str | None = "dbo.DLPersonCompanyLinkDet",
    relation_table: str | None = "dbo.DLPersonRelationDet",
    document_table: str | None = "dbo.DLPersonDocumentDet",
    extra_field_table: str | None = "dbo.DLPersonExtraFieldValueDet",
    im_table: str | None = "dbo.DLPersonIMDet",
) -> str:
    """
    Builds a single, set-based, read-only T-SQL query to compute domain aggregate metrics
    for the PERSON module using pre-aggregated distinct CTEs.
    """
    ctes: list[str] = []
    select_fields: list[str] = [
        "COUNT_BIG(1) AS total_persons",
    ]

    # Status Flags
    if has_active_col:
        select_fields.append(
            "SUM(CASE WHEN p.PersonIsActive = 1 THEN 1 ELSE 0 END) AS active_persons"
        )
        select_fields.append(
            "SUM(CASE WHEN p.PersonIsActive = 0 OR p.PersonIsActive IS NULL THEN 1 ELSE 0 END) AS inactive_persons"
        )
    else:
        select_fields.append("NULL AS active_persons")
        select_fields.append("NULL AS inactive_persons")

    if has_deleted_col:
        select_fields.append("SUM(CASE WHEN p.PersonIsDeleted = 1 THEN 1 ELSE 0 END) AS deleted_persons")
    else:
        select_fields.append("NULL AS deleted_persons")

    if has_temp_col:
        select_fields.append("SUM(CASE WHEN p.PersonIsTemp = 1 THEN 1 ELSE 0 END) AS temp_persons")
    else:
        select_fields.append("NULL AS temp_persons")

    if has_blacklist_col:
        select_fields.append("SUM(CASE WHEN p.PersonIsBlackList = 1 THEN 1 ELSE 0 END) AS blacklist_persons")
    else:
        select_fields.append("NULL AS blacklist_persons")

    # Business Mappings: PersonIsVisitor_Contact (1=Visitor, 2=Contact)
    select_fields.append("SUM(CASE WHEN p.PersonIsVisitor_Contact = 1 THEN 1 ELSE 0 END) AS visitor_count")
    select_fields.append("SUM(CASE WHEN p.PersonIsVisitor_Contact = 2 THEN 1 ELSE 0 END) AS contact_entity_count")

    # Business Mappings: PersonIsShareContact (0=Private, 1=Public)
    select_fields.append("SUM(CASE WHEN p.PersonIsShareContact = 1 THEN 1 ELSE 0 END) AS public_count")
    select_fields.append("SUM(CASE WHEN p.PersonIsShareContact = 0 OR p.PersonIsShareContact IS NULL THEN 1 ELSE 0 END) AS private_count")

    joins: list[str] = []

    # 1. Address CTE & Join
    if address_table:
        ctes.append(
            f"DistinctAddresses AS (\n"
            f"    SELECT \n"
            f"        PersonID,\n"
            f"        COUNT_BIG(1) AS addr_count,\n"
            f"        SUM(CASE WHEN PersonAddIsActive = 1 THEN 1 ELSE 0 END) AS active_addr,\n"
            f"        SUM(CASE WHEN Latitude IS NOT NULL AND Longitude IS NOT NULL THEN 1 ELSE 0 END) AS geo_addr,\n"
            f"        SUM(CASE WHEN GoogleFormattedAddress IS NOT NULL AND LEN(LTRIM(RTRIM(GoogleFormattedAddress))) > 0 THEN 1 ELSE 0 END) AS fmt_addr,\n"
            f"        SUM(CASE WHEN PostalCode IS NOT NULL AND LEN(LTRIM(RTRIM(PostalCode))) > 0 THEN 1 ELSE 0 END) AS postal_addr\n"
            f"    FROM {address_table} WHERE PersonID IS NOT NULL\n"
            f"    GROUP BY PersonID\n"
            f")"
        )
        joins.append("LEFT JOIN DistinctAddresses a ON p.PersonID = a.PersonID")
        select_fields.append("COUNT_BIG(a.PersonID) AS persons_with_address")
        select_fields.append("ISNULL(SUM(a.addr_count), 0) AS total_addresses")
        select_fields.append("ISNULL(SUM(a.active_addr), 0) AS active_addresses")
        select_fields.append("ISNULL(SUM(a.geo_addr), 0) AS geo_addresses")
        select_fields.append("ISNULL(SUM(a.fmt_addr), 0) AS formatted_addresses")
        select_fields.append("ISNULL(SUM(a.postal_addr), 0) AS postal_addresses")
    else:
        select_fields.append("NULL AS persons_with_address")
        select_fields.append("NULL AS total_addresses")
        select_fields.append("NULL AS active_addresses")
        select_fields.append("NULL AS geo_addresses")
        select_fields.append("NULL AS formatted_addresses")
        select_fields.append("NULL AS postal_addresses")

    # 2. Contact Channels CTE & Join (Any Contact, Email, Phone, Verified, Primary, Active)
    if contact_table:
        ctes.append(
            f"DistinctContacts AS (\n"
            f"    SELECT \n"
            f"        {contact_person_key} AS PersonID,\n"
            f"        COUNT_BIG(1) AS contact_count,\n"
            f"        SUM(CASE WHEN PersonPhoneIsActive = 1 THEN 1 ELSE 0 END) AS active_contacts,\n"
            f"        SUM(CASE WHEN IsVerified = 1 THEN 1 ELSE 0 END) AS verified_contacts,\n"
            f"        SUM(CASE WHEN IsPrimary = 1 THEN 1 ELSE 0 END) AS primary_contacts\n"
            f"    FROM {contact_table} WHERE {contact_person_key} IS NOT NULL\n"
            f"    GROUP BY {contact_person_key}\n"
            f")"
        )
        ctes.append(
            f"DistinctEmails AS (\n"
            f"    SELECT DISTINCT {contact_person_key} AS PersonID FROM {contact_table} "
            f"WHERE {contact_person_key} IS NOT NULL AND TypeValue LIKE '%@%'\n"
            f")"
        )
        ctes.append(
            f"DistinctPhones AS (\n"
            f"    SELECT DISTINCT {contact_person_key} AS PersonID FROM {contact_table} "
            f"WHERE {contact_person_key} IS NOT NULL "
            f"AND TypeValue NOT LIKE '%@%' "
            f"AND TypeValue NOT LIKE 'http%' "
            f"AND TypeValue NOT LIKE 'www%'\n"
            f")"
        )
        joins.append("LEFT JOIN DistinctContacts c ON p.PersonID = c.PersonID")
        joins.append("LEFT JOIN DistinctEmails e ON p.PersonID = e.PersonID")
        joins.append("LEFT JOIN DistinctPhones ph ON p.PersonID = ph.PersonID")

        select_fields.append("COUNT_BIG(c.PersonID) AS persons_with_contact")
        select_fields.append("COUNT_BIG(e.PersonID) AS persons_with_email")
        select_fields.append("COUNT_BIG(ph.PersonID) AS persons_with_phone")
        select_fields.append("ISNULL(SUM(c.contact_count), 0) AS total_contacts")
        select_fields.append("ISNULL(SUM(c.active_contacts), 0) AS active_contacts")
        select_fields.append("ISNULL(SUM(c.verified_contacts), 0) AS verified_contacts")
        select_fields.append("ISNULL(SUM(c.primary_contacts), 0) AS primary_contacts")
    else:
        select_fields.append("NULL AS persons_with_contact")
        select_fields.append("NULL AS persons_with_email")
        select_fields.append("NULL AS persons_with_phone")
        select_fields.append("NULL AS total_contacts")
        select_fields.append("NULL AS active_contacts")
        select_fields.append("NULL AS verified_contacts")
        select_fields.append("NULL AS primary_contacts")

    # 3. Company Link CTE & Join
    if company_link_table:
        ctes.append(
            f"DistinctCompanyLinks AS (\n"
            f"    SELECT PersonID, COUNT_BIG(1) AS comp_count FROM {company_link_table} WHERE PersonID IS NOT NULL GROUP BY PersonID\n"
            f")"
        )
        joins.append("LEFT JOIN DistinctCompanyLinks cl ON p.PersonID = cl.PersonID")
        select_fields.append("COUNT_BIG(cl.PersonID) AS persons_with_company_link")
        select_fields.append("ISNULL(SUM(cl.comp_count), 0) AS total_company_links")
    else:
        select_fields.append("NULL AS persons_with_company_link")
        select_fields.append("NULL AS total_company_links")

    # 4. Relations CTE & Join
    if relation_table:
        ctes.append(
            f"DistinctRelations AS (\n"
            f"    SELECT PersonID FROM {relation_table} WHERE PersonID IS NOT NULL\n"
            f"    UNION\n"
            f"    SELECT RelatedPersonID AS PersonID FROM {relation_table} WHERE RelatedPersonID IS NOT NULL\n"
            f")"
        )
        joins.append("LEFT JOIN DistinctRelations r ON p.PersonID = r.PersonID")
        select_fields.append("COUNT_BIG(r.PersonID) AS persons_with_relationship")
    else:
        select_fields.append("NULL AS persons_with_relationship")

    # 5. Documents CTE & Join
    if document_table:
        ctes.append(
            f"DistinctDocs AS (\n"
            f"    SELECT PersonID, COUNT_BIG(1) AS doc_count FROM {document_table} WHERE PersonID IS NOT NULL GROUP BY PersonID\n"
            f")"
        )
        joins.append("LEFT JOIN DistinctDocs d ON p.PersonID = d.PersonID")
        select_fields.append("COUNT_BIG(d.PersonID) AS persons_with_document")
        select_fields.append("ISNULL(SUM(d.doc_count), 0) AS total_documents")
    else:
        select_fields.append("NULL AS persons_with_document")
        select_fields.append("NULL AS total_documents")

    # 6. Extra Fields CTE & Join
    if extra_field_table:
        ctes.append(
            f"DistinctExtras AS (\n"
            f"    SELECT PersonID, COUNT_BIG(1) AS extra_count FROM {extra_field_table} WHERE PersonID IS NOT NULL GROUP BY PersonID\n"
            f")"
        )
        joins.append("LEFT JOIN DistinctExtras ex ON p.PersonID = ex.PersonID")
        select_fields.append("COUNT_BIG(ex.PersonID) AS persons_with_extra_field")
        select_fields.append("ISNULL(SUM(ex.extra_count), 0) AS total_extra_fields")
    else:
        select_fields.append("NULL AS persons_with_extra_field")
        select_fields.append("NULL AS total_extra_fields")

    # 7. IM Handles CTE & Join
    if im_table:
        ctes.append(
            f"DistinctIMs AS (\n"
            f"    SELECT PersionID AS PersonID, COUNT_BIG(1) AS im_count FROM {im_table} WHERE PersionID IS NOT NULL GROUP BY PersionID\n"
            f")"
        )
        joins.append("LEFT JOIN DistinctIMs im ON p.PersonID = im.PersonID")
        select_fields.append("COUNT_BIG(im.PersonID) AS persons_with_im")
        select_fields.append("ISNULL(SUM(im.im_count), 0) AS total_ims")
    else:
        select_fields.append("NULL AS persons_with_im")
        select_fields.append("NULL AS total_ims")

    cte_block = "WITH " + ",\n".join(ctes) if ctes else ""
    select_block = "SELECT\n    " + ",\n    ".join(select_fields)
    from_block = f"FROM {root_table} p"
    joins_block = "\n".join(joins)

    query = f"{cte_block}\n{select_block}\n{from_block}\n{joins_block};"
    return query


def build_child_table_counts_query(
    tables_dict: Dict[str, str],
) -> str:
    """
    Builds a quick query to fetch total row counts for child tables.
    tables_dict maps alias -> full_table_name, e.g. {"total_addresses": "dbo.DLPersonAddressDet"}
    """
    if not tables_dict:
        return "SELECT 1 AS dummy;"

    select_items = [
        f"(SELECT COUNT_BIG(1) FROM {tbl}) AS {alias}"
        for alias, tbl in tables_dict.items()
    ]
    return "SELECT\n    " + ",\n    ".join(select_items) + ";"
