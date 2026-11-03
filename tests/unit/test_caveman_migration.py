from importlib import import_module

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

pytestmark = pytest.mark.unit


def test_existing_keys_default_off_and_downgrade_preserves_rows():
    migration = import_module("app.db.alembic.versions.20261103_000000_add_api_key_caveman")
    engine = sa.create_engine("sqlite://")
    with engine.begin() as connection:
        connection.execute(sa.text("CREATE TABLE api_keys (id TEXT PRIMARY KEY, name TEXT NOT NULL)"))
        connection.execute(sa.text("INSERT INTO api_keys VALUES ('existing', 'keep')"))
        with Operations.context(MigrationContext.configure(connection)):
            migration.upgrade()
            assert connection.execute(sa.text("SELECT caveman_enabled FROM api_keys")).scalar_one() == 0
            connection.execute(sa.text("UPDATE api_keys SET caveman_enabled = 1"))
            migration.downgrade()
            assert connection.execute(sa.text("SELECT name FROM api_keys")).scalar_one() == "keep"
            migration.upgrade()
            assert connection.execute(sa.text("SELECT caveman_enabled FROM api_keys")).scalar_one() == 0
    engine.dispose()
