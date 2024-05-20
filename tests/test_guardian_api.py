from src.guardian_api import get_guardian_content, filter_response
import pytest
import json
from dotenv import load_dotenv
import os

load_dotenv()


class TestFormattedResponse:
    @pytest.fixture
    def response_1(self):
        return json.load(open(
            './tests/data/api_content_1/raw_response.json'))

    @pytest.fixture
    def results_1(self):
        return json.load(open(
            './tests/data/api_content_1/formatted_results.json'))

    def test_null_argument_returns_empty_array(self):
        assert filter_response(None) == []

    def test_returns_only_revelent_fields(self, response_1):
        expected_fields = ['webPublicationDate', 'webTitle', 'webUrl']
        output = filter_response(response_1)
        for result in output:
            assert sorted(list(result.keys())) == expected_fields

    def test_returns_correct_values_for_keys(self, response_1, results_1):
        output = filter_response(response_1)
        assert output == results_1['results']


if __name__ == '__main__':
    api_key = os.getenv('GUARDIAN_KEY')
    print(api_key)
    search_term = 'coronavirus'
    date_from = '2020-01-01'
    content = get_guardian_content(api_key, search_term, date_from)
    print(content)
