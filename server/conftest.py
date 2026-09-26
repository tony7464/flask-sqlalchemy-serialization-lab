#!/usr/bin/env python3
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app import app
from models import *


@pytest.fixture(scope="function")
def test_client():
    """Run each test against a shared in-memory database.

    The application engine is created at import time and points at
    ``instance/app.db``. Replacing that cached engine keeps ``create_all``
    and ``drop_all`` from deleting the seeded development database.
    """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        previous_engine = db.engines.get(None)
        memory_engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        db.engines[None] = memory_engine
        db.session.remove()
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()
        memory_engine.dispose()
        if previous_engine is not None:
            db.engines[None] = previous_engine
