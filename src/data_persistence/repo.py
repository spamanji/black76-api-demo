"""
Repository module for performing database operations
"""
from typing import List
from sqlalchemy.orm import Session
from . import models, schemas


def get_financial_option_by_id(db_session: Session, f_option_id: int):
    """Returns a single option based on its ID"""
    return (
        db_session.query(models.FinancialOption)
        .filter(models.FinancialOption.id == f_option_id)
        .first()
    )


def get_financial_options_by_name(db_session: Session, asset_name: str):
    """Returns all options based on underlying commodity name"""
    return (
        db_session.query(models.FinancialOption)
        .filter(models.FinancialOption.commodity == asset_name)
        .all()
    )


def get_all_financial_options(db_session: Session, skip: int = 0, limit: int = 100):
    """Returns all options"""
    return db_session.query(models.FinancialOption).offset(skip).limit(limit).all()


def add_financial_option(db_session: Session, f_option: schemas.FinancialOptionCreate):
    """Adds a single option"""
    new_option = models.FinancialOption(**f_option.dict())
    db_session.add(new_option)
    db_session.commit()
    db_session.refresh(new_option)
    return new_option


def remove_option(db_session: Session, f_option_id: int):
    """Removes a single option based on option's ID"""
    return (
        db_session.query(models.FinancialOption)
        .filter(models.FinancialOption.id == f_option_id)
        .delete()
    )


def initialise_with_options(db_session: Session, seed_data: list):
    """Initialises database with seed data of options"""
    db_session.add_all(seed_data)
    db_session.commit()
