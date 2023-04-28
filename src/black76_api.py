"""
Market Options API
---------
This module is the API layer to Market Options Web API.

Endpoints
-----
- `/market_options` : Returns all the options for GET request or adds a new option for  POST request
- `/market_options/{id}` : Returns a single option based on their ID
- `/market_options/pv`: Returns all the options including their PV, calculated using Black76 formula

"""
from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from .data_persistence import repo, schemas
from .data_persistence.database import SessionLocal

from .log_config import LOGGER
from .pv_service import PVService

api = FastAPI()


def get_db_session():
    """Generates a new SQLAlchemy database session everytime requested"""
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


@api.get("/", status_code=status.HTTP_200_OK)
def welcome():
    """
    Welcome endpoint to the Black76 API
    """
    return {"message": "Welcome to Black76 API"}


@api.get(
    "/market_options",
    response_model=List[schemas.FinancialOption],
    status_code=status.HTTP_200_OK,
)
def get_all_options(
    skip: int = 0, limit: int = 100, db_session: Session = Depends(get_db_session)
):
    """
    Get all options, with all the information for each option:
    - **id**: Id of the option
    - **commodity**: Name of the commodity
    - **expires_on**: Expiry time for the option (e.g., "Mar24" to indicate March of 2024)
    - **strike_price**: Strike price of the option
    - **option_type**: Type of option (CALL or PUT)
    - **unit_of_measure**: Pricing unit of measure (e.g., USD/BBL for Brent Oil)
    \f
    Args:
        skip (int): number of results to skip before fetching data from db.
        limit (int): maximum number of results to fetch from db.
        db_session (sqlalchemy.orm.Session): SQLAlchemy database session object.

    Returns:
        On Success: List[schemas.FinancialOption] with status code 200
        On Failure: HTTPException with status code 404
    """
    try:
        options = repo.get_all_financial_options(db_session, skip, limit)
        return options
    except OperationalError as op_error:
        raise HTTPException(status_code=404, detail=str(op_error)) from op_error


@api.get(
    "/market_options/{m_option_id}",
    response_model=schemas.FinancialOption,
    status_code=status.HTTP_200_OK,
)
def get_single_option(m_option_id: int, db_session: Session = Depends(get_db_session)):
    """
    Get single cake with all the information:
    - **id**: Id of the cake
    - **name**: Name of the cake
    - **comment**: Description of the cake
    - **image_url**: URL of the image of the cake
    - **yum_factor**: To indicate its tastiness
    \f
    :param cake_id: Id of the cake.
    :db_session: SQLAlchemy database session object.
    """
    market_option = repo.get_financial_option_by_id(db_session, m_option_id)
    if market_option is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Option not found"
        )
    return market_option


@api.post(
    "/market_options",
    response_model=schemas.FinancialOption,
    status_code=status.HTTP_201_CREATED,
)
def create_option(
    new_option: schemas.FinancialOptionCreate,
    db_session: Session = Depends(get_db_session),
):
    """
    Add a single cake with all the information:
    - **commodity**: Name of the commodity for which the option is getting created
    - **expires_on**: Expiry time for the option (e.g., "Mar24" to indicate March of 2024)
    - **strike_price**: Strike price of the option
    - **option_type**: Type of option (CALL or PUT)
    - **unit_of_measure**: Pricing unit of measure (e.g., USD/BBL for Brent Oil)
    \f
    Args:
        new_option (schemas.FinancialOptionCreate): FinancialOptionCreate object.
        db_session (sqlalchemy.orm.Session): SQLAlchemy database session object.

    Returns:
        On Success: schemas.FinancialOption with status code 200
        On Failure: HTTPException with status code 400
    """

    try:
        return repo.add_financial_option(db_session, new_option)
    except OperationalError as op_error:
        LOGGER.warning(
            "Error occured when creating a new option. Details: %s", str(op_error)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(op_error)
        ) from op_error
    except ValueError as val_error:
        LOGGER.warning(
            "Error occured when creating a new option. Details: %s", str(val_error)
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(val_error)
        ) from val_error


@api.post(
    "/market_options/pv",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
)
def calculate_present_value(
    pv_query: schemas.PVOptionQuery, db_session: Session = Depends(get_db_session)
):
    """
    Return Options with PV value included, with additional information for each option:
    - **id**: Id of the option
    - **commodity**: Name of the commodity
    - **expires_on**: Expiry time for the option (e.g., "Mar24" to indicate March of 2024)
    - **strike_price**: Strike price of the option
    - **option_type**: Type of option (CALL or PUT)
    - **unit_of_measure**: Pricing unit of measure (e.g., USD/BBL for Brent Oil)
    - **volatility**: The implied volatility of the underlying asset
    - **interest_rate**: The annualized risk-free interest rate.
    - **spot_price**: The current market price of the underlying asset.
    - **pv**: The present value of the option, rounded to 2 decimals..
    \f
    Args:
        pv_query (schemas.PVOptionQuery): PVOptionQuery Object.
        db_session (sqlalchemy.orm.Session): SQLAlchemy database session object.

    Returns:
        On Success: List[dict] with status code 200
        On Failure: HTTPException with status code 404
    """
    # We can do this using one of the 2 approaches:
    # Approach 1:
    # user supplies spot_price, risk_free_interest_rate, volatility, commodity name of interest
    # we perform the calculations for all the options and send back the results
    # Approach 2:
    # User only supplies some of the data (minimum being the asset they're interested in)
    # and the API will fetch the remaining details (for spot_price, interest_rate and volatility)
    # in real time from authorized Pricing APIs and performs the calculations accordingly.
    # The current implementation is Approach 1
    current_options = repo.get_financial_options_by_name(db_session, pv_query.commodity)
    if not current_options:
        LOGGER.warning("No options exist for commodity %s.", pv_query.commodity)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str("No options exist.")
        )

    updated_options = PVService.generate_pv_for_options(
        current_options,
        pv_query.interest_rate,
        pv_query.volatility,
        pv_query.spot_price,
    )
    return updated_options
