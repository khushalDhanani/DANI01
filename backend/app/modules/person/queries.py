

def build_person_metrics_query(
    root_table: str = "dbo.DLPersonMst",
    root_key: str = "PersonID",
    has_active_col: bool = True,
    has_deleted_col: bool = True,
    has_temp_col: bool = True,
    has_blacklist_col: bool = True,
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

    cte_block = "WITH " + ",\n".join(ctes) if ctes else ""
    select_block = "SELECT\n    " + ",\n    ".join(select_fields)
    from_block = f"FROM {root_table} p"
    joins_block = ""

    query = f"{cte_block}\n{select_block}\n{from_block}\n{joins_block};"
    return query


def build_child_table_counts_query(
    tables_dict: dict[str, str],
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
