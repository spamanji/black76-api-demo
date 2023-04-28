# pylint: disable=no-self-argument,too-few-public-methods
"Pydantic Schemas module for serialization and input validation"
import datetime as dt
from pydantic import BaseModel, root_validator


class FinancialOptionBase(BaseModel):
    """Base Model schema for Financial Option"""

    commodity: str
    expires_on: str
    strike_price: float
    option_type: str
    unit_of_measure: str


class FinancialOptionCreate(FinancialOptionBase):
    """Creation schema for Financial Option"""

    @root_validator
    def validate_fields(cls, values):
        """Request body validation before creation"""
        # Confirm if its a valid asset. example: BRN is valid but MNBVCX is probably not?
        # Ideally we should check against valid asset names from an apporved API
        # Simplifying this to a list for now to minimize scope
        allowed_assets = ["BRN", "HH"]
        allowed_option_types = ["CALL", "PUT"]
        if values["commodity"].upper() not in allowed_assets:
            raise ValueError("Unknown Commodity. Accepted commodities are: BRN or HH")
        if values["option_type"].upper() not in allowed_option_types:
            raise ValueError("Invalid Option Type. Allowed values: Call or Put.")
        if values["strike_price"] < 0:
            raise ValueError("Strike price cannot be less than 0.")
        return values


class FinancialOption(FinancialOptionBase):
    """Presentation schema for Financial Option"""

    id: str
    expiration_date: dt.date

    class Config:
        orm_mode = True


class FinancialOptionPresentValue(FinancialOption):
    """Presentation schema for Financial Option with PV calculated from Black76 formula"""

    interest_rate: float = 0.0
    volatility: float = 0.0
    spot_price: float = 0.0
    pv: float = 0.0


class PVOptionQuery(BaseModel):
    """Query Schema for calculation of PV using Black76 formula"""

    commodity: str
    interest_rate: float
    volatility: float
    spot_price: float
