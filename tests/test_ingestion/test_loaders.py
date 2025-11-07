# Alpha Vantage


# Massive


# yfinance

import pytest

from fxpipeline.ingestion.loaders import get_loader


def test_get_loader():
    assert get_loader("alpha_vantage").__class__.__name__ == "AlphaVantageForex"
    assert get_loader("massive").__class__.__name__ == "MassiveForex"
    assert get_loader("yfinance").__class__.__name__ == "YFinanceForex"


def test_get_loader_value_error():
    with pytest.raises(TypeError):
        l = get_loader()  # must require 1 argument

    with pytest.raises(ValueError):
        l = get_loader("Alpha_vantage")  # wrong spelling, must be case-insensitive


# Mock API
def test_alpha_vantage():
    pass


def test_massive():
    pass


def test_yfinance():
    pass
