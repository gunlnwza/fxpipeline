# Alpha Vantage


# Massive


# yfinance

import pytest

from fxpipeline.ingestion.loaders import get_loader


def test_normal():
    assert get_loader("alpha_vantage").__class__.__name__ == "AlphaVantageForex"
    assert get_loader("massive").__class__.__name__ == "Massive"
    assert get_loader("yfinance").__class__.__name__ == "YFinance"


def test_value_error():
    with pytest.raises(ValueError):
        l = get_loader()  # must have input

    with pytest.raises(ValueError):
        l = get_loader("Alpha_vantage")  # wrong spelling, must be case-insensitive
