import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401  (registers tables on Base.metadata)
from app.database import Base

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+psycopg://localhost/partner_onboarding_test"
)


@pytest.fixture(scope="session")
def engine():
    # Uses create_all against a disposable test DB, deliberately not Alembic here —
    # this is test-fixture setup, not the app's own migration path (still Alembic-only).
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db(engine):
    connection = engine.connect()
    transaction = connection.begin()
    # join_transaction_mode="create_savepoint": a failed flush() inside a test (e.g. the
    # constraint-violation tests) rolls back to a SAVEPOINT instead of ending this outer
    # transaction — otherwise the fixture's own rollback() at teardown has nothing left
    # to roll back and SQLAlchemy warns about it.
    session = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")()
    yield session
    session.close()
    transaction.rollback()
    connection.close()
