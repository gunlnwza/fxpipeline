# test_my_module.py
from unittest.mock import patch, MagicMock
from my_module import fetch_data

@patch("my_module.requests.get")
def test_fetch_data(mock_get):
    # create mock response object
    mock_response = MagicMock()
    mock_response.json.return_value = {"key": "value"}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result = fetch_data()

    mock_get.assert_called_once_with("https://api.example.com/data")
    assert result == {"key": "value"}