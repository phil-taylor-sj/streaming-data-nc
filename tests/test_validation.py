import pytest
import re
from src.validation import (
    check_date_is_valid, check_id_string_is_valid
)


class TestcCheckDateIsValid():

    def test_returns_true_for_valid_date(self):
        '''
        Verify does not raise errors for properly formatted and valid
        date values.

        This test confirms that the function properly validates date strings
        that meet the expected criteria (non-empty and properly formatted).
        The function should return 'True' for all valid cases.

        Valid values Tested:
            - '2024-01-01'
            - '1992-05-05'
            - '0001-01-01'
        '''
        assert check_date_is_valid('2024-01-01')
        assert check_date_is_valid('1992-05-05')
        assert check_date_is_valid('0001-01-01')

    @pytest.mark.parametrize('param', [14, []])
    def test_raises_error_for_none_string_value(self, param):
        '''
        Verify raises TypeError for non-string date values.

        Invalid types Tested:
            - 14 (integer)
            - [] (empty list)
        '''
        with pytest.raises(TypeError) as exec:
            check_date_is_valid(param)
        assert exec.match(re.escape(
            'Parameter (date_from) must be of type string.'
        ))

    @pytest.mark.parametrize('param', [
        'Hello World', '0000-00-00', '2022-DD01-01', ''
    ])
    def test_raises_error_for_invalid_date_format(self, param):
        '''
        Verify raises ValueError for improperly formatted date values.
        
        Invalid values tested:
            - 'Hello World'
            - '0000-00-00'
            - '2022-DD01-01'
        '''
        with pytest.raises(ValueError) as exec:
            check_date_is_valid(param)
        assert exec.match(re.escape(
            'Parameter (date_from) must be formatted as %Y-%m-%d.'
        ))

    def test_raises_error_for_invalid_date_value(self):
        '''
        Verify raises ValueError for invalid dates values.

        This test checks that the function raises a ValueError when provided
        a date which is properly formatted, with valid days and months, but
        occurs after the current date.

        Invalid values tested:
            - '3020-01-01' 
        '''
        with pytest.raises(ValueError) as exec:
            check_date_is_valid('3020-01-01')
        assert exec.match(re.escape(
            'Parameter (date_from) must be before current date.'
        ))

    @pytest.mark.parametrize('param', ['2024-14-01', '2024-01-32'])
    def test_raises_error_for_invalid_month_or_day(self, param):
        '''
        Verify raises ValueError for invalid month or day values.

        This test checks that the function raises a ValueError when provided
        provided a date string which is properly formatted, but contains an
        invalid month or day.
        '''
        with pytest.raises(ValueError) as exec:
            check_date_is_valid(param)
        assert exec.match(re.escape(
            'Parameter (date_from) must be formatted as %Y-%m-%d.'))


class TestCheckIdStringIsValid:

    def test_returns_true_for_valid_id(self):
        '''
        Verify correct ID strings are accepted by
        'check_id_string_is_valid'.

        This test confirms that the function properly validates ID strings
        that meet the expected criteria (non-empty and properly formatted).
        The function should return 'True' for all valid cases.

        Valid IDs Tested:
            - 'Hello World'
            - '  1234-hello' (with leading whitespace)
            - '  1234-world   ' (with leading and trailing whitespace)
        '''
        assert check_id_string_is_valid('Hello World', 'test_id')
        assert check_id_string_is_valid('  1234-hello', 'test_id')
        assert check_id_string_is_valid('  1234-world   ', 'test_id')

    @pytest.mark.parametrize('param', [14, []])
    def test_raises_error_for_invalid_type(self, param):
        '''
        Ensure that non-string ID inputs raise TypeError in `check_id_string_is_valid`.

        This test checks that the function enforces type constraints by raising a TypeError
        when provided with input types other than string, ensuring robust input validation.

        Non-string Inputs Tested:
            - 14 (integer)
            - [] (empty list)

        Expected Exception:
            TypeError with a message specifying that the parameter must be a string.
        '''
        with pytest.raises(TypeError) as exec:
            check_id_string_is_valid(param, 'test_id')
        assert exec.match(re.escape(
            'Parameter (test_id) must be of type string.'
        ))

    def test_raises_error_for_empty_id_string(self):
        '''
        Confirm that empty or whitespace-only strings raise ValueError in `check_id_string_is_valid`.

        This test verifies that the function identifies and rejects empty strings and strings
        composed solely of whitespace as invalid IDs, aiming to prevent data integrity issues.

        Scenarios Tested:
            - '' (empty string)
            - '   ' (whitespace only)

        Expected Exception:
            ValueError with messages explaining that the ID string cannot be empty or only whitespace.
        '''
        with pytest.raises(ValueError) as exec:
            check_id_string_is_valid('', 'test_id')
        assert exec.match(re.escape(
            'Parameter (test_id) cannot be an empty string.'
        ))
        with pytest.raises(ValueError) as exec:
            check_id_string_is_valid('   ', 'test_id')
        assert exec.match(re.escape(
            'Parameter (test_id) cannot contain only whitespace.'
        ))
