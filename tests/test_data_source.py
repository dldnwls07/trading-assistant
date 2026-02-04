# tests/test_data_source.py
import unittest
from unittest.mock import patch

import pandas as pd

from trading_assist.data_source import get_economic_calendar


class TestDataSources(unittest.TestCase):

    @patch("trading_assist.data_source.te")
    def test_get_economic_calendar_success(self, mock_te):
        """
        Tests successful fetching of economic calendar data.
        """
        # Arrange
        sample_data = {
            "Date": ["2024-01-01 10:00:00"],
            "Country": ["United States"],
            "Event": ["CPI MoM"],
            "Actual": ["0.3%"],
            "Previous": ["0.2%"],
            "Consensus": ["0.3%"],
            "Forecast": ["0.3%"],
        }
        mock_df = pd.DataFrame(sample_data)
        mock_te.getCalendarData.return_value = mock_df

        # Act
        result_df = get_economic_calendar(country="United States")

        # Assert
        self.assertIsNotNone(result_df)
        self.assertTrue(isinstance(result_df, pd.DataFrame))
        self.assertFalse(result_df.empty)
        pd.testing.assert_frame_equal(result_df, mock_df)
        mock_te.login.assert_called_with("guest:guest")
        mock_te.getCalendarData.assert_called_with(
            country="United States", output_type="df"
        )

    @patch("trading_assist.data_source.te")
    def test_get_economic_calendar_api_error(self, mock_te):
        """
        Tests handling of an exception during API call.
        """
        # Arrange
        mock_te.getCalendarData.side_effect = Exception("API connection failed")

        # Act
        result = get_economic_calendar(country="United States")

        # Assert
        self.assertIsNone(result)
        mock_te.login.assert_called_with("guest:guest")
        mock_te.getCalendarData.assert_called_with(
            country="United States", output_type="df"
        )

    @patch("trading_assist.data_source.te")
    def test_get_economic_calendar_no_data(self, mock_te):
        """
        Tests handling of an empty DataFrame response from the API.
        """
        # Arrange
        mock_te.getCalendarData.return_value = pd.DataFrame()  # Empty dataframe

        # Act
        result = get_economic_calendar(country="United States")

        # Assert
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
