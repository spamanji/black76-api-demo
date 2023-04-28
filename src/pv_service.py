# pylint: disable=no-self-argument
"""PV Service Module"""
import datetime as dt
from typing import List
from scipy.stats import norm
import numpy as np
from .data_persistence import schemas, models


class PVService:
    """PV Service"""

    @staticmethod
    def get_time_to_expiry(expiry_date: dt.date) -> float:
        """
        Calculate time to expiry as a fraction of the year

        Args:
            expiry_date (datetime.date): The expiry date of the option

        Returns:
            float: calculated time_to_expiry rounded to 2 decimals
        """
        today = dt.date.today()
        time_to_expiry = (expiry_date - today).days / 365
        return round(time_to_expiry, 2)

    @classmethod
    def calculate_pv(
        cls,
        pv_calculation_inputs: dict,
    ):
        """
        Calculate the present value of an option using the Black76 formula.
        Verified results against: [https:]//goodcalculators[.]com/black-scholes-calculator/

        Args:
            pv_calculation_inputs (dict):  Consisting of the following keys
                expiration_date (datetime.date): The expiry date of the option
                strike_price (float): The strike price of the option.
                option_type (str): The type of option, either "call" or "put".
                interest_rate (float): The annualized risk-free interest rate.
                volatility (float): The implied volatility of the underlying asset.
                spot_price (float): The current market price of the underlying asset.

        Returns:
            float: The present value of the option, rounded to 2 decimals.
        """
        present_value = 0.0
        n_cdf = norm.cdf
        time_to_expiry = PVService.get_time_to_expiry(
            pv_calculation_inputs["expiration_date"]
        )

        d1_calc = (
            np.log(
                pv_calculation_inputs["spot_price"]
                / pv_calculation_inputs["strike_price"]
            )
            + (
                pv_calculation_inputs["interest_rate"]
                + pv_calculation_inputs["volatility"] ** 2 / 2
            )
            * time_to_expiry
        ) / (pv_calculation_inputs["volatility"] * np.sqrt(time_to_expiry))
        d2_calc = d1_calc - pv_calculation_inputs["volatility"] * np.sqrt(
            time_to_expiry
        )

        if pv_calculation_inputs["option_type"].casefold() == "put":
            present_value = pv_calculation_inputs["strike_price"] * np.exp(
                -pv_calculation_inputs["interest_rate"] * time_to_expiry
            ) * n_cdf(-d2_calc) - pv_calculation_inputs["spot_price"] * n_cdf(-d1_calc)
        elif pv_calculation_inputs["option_type"].casefold() == "call":
            present_value = pv_calculation_inputs["spot_price"] * n_cdf(
                d1_calc
            ) - pv_calculation_inputs["strike_price"] * np.exp(
                -pv_calculation_inputs["interest_rate"] * time_to_expiry
            ) * n_cdf(
                d2_calc
            )
        else:
            raise ValueError("Unknown option type.")

        return round(present_value, 2)

    @classmethod
    def update_pv_for_single_option(
        cls,
        option: schemas.FinancialOptionPresentValue,
        interest_rate: float,
        volatility: float,
        spot_price: float,
    ) -> schemas.FinancialOptionPresentValue:
        """
        Update the option with present value using the Black76 formula, along with supporting metadata

        Args:
            option (schemas.FinancialOptionPresentValue): Option for which we need to calculate the present value
            interest_rate (float): The annualized risk-free interest rate.
            volatility (float): The implied volatility of the underlying asset.
            spot_price (float): The current market price of the underlying asset.

        Returns:
            option (schemas.FinancialOptionPresentValue): The updated option with value for PV.
        """
        pv_calculation_inputs = {
            "expiration_date": option.expiration_date,
            "strike_price": option.strike_price,
            "option_type": option.option_type,
            "interest_rate": interest_rate,
            "volatility": volatility,
            "spot_price": spot_price,
        }
        present_value = PVService.calculate_pv(pv_calculation_inputs)
        option.volatility = volatility
        option.interest_rate = interest_rate
        option.spot_price = spot_price
        option.pv = present_value
        return option

    @classmethod
    def generate_pv_for_options(
        cls,
        options_list: List[models.FinancialOption],
        interest_rate: float,
        volatility: float,
        spot_price: float,
    ):
        """Generate present values for a list of options"""
        options_with_pv: List[schemas.FinancialOptionPresentValue] = []
        serialised_options_list = [
            schemas.FinancialOptionPresentValue.from_orm(option)
            for option in options_list
        ]
        for option in serialised_options_list:
            res = PVService.update_pv_for_single_option(
                option, interest_rate, volatility, spot_price
            )
            options_with_pv.append(res)
        return options_with_pv
