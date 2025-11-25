from enum import StrEnum


class InterestCalculationType(StrEnum):
    FLAT = "Flat Rate"
    AMORTIZATION = "Amortization"
    TERM = "Loan Term"
    REDUCING = "Reducing Balance"
    EQUAL_PAYMENT = "Reducing Balance (Equal Repayment)"
    STRAIGHT_LINE = "Straight Line"


class InterestTerm(StrEnum):
    PER_ANNUM = "Per Annum"
    PER_MONTH = "Per Month"


class PaymentType(StrEnum):
    DEFAULT = "Default"
    CUSTOM = "Custom"
