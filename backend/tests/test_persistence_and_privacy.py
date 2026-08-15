import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.analysis.sanitization import ProfileSanitizer
from app.classification.taxonomy import SensitivityLevel
from app.db.postgres import Base
from app.persistence.models.analysis_run import AnalysisRunModel, AnalysisRunStatus
from app.persistence.repositories.analysis_runs import AnalysisRunRepository
from app.persistence.repositories.profiles import AnalysisProfileRepository
from app.persistence.repositories.table_results import AnalysisTableResultRepository
from app.schemas.analysis import (
    TableAnalysisStatus,
    TableAnalysisSummary,
    TableAnalysisTimings,
)
from app.schemas.classification import (
    ColumnClassification,
    TableClassificationResponse,
)
from app.schemas.profiling import (
    NumericColumnProfile,
    TableProfileResponse,
    TextColumnProfile,
    ValueFrequency,
)


@pytest.fixture
def db_session():
    """Creates an isolated in-memory SQLite database session for testing persistence."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def test_analysis_run_repository_lifecycle(db_session):
    repo = AnalysisRunRepository(db_session)

    # 1. Create run
    run = repo.create_run(database_name="AIRIS_TEST", analysis_type="QUICK", schema_filter="dbo")
    assert run.id is not None
    assert run.status == AnalysisRunStatus.QUEUED.value
    assert run.database_name == "AIRIS_TEST"
    assert run.schema_filter == "dbo"

    # 2. Update status to RUNNING
    updated = repo.update_status(run.id, status=AnalysisRunStatus.RUNNING)
    assert updated.status == AnalysisRunStatus.RUNNING.value

    # 3. Update progress
    repo.update_progress(
        run_id=run.id,
        tables_total=10,
        tables_completed=5,
        tables_skipped=2,
        tables_failed=0,
        progress_percent=70.0,
        columns_discovered=50,
        columns_profiled=35,
        columns_classified=35,
    )
    fetched = repo.get_run(run.id)
    assert fetched.tables_completed == 5
    assert fetched.progress_percent == 70.0
    assert fetched.columns_profiled == 35

    # 4. List runs
    runs, total = repo.list_runs(limit=10, offset=0)
    assert total == 1
    assert len(runs) == 1
    assert runs[0].id == run.id


def test_analysis_table_result_repository_and_idempotency(db_session):
    run_repo = AnalysisRunRepository(db_session)
    table_repo = AnalysisTableResultRepository(db_session)

    run = run_repo.create_run(database_name="AIRIS_TEST")

    summary = TableAnalysisSummary(
        schema="dbo",
        table="Users",
        estimated_rows=5000,
        status=TableAnalysisStatus.COMPLETED,
        sample_size=1000,
        returned_rows=1000,
        column_count=10,
        profiled_columns=10,
        classified_columns=10,
        duration_ms=120.5,
        timings=TableAnalysisTimings(
            structure_duration_ms=10.0,
            sampling_duration_ms=40.0,
            profiling_duration_ms=50.0,
            classification_duration_ms=20.0,
            total_duration_ms=120.5,
        ),
    )

    # 1. First insert
    record1 = table_repo.upsert_table_result(run.id, summary)
    assert record1.id is not None
    assert record1.schema_name == "dbo"
    assert record1.table_name == "Users"
    assert record1.timing is not None
    assert record1.timing.total_duration_ms == 120.5

    # 2. Second upsert (simulating retry / idempotency)
    summary.duration_ms = 110.0
    record2 = table_repo.upsert_table_result(run.id, summary)

    # Must update existing record without creating duplicate
    assert record2.id == record1.id
    assert record2.duration_ms == 110.0

    # Verify count remains 1
    results, total = table_repo.get_table_results(run.id)
    assert total == 1
    assert len(results) == 1


def test_privacy_sanitization_redacts_pii_top_values():
    """
    CRITICAL PRIVACY TEST:
    Verifies that ProfileSanitizer removes/redacts top_values for sensitive PII
    (EMAIL, PHONE, NAME, DATE_OF_BIRTH, etc.) when expose_values == False,
    while preserving safe analytical metrics and non-PII values.
    """
    profile_response = TableProfileResponse(
        schema="dbo",
        table="Customers",
        sample_size=1000,
        returned_rows=100,
        columns=[
            TextColumnProfile(
                name="EmailAddress",
                data_type="nvarchar",
                null_count=0,
                null_percent=0.0,
                distinct_count=100,
                distinct_percent=100.0,
                top_values=[
                    ValueFrequency(value="ceo@example.com", count=1, percent=1.0),
                    ValueFrequency(value="user@secret.org", count=1, percent=1.0),
                ],
                min_length=15,
                max_length=25,
                avg_length=20.0,
            ),
            TextColumnProfile(
                name="PhoneNumber",
                data_type="varchar",
                null_count=5,
                null_percent=5.0,
                distinct_count=95,
                distinct_percent=95.0,
                top_values=[
                    ValueFrequency(value="+1-555-0199", count=1, percent=1.0),
                ],
            ),
            NumericColumnProfile(
                name="Salary",
                data_type="decimal",
                null_count=0,
                null_percent=0.0,
                distinct_count=50,
                distinct_percent=50.0,
                top_values=[
                    ValueFrequency(value=50000.0, count=10, percent=10.0),
                ],
                min=30000.0,
                max=150000.0,
                mean=75000.0,
            ),
        ],
    )

    classification_response = TableClassificationResponse(
        schema="dbo",
        table="Customers",
        columns=[
            ColumnClassification(
                name="EmailAddress",
                sql_type="nvarchar",
                semantic_type="EMAIL",
                sensitivity=SensitivityLevel.PII.value,
                expose_values=False,
                confidence=1.0,
            ),
            ColumnClassification(
                name="PhoneNumber",
                sql_type="varchar",
                semantic_type="PHONE",
                sensitivity=SensitivityLevel.PII.value,
                expose_values=False,
                confidence=0.95,
            ),
            ColumnClassification(
                name="Salary",
                sql_type="decimal",
                semantic_type="AMOUNT",
                sensitivity=SensitivityLevel.INTERNAL.value,
                expose_values=True,
                confidence=0.85,
            ),
        ],
    )

    sanitized = ProfileSanitizer.sanitize_column_profiles(
        profile_response, classification_response
    )

    # 1. EmailAddress: top_values must be completely redacted
    email_prof = next(p for p in sanitized if p["column_name"] == "EmailAddress")
    assert email_prof["top_values"] == []
    assert email_prof["stats"]["min_length"] == 15  # Statistical metrics preserved
    assert email_prof["null_count"] == 0

    # 2. PhoneNumber: top_values must be completely redacted
    phone_prof = next(p for p in sanitized if p["column_name"] == "PhoneNumber")
    assert phone_prof["top_values"] == []

    # 3. Salary: expose_values is True, top_values preserved
    salary_prof = next(p for p in sanitized if p["column_name"] == "Salary")
    assert len(salary_prof["top_values"]) == 1
    assert salary_prof["top_values"][0]["value"] == 50000.0
    assert salary_prof["stats"]["mean"] == 75000.0


def test_profile_repository_persistence(db_session):
    run_repo = AnalysisRunRepository(db_session)
    table_repo = AnalysisTableResultRepository(db_session)
    profile_repo = AnalysisProfileRepository(db_session)

    run = run_repo.create_run(database_name="AIRIS_TEST")
    summary = TableAnalysisSummary(
        schema="dbo",
        table="Employees",
        estimated_rows=100,
        status=TableAnalysisStatus.COMPLETED,
        column_count=2,
    )
    table_record = table_repo.upsert_table_result(run.id, summary)

    # Save sanitized profiles
    profiles_data = [
        {
            "column_name": "EmployeeID",
            "data_type": "int",
            "profile_type": "numeric",
            "null_count": 0,
            "null_percent": 0.0,
            "distinct_count": 100,
            "distinct_percent": 100.0,
            "top_values": [],
            "stats": {"min": 1, "max": 100},
        }
    ]
    profile_repo.save_column_profiles(table_record.id, profiles_data)

    # Save classifications
    classifications_data = [
        ColumnClassification(
            name="EmployeeID",
            sql_type="int",
            semantic_type="IDENTIFIER",
            sensitivity=SensitivityLevel.INTERNAL.value,
            expose_values=True,
            confidence=1.0,
        )
    ]
    profile_repo.save_column_classifications(table_record.id, classifications_data)

    saved_profiles = profile_repo.get_column_profiles(table_record.id)
    saved_classes = profile_repo.get_column_classifications(table_record.id)

    assert len(saved_profiles) == 1
    assert saved_profiles[0].column_name == "EmployeeID"
    assert saved_profiles[0].stats["max"] == 100

    assert len(saved_classes) == 1
    assert saved_classes[0].column_name == "EmployeeID"
    assert saved_classes[0].semantic_type == "IDENTIFIER"
