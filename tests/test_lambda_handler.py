import logging
from src.lambda_handler import lambda_handler

logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
logger.propagate = True


class TestInputValidation:

    def test_logs_error_for_empty_search_term(self, caplog):
        event_1 = {
            'date_from': '2022-01-01',
            'search_term': '',
            'stream_id': 'test_stream'
        }
        event_2 = {
            'date_from': '2022-01-01',
            'search_term': '   ',
            'stream_id': 'test_stream'
            }
        with caplog.at_level(logging.INFO):
            lambda_handler(event_1, None)
            expected = "Empty input parameter (search_term)."
            assert expected in caplog.text
        with caplog.at_level(logging.INFO):
            lambda_handler(event_2, None)
            expected = "Invalid input parameter (search_term)."
            assert expected in caplog.text

    def test_logs_error_for_empty_stream_id(self, caplog):
        event_1 = {
            'date_from': '2022-01-01',
            'search_term': 'test_term',
            'stream_id': ''
        }
        event_2 = {
            'date_from': '2022-01-01',
            'search_term': 'test_term',
            'stream_id': '    '
            }
        with caplog.at_level(logging.INFO):
            lambda_handler(event_1, None)
            expected = 'Empty input parameter (stream_id).'
            assert expected in caplog.text
        with caplog.at_level(logging.INFO):
            lambda_handler(event_2, None)
            expected = 'Invalid input parameter (stream_id).'
            assert expected in caplog.text

    def test_logs_error_for_non_string_input_parameter(self, caplog):
        params = ['date_from', 'search_term', 'stream_id']
        for param in params:
            event = {
                'date_from': '2022-01-01',
                'search_term': 'test_term',
                'stream_id': 'test_stream'
            }
            event[param] = 123
            with caplog.at_level(logging.INFO):
                lambda_handler(event, None)
                expected = f'Invalid input parameter type ({param}).'
                assert expected in caplog.text
