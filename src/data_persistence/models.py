# pylint: disable=missing-function-docstring,no-self-argument
"""SQLALchemy model to represent table in the Database"""
import calendar
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import validates
from .database import Base


class FinancialOption(Base):
    """To Persist Options data in the DB"""

    __tablename__ = "financial_options"
    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String)
    expires_on = Column(String)
    strike_price = Column(Float)
    option_type = Column(String)
    unit_of_measure = Column(String)
    _expiration_date = Column("expiration_date", Date, nullable=False)

    @property
    def expiration_date(self):
        return self._expiration_date

    @staticmethod
    def get_month_and_year(date_str: str) -> tuple:
        months = {
            "Jan": 1,
            "Feb": 2,
            "Mar": 3,
            "Apr": 4,
            "May": 5,
            "Jun": 6,
            "Jul": 7,
            "Aug": 8,
            "Sep": 9,
            "Oct": 10,
            "Nov": 11,
            "Dec": 12,
        }
        month_str = date_str[:3]
        year_str = "20" + date_str[-2:]
        month = months[month_str.capitalize()]
        year = int(year_str)
        return month, year

    @staticmethod
    def get_last_day_of_month(year: int, month: int) -> int:
        return calendar.monthrange(year, month)[1]

    @validates("expires_on")
    def get_last_business_day(self, _, value):
        month_int, year_int = FinancialOption.get_month_and_year(value)
        if self.commodity == "BRN":
            month_int -= 2
            if month_int < 1:
                year_int -= 1
                month_int += 12
        elif self.commodity == "HH":
            month_int -= 1
            if month_int < 1:
                year_int -= 1
                month_int += 12
        else:
            raise ValueError("Invalid commodity.")
        last_day_of_month = FinancialOption.get_last_day_of_month(year_int, month_int)
        last_day = datetime(year_int, month_int, last_day_of_month)
        while last_day.weekday() >= 5:
            last_day -= timedelta(days=1)

        if last_day <= datetime.now():
            raise ValueError("Expiry date should be earlier than today.")
        self._expiration_date = last_day
        return value
