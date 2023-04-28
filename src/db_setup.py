""" Database initialization module """
from sqlalchemy import inspect
from data_persistence import models, repo
from data_persistence.database import (
    engine,
    SessionLocal,
    test_engine,
    SessionTest,
    Base,
)

from log_config import LOGGER


def setup_db():
    """
    Database initialization.
    Creates the database if it doesnt exist and creates the tables required, along with seed data.
    """
    db_session = SessionLocal()
    if not inspect(engine).has_table("financial_options"):
        models.Base.metadata.create_all(bind=engine)
        seed_data = [
            models.FinancialOption(
                commodity="BRN",
                expires_on="Jan24",
                strike_price="100",
                option_type="Call",
                unit_of_measure="USD/BBL",
            ),
            models.FinancialOption(
                commodity="HH",
                expires_on="Mar24",
                strike_price="10",
                option_type="Put",
                unit_of_measure="USD/MMBTu",
            ),
            models.FinancialOption(
                commodity="BRN",
                expires_on="Apr24",
                strike_price="100",
                option_type="Call",
                unit_of_measure="USD/BBL",
            ),
            models.FinancialOption(
                commodity="HH",
                expires_on="May24",
                strike_price="10",
                option_type="Put",
                unit_of_measure="USD/MMBTu",
            ),
        ]
        repo.initialise_with_options(db_session, seed_data)
    else:
        LOGGER.info("App db already initialized")


# Refactoring - Both setup_test_db and teardown_test_db can be moved out into tests/ package
def setup_test_db():
    """Database initialization for tests"""
    db_session = SessionTest()
    if not inspect(test_engine).has_table("financial_options"):
        Base.metadata.create_all(bind=test_engine)
        seed_data = [
            models.FinancialOption(
                commodity="BRN",
                expires_on="Jan24",
                strike_price="100",
                option_type="Call",
                unit_of_measure="USD/BBL",
            ),
            models.FinancialOption(
                commodity="HH",
                expires_on="Mar24",
                strike_price="10",
                option_type="Put",
                unit_of_measure="USD/MMBTu",
            ),
            models.FinancialOption(
                commodity="BRN",
                expires_on="Apr24",
                strike_price="100",
                option_type="Call",
                unit_of_measure="USD/BBL",
            ),
            models.FinancialOption(
                commodity="HH",
                expires_on="May24",
                strike_price="10",
                option_type="Put",
                unit_of_measure="USD/MMBTu",
            ),
        ]
        repo.initialise_with_options(db_session, seed_data)


def teardown_test_db():
    """Database teardown for tests"""
    if inspect(test_engine).has_table("financial_options"):
        Base.metadata.drop_all(bind=test_engine)


if __name__ == "__main__":
    setup_db()
