"""
persons.py

Common SQL definitions and predicates for Daylite Person entities.
"""

ACTIVE_PERSON_WHERE_SQL = (
    "p.PersonIsActive = 1 AND (p.PersonIsDeleted = 0 OR p.PersonIsDeleted IS NULL)"
)

PERSON_NAME_SQL = """
CASE
    WHEN p.PersonFirstName IS NOT NULL AND LTRIM(RTRIM(p.PersonFirstName)) <> ''
     AND p.PersonLastName IS NOT NULL AND LTRIM(RTRIM(p.PersonLastName)) <> ''
        THEN LTRIM(RTRIM(p.PersonFirstName)) + ' ' + LTRIM(RTRIM(p.PersonLastName))
    WHEN p.PersonFirstName IS NOT NULL AND LTRIM(RTRIM(p.PersonFirstName)) <> ''
        THEN LTRIM(RTRIM(p.PersonFirstName))
    WHEN p.PersonLastName IS NOT NULL AND LTRIM(RTRIM(p.PersonLastName)) <> ''
        THEN LTRIM(RTRIM(p.PersonLastName))
    ELSE 'Person #' + CAST(p.PersonID AS VARCHAR(20))
END
""".strip()
