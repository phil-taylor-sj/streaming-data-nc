from src.validation import check_date_is_valid
import pytest


class TestcCheckDateIsValid():

    def test_returns_true_for_valid_date(self):
        assert check_date_is_valid('2024-01-01')
        assert check_date_is_valid('1992-05-05')
        assert check_date_is_valid('0001-01-01')

    def test_raises_error_for_none_string_value(self):
        with pytest.raises(TypeError) as exec:
            check_date_is_valid(14)
        assert exec.match('date_from parameter must be of type string.')
        with pytest.raises(TypeError) as exec:
            check_date_is_valid([])
        assert exec.match('date_from parameter must be of type string.')

    def test_raises_error_for_invalid_date_format(self):
        with pytest.raises(ValueError) as exec:
            check_date_is_valid('Hello World')
        assert exec.match('date_from parameter must be formatted as %Y-%m-%d.')
        with pytest.raises(ValueError) as exec:
            check_date_is_valid('0000-00-00')
        assert exec.match('date_from parameter must be formatted as %Y-%m-%d.')
        with pytest.raises(ValueError) as exec:
            check_date_is_valid('')
        assert exec.match('date_from parameter must be formatted as %Y-%m-%d.')

    def test_raises_error_for_invalid_date_value(self):
        with pytest.raises(ValueError) as exec:
            check_date_is_valid('3020-01-01')
        assert exec.match('date_from parameter must be before current date.')
