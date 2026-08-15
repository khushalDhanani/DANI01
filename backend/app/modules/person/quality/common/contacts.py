"""
contacts.py

Common CTEs and qualifying contact predicate expressions for Daylite Person communication channels.
"""

CLASSIFIED_CONTACTS_CTE_SQL = """
WITH ClassifiedContacts AS (
    SELECT 
        c.PersonPhoneID,
        c.PersionID AS PersonID,
        c.LabelTypeID,
        l.LableValue AS LabelName,
        c.TypeValue,
        c.IsVerified,
        c.IsPrimary,
        c.PersonPhoneIsActive,
        CASE 
            WHEN l.LabelType = 'EMail' OR (c.LabelTypeID IS NULL AND c.TypeValue LIKE '%@%') THEN 'EMAIL'
            WHEN l.LabelType = 'PhoneNumbers' OR (c.LabelTypeID IS NULL AND c.TypeValue NOT LIKE '%@%' AND c.TypeValue NOT LIKE 'http%' AND c.TypeValue NOT LIKE 'www%') THEN 'PHONE'
            WHEN l.LabelType = 'URL' OR (c.LabelTypeID IS NULL AND (c.TypeValue LIKE 'http%' OR c.TypeValue LIKE 'www%')) THEN 'URL'
            ELSE 'OTHER'
        END AS ContactCategory,
        LOWER(LTRIM(RTRIM(c.TypeValue))) AS NormalizedEmail,
        REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LTRIM(RTRIM(c.TypeValue)), ' ', ''), '-', ''), '+', ''), '(', ''), ')', ''), '.', ''), '/', '') AS NormalizedPhone
    FROM dbo.DLPersonPhoneEmailURLDet c
    JOIN dbo.DLPersonMst p ON p.PersonID = c.PersionID
    LEFT JOIN dbo.DLLabelTypeMst l ON c.LabelTypeID = l.LabelTypeID
    WHERE p.PersonIsActive = 1 AND (p.PersonIsDeleted = 0 OR p.PersonIsDeleted IS NULL)
)
""".strip()

QUALIFYING_EMAIL_EXISTS_SQL = """
EXISTS (
    SELECT 1 
    FROM ClassifiedContacts c
    WHERE c.PersonID = p.PersonID 
      AND c.ContactCategory = 'EMAIL'
      AND c.TypeValue IS NOT NULL 
      AND LTRIM(RTRIM(c.TypeValue)) <> ''
)
""".strip()

QUALIFYING_PHONE_EXISTS_SQL = """
EXISTS (
    SELECT 1 
    FROM ClassifiedContacts c
    WHERE c.PersonID = p.PersonID 
      AND c.ContactCategory = 'PHONE'
      AND c.TypeValue IS NOT NULL 
      AND LTRIM(RTRIM(c.TypeValue)) <> ''
)
""".strip()
