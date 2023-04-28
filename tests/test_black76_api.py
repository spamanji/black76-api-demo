# pylint: disable=missing-function-docstring,missing-module-docstring
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.exc import OperationalError
from src.black76_api import api, get_db_session
from src.data_persistence.database import SessionTest

from src.db_setup import setup_test_db, teardown_test_db


def get_test_db_session():
    db_session = SessionTest()
    try:
        yield db_session
    finally:
        db_session.close()


api.dependency_overrides[get_db_session] = get_test_db_session


client = TestClient(app=api)


def setup_module():
    setup_test_db()


def teardown_module():
    teardown_test_db()


def mock_get_options_raise_db_op_error(db_session, skip, limit):
    raise OperationalError("Test DB Connection Failed", None, None)


def test_welcome_endpoint():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to Black76 API"}


def test_get_all_financial_options_success():
    response = client.get("/market_options")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None and len(response.json()) == 4


@patch("src.black76_api.repo.get_all_financial_options")
def test_get_all_financial_options_failure(mock_get_options):
    mock_get_options.side_effect = mock_get_options_raise_db_op_error
    response = client.get("/market_options")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() is not None


def test_get_single_option_found():
    response = client.get("/market_options/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None and int(response.json()["id"]) == 1


def test_get_single_option_not_found():
    response = client.get("/market_options/10")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert (
        response.json() is not None
        and (response.json()["detail"]) == "Option not found"
    )


def test_create_option_success():
    good_option = {
        "commodity": "BRN",
        "strike_price": "100",
        "expires_on": "Jun24",
        "option_type": "PUT",
        "unit_of_measure": "USD/BBL",
    }

    response = client.post("/market_options", json=good_option)
    assert response.status_code == status.HTTP_201_CREATED
    print(response.json())
    assert response.json()["id"] != 0
    assert response.json()["strike_price"] == 100


def test_create_option_expires_on_validation_failure():
    bad_option = {
        "commodity": "BRN",
        "strike_price": "100",
        "expires_on": "Apr23",
        "option_type": "PUT",
        "unit_of_measure": "USD/BBL",
    }

    response = client.post("/market_options", json=bad_option)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response_detail = response.json()["detail"]
    assert response_detail == "Expiry date should be earlier than today."


def test_create_option_commodity_validation_failure():
    bad_option = {
        "commodity": "ABC",
        "strike_price": "100",
        "expires_on": "Apr24",
        "option_type": "PUT",
        "unit_of_measure": "USD/BBL",
    }

    response = client.post("/market_options", json=bad_option)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_detail = response.json()["detail"][0]
    assert (
        response_detail["msg"]
        == "Unknown Commodity. Accepted commodities are: BRN or HH"
    )
    assert response_detail["type"] == "value_error"


def test_create_option_strike_price_validation_failure():
    bad_option = {
        "commodity": "BRN",
        "strike_price": "-12",
        "expires_on": "Apr24",
        "option_type": "PUT",
        "unit_of_measure": "USD/BBL",
    }

    response = client.post("/market_options", json=bad_option)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_detail = response.json()["detail"][0]
    assert response_detail["msg"] == "Strike price cannot be less than 0."
    assert response_detail["type"] == "value_error"


def test_create_option_option_type_validation_failure():
    bad_option = {
        "commodity": "BRN",
        "strike_price": "12",
        "expires_on": "Apr24",
        "option_type": "TEST",
        "unit_of_measure": "USD/BBL",
    }

    response = client.post("/market_options", json=bad_option)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    response_detail = response.json()["detail"][0]
    assert response_detail["msg"] == "Invalid Option Type. Allowed values: Call or Put."
    assert response_detail["type"] == "value_error"


def test_calculate_present_value_success():
    good_pv_query = {
        "commodity": "BRN",
        "interest_rate": 0.2,
        "volatility": 0.3,
        "spot_price": 78.94,
    }
    response = client.post("/market_options/pv", json=good_pv_query)
    assert response.status_code == status.HTTP_200_OK
    print(response.json())
    assert response.json()[0]["pv"] == 3.72
    assert response.json()[0]["interest_rate"] == 0.2


def test_calculate_present_value_failure(caplog):
    bad_pv_query = {
        "commodity": "ABC",
        "interest_rate": 0.2,
        "volatility": 0.3,
        "spot_price": 78.94,
    }
    response = client.post("/market_options/pv", json=bad_pv_query)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "No options exist for commodity" in caplog.text
